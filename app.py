"""
Aau Ya Nahi - AI Attendance Risk Predictor
Flask Backend Application & REST API Server
"""
import os
import sys
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

from services.calculator import AttendanceCalculator
from services.ml_service import MLRiskService

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Initialize Services
ml_service = MLRiskService()


def parse_common_inputs(req_data):
    """Safely extracts and validates common attendance input parameters."""
    if not req_data:
        raise ValueError("Request body cannot be empty.")

    try:
        total_conducted = int(req_data.get('total_conducted', 0))
    except (ValueError, TypeError):
        raise ValueError("Total conducted classes must be a valid integer.")

    try:
        classes_attended = int(req_data.get('classes_attended', 0))
    except (ValueError, TypeError):
        raise ValueError("Classes attended must be a valid integer.")

    try:
        required_pct = float(req_data.get('required_pct', 75.0))
    except (ValueError, TypeError):
        raise ValueError("Required percentage must be a valid number.")

    if total_conducted < 0:
        raise ValueError("Total conducted classes cannot be negative.")
    if classes_attended < 0:
        raise ValueError("Classes attended cannot be negative.")
    if classes_attended > total_conducted:
        raise ValueError(f"Attended classes ({classes_attended}) cannot exceed total conducted classes ({total_conducted}).")
    if required_pct <= 0 or required_pct > 100:
        raise ValueError("Required percentage must be between 1% and 100%.")

    return total_conducted, classes_attended, required_pct


@app.route('/')
def index():
    """Serves the primary web application interface."""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health():
    """System health check endpoint."""
    return jsonify({
        "status": "online",
        "service": "Aau Ya Nahi AI Attendance Risk Predictor",
        "version": "2.0.0",
        "ml_model_loaded": ml_service.model is not None
    })


@app.route('/api/predict', methods=['POST'])
def predict_attendance():
    """
    Attendance Predictor endpoint.
    Calculates future attendance scenarios (attending vs missing X upcoming classes).
    """
    try:
        data = request.get_json(force=True)
        total_conducted, classes_attended, required_pct = parse_common_inputs(data)

        try:
            upcoming_classes = int(data.get('upcoming_classes', 5))
        except (ValueError, TypeError):
            raise ValueError("Upcoming classes count must be a valid positive integer.")

        if upcoming_classes < 0:
            raise ValueError("Upcoming classes cannot be negative.")

        result = AttendanceCalculator.predict_future_attendance(
            total_conducted=total_conducted,
            classes_attended=classes_attended,
            upcoming_classes=upcoming_classes
        )
        
        # Add risk classification tags to scenarios
        def get_status(pct):
            if pct >= required_pct:
                return {"level": "safe", "label": "🟢 Safe", "message": f"Safe ({pct}% ≥ {required_pct}%)"}
            elif pct >= required_pct - 5.0:
                return {"level": "warning", "label": "🟡 Warning", "message": f"Borderline Danger ({pct}% is close to {required_pct}%)"}
            else:
                return {"level": "critical", "label": "🔴 Critical", "message": f"Critical Shortage ({pct}% < {required_pct}%)"}

        result['required_pct'] = required_pct
        result['current']['status'] = get_status(result['current']['percentage'])
        result['if_attend_all']['status'] = get_status(result['if_attend_all']['percentage'])
        result['if_miss_all']['status'] = get_status(result['if_miss_all']['percentage'])

        # Contextual summary sentence
        curr_p = result['current']['percentage']
        miss_p = result['if_miss_all']['percentage']
        attend_p = result['if_attend_all']['percentage']

        if miss_p < required_pct and curr_p >= required_pct:
            result['summary_message'] = f"Your attendance will fall from {curr_p}% to {miss_p}% (below required {required_pct}%) if you miss the next {upcoming_classes} classes."
        elif curr_p < required_pct and attend_p >= required_pct:
            result['summary_message'] = f"Attending the next {upcoming_classes} classes will successfully lift your attendance from {curr_p}% to {attend_p}% (above required {required_pct}%)."
        elif curr_p < required_pct and attend_p < required_pct:
            result['summary_message'] = f"Attending the next {upcoming_classes} classes will improve attendance to {attend_p}%, but you will still need more classes to reach {required_pct}%."
        else:
            result['summary_message'] = f"Your attendance will remain safe at {miss_p}% even if you miss the next {upcoming_classes} classes."

        return jsonify({
            "success": True,
            "data": result
        })

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Internal server error: {str(e)}"}), 500


@app.route('/api/aau-ya-nahi', methods=['POST'])
def aau_ya_nahi():
    """
    'Aau Ya Nahi?' Core Calculator endpoint.
    Returns:
    A. 'Kitni Classes Chhod Sakta Hoon?' (Max safe bunk capacity)
    B. 'Kitni Classes Attend Karni Hogi?' (Consecutive classes to recover)
    """
    try:
        data = request.get_json(force=True)
        total_conducted, classes_attended, required_pct = parse_common_inputs(data)

        bunk_calc = AttendanceCalculator.calculate_bunk_capacity(
            total_conducted=total_conducted,
            classes_attended=classes_attended,
            required_pct=required_pct
        )

        recovery_calc = AttendanceCalculator.calculate_recovery_classes(
            total_conducted=total_conducted,
            classes_attended=classes_attended,
            required_pct=required_pct
        )

        return jsonify({
            "success": True,
            "data": {
                "bunk_capacity": bunk_calc,
                "recovery_requirement": recovery_calc,
                "total_conducted": total_conducted,
                "classes_attended": classes_attended,
                "classes_missed": total_conducted - classes_attended,
                "current_percentage": bunk_calc['current_pct'],
                "required_percentage": required_pct
            }
        })

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Internal server error: {str(e)}"}), 500


@app.route('/api/ml-risk', methods=['POST'])
def ml_risk_prediction():
    """
    AI / ML Attendance Risk Prediction Module endpoint.
    Returns Machine Learning classification, class probabilities, factor breakdown, and smart recommendations.
    """
    try:
        data = request.get_json(force=True)
        total_conducted, classes_attended, required_pct = parse_common_inputs(data)

        recent_trend = data.get('recent_trend_pct')
        if recent_trend is not None:
            try:
                recent_trend = float(recent_trend)
            except (ValueError, TypeError):
                recent_trend = None

        upcoming_classes = int(data.get('upcoming_classes', 5))

        prediction = ml_service.predict_risk(
            total_conducted=total_conducted,
            classes_attended=classes_attended,
            recent_trend_pct=recent_trend,
            upcoming_classes=upcoming_classes,
            required_pct=required_pct
        )

        return jsonify({
            "success": True,
            "data": prediction
        })

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Internal server error: {str(e)}"}), 500


@app.route('/api/model-info', methods=['GET'])
def model_info():
    """
    Returns ML Model architecture, evaluation metrics, feature importances, and viva documentation data.
    """
    try:
        info = ml_service.get_model_info()
        return jsonify({
            "success": True,
            "data": info
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/batch-subject-analysis', methods=['POST'])
def batch_subject_analysis():
    """
    Evaluates a collection of college subjects and generates an overall semester attendance report.
    """
    try:
        data = request.get_json(force=True)
        subjects = data.get('subjects', [])
        required_pct = float(data.get('required_pct', 75.0))

        if not subjects or not isinstance(subjects, list):
            raise ValueError("Subjects list cannot be empty.")

        results = []
        total_all_conducted = 0
        total_all_attended = 0

        for subj in subjects:
            name = str(subj.get('name', 'Unnamed Subject')).strip()
            conducted = int(subj.get('total_conducted', 0))
            attended = int(subj.get('classes_attended', 0))
            
            if conducted < 0 or attended < 0 or attended > conducted:
                continue

            total_all_conducted += conducted
            total_all_attended += attended

            pct, missed = AttendanceCalculator.calculate_current_attendance(conducted, attended)
            bunk = AttendanceCalculator.calculate_bunk_capacity(conducted, attended, required_pct)
            recovery = AttendanceCalculator.calculate_recovery_classes(conducted, attended, required_pct)

            # ML prediction for subject
            risk = ml_service.predict_risk(
                total_conducted=conducted,
                classes_attended=attended,
                required_pct=required_pct
            )

            results.append({
                "name": name,
                "total_conducted": conducted,
                "classes_attended": attended,
                "classes_missed": missed,
                "percentage": pct,
                "can_bunk": bunk['can_bunk'],
                "classes_needed": recovery['classes_needed'],
                "risk_level": risk['risk_level'],
                "risk_ui": risk['ui']
            })

        overall_pct, overall_missed = AttendanceCalculator.calculate_current_attendance(
            total_all_conducted, total_all_attended
        )
        overall_bunk = AttendanceCalculator.calculate_bunk_capacity(total_all_conducted, total_all_attended, required_pct)
        overall_recovery = AttendanceCalculator.calculate_recovery_classes(total_all_conducted, total_all_attended, required_pct)
        overall_risk = ml_service.predict_risk(total_all_conducted, total_all_attended, required_pct=required_pct)

        return jsonify({
            "success": True,
            "data": {
                "subjects": results,
                "aggregate": {
                    "total_conducted": total_all_conducted,
                    "classes_attended": total_all_attended,
                    "classes_missed": overall_missed,
                    "percentage": overall_pct,
                    "can_bunk": overall_bunk['can_bunk'],
                    "classes_needed": overall_recovery['classes_needed'],
                    "risk_level": overall_risk['risk_level'],
                    "risk_ui": overall_risk['ui']
                }
            }
        })

    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Internal server error: {str(e)}"}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n=======================================================")
    print("Aau Ya Nahi - AI Attendance Risk Predictor Started!")
    print(f"Serving on http://127.0.0.1:{port}")
    print("=======================================================\n")
    app.run(host='0.0.0.0', port=port, debug=True)
