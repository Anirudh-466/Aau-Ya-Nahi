import math
from app.models.attendance import SubjectAttendance
from app.models.medical import MedicalApplication
from app.models.system_setting import SystemSetting

class AttendanceService:
    @staticmethod
    def get_student_dashboard_data(student_id: int) -> dict:
        """
        Gathers comprehensive attendance and medical data for the student dashboard.
        Includes side-by-side data structures, metrics, warnings, and charts.
        """
        settings = SystemSetting.get_all_settings()
        formula_mode = settings.get('medical_formula_mode', 'standard_addition')
        max_benefit = settings.get('max_medical_benefit_percent', 15.0)
        weight = settings.get('medical_weight', 1.0)
        req_threshold = settings.get('required_attendance_threshold', 75.0)
        warn_threshold = settings.get('warning_attendance_threshold', 65.0)

        records = SubjectAttendance.query.filter_by(student_id=student_id).all()
        
        total_conducted = 0
        total_attended = 0
        total_medical_classes = 0
        
        subject_list = []
        medical_breakdown = []
        warnings = []
        safe_count = 0
        warning_count = 0
        shortage_count = 0

        for r in records:
            total_conducted += r.total_classes
            total_attended += r.attended_classes
            total_medical_classes += r.medical_classes
            
            sub_dict = r.to_dict(
                formula_mode=formula_mode,
                max_benefit=max_benefit,
                weight=weight,
                threshold=req_threshold,
                warning_threshold=warn_threshold
            )
            subject_list.append(sub_dict)

            # Dedicated per-subject medical attendance entry
            med_entry = {
                'subject_id': r.subject_id,
                'subject_name': r.subject.name if r.subject else 'Subject',
                'subject_code': r.subject.code if r.subject else 'SUB',
                'medical_classes': r.medical_classes,
                'medical_percentage': r.medical_percentage,
                'total_classes': r.total_classes
            }
            medical_breakdown.append(med_entry)

            # Status counters
            status = sub_dict['eligibility']['status']
            if status == 'Safe':
                safe_count += 1
            elif status == 'Warning':
                warning_count += 1
                warnings.append({
                    'subject': r.subject.name,
                    'code': r.subject.code,
                    'percentage': sub_dict['final_percentage'],
                    'severity': 'warning',
                    'message': f"Attendance is at {sub_dict['final_percentage']}%. Attend upcoming classes to remain above {req_threshold}%."
                })
            else:
                shortage_count += 1
                needed = AttendanceService.calculate_required_classes(
                    r.total_classes, r.attended_classes, r.medical_classes, req_threshold, formula_mode, max_benefit, weight
                )
                warnings.append({
                    'subject': r.subject.name,
                    'code': r.subject.code,
                    'percentage': sub_dict['final_percentage'],
                    'severity': 'danger',
                    'message': f"Shortage alert! Current attendance is {sub_dict['final_percentage']}%. Must attend next {needed} classes to reach {req_threshold}%."
                })

        # Overall calculations
        overall_regular_pct = round((total_attended / total_conducted * 100), 2) if total_conducted > 0 else 100.0
        overall_medical_pct = round((total_medical_classes / total_conducted * 100), 2) if total_conducted > 0 else 0.0
        
        # Calculate overall final percentage using configured formula
        if total_conducted <= 0:
            overall_final_pct = 100.0
        elif formula_mode == 'exemption_subtraction':
            eff_total = max(1, total_conducted - total_medical_classes)
            overall_final_pct = round(min(100.0, (total_attended / eff_total) * 100), 2)
        elif formula_mode == 'capped_benefit':
            overall_final_pct = round(min(100.0, overall_regular_pct + min(overall_medical_pct, max_benefit)), 2)
        elif formula_mode == 'weighted_benefit':
            eff_att = total_attended + (total_medical_classes * weight)
            overall_final_pct = round(min(100.0, (eff_att / total_conducted) * 100), 2)
        else:
            overall_final_pct = round(min(100.0, ((total_attended + total_medical_classes) / total_conducted) * 100), 2)

        # Overall eligibility
        if overall_final_pct >= req_threshold:
            overall_eligibility = {'status': 'Safe', 'badge_class': 'badge-safe', 'color': '#10b981', 'label': 'Eligible for Exams'}
        elif overall_final_pct >= warn_threshold:
            overall_eligibility = {'status': 'Warning', 'badge_class': 'badge-warning', 'color': '#f59e0b', 'label': 'Conditionally Eligible (Warning)'}
        else:
            overall_eligibility = {'status': 'Shortage', 'badge_class': 'badge-danger', 'color': '#ef4444', 'label': 'Not Eligible (Attendance Shortage)'}

        # Medical applications statistics
        med_apps = MedicalApplication.query.filter_by(student_id=student_id).all()
        pending_apps_count = sum(1 for a in med_apps if a.status == 'Pending')
        approved_apps_count = sum(1 for a in med_apps if a.status == 'Approved')
        rejected_apps_count = sum(1 for a in med_apps if a.status == 'Rejected')
        
        # Total medically approved days
        total_approved_days = sum(a.duration_days for a in med_apps if a.status == 'Approved')

        return {
            'total_subjects': len(records),
            'total_conducted': total_conducted,
            'total_attended': total_attended,
            'total_missed': max(0, total_conducted - total_attended),
            'total_medical_classes': total_medical_classes,
            'overall_regular_pct': overall_regular_pct,
            'overall_medical_pct': overall_medical_pct,
            'overall_final_pct': overall_final_pct,
            'overall_eligibility': overall_eligibility,
            'subjects': subject_list,
            'medical_breakdown': medical_breakdown,
            'total_approved_days': total_approved_days,
            'pending_apps_count': pending_apps_count,
            'approved_apps_count': approved_apps_count,
            'rejected_apps_count': rejected_apps_count,
            'safe_count': safe_count,
            'warning_count': warning_count,
            'shortage_count': shortage_count,
            'warnings': warnings,
            'formula_info': {
                'mode': formula_mode,
                'threshold': req_threshold,
                'warning_threshold': warn_threshold,
                'max_benefit': max_benefit
            }
        }

    @staticmethod
    def calculate_required_classes(total: int, attended: int, medical: int, target_pct: float = 75.0, formula_mode='standard_addition', max_benefit=15.0, weight=1.0) -> int:
        """
        Calculates how many consecutive future classes must be attended to reach target_pct.
        """
        p = target_pct / 100.0
        if p >= 1.0:
            return 999  # Mathematically unreachable if any class missed

        if formula_mode == 'exemption_subtraction':
            # Attended + x / (Total - Medical + x) >= p
            eff_total = max(0, total - medical)
            if eff_total > 0 and (attended / eff_total) >= p:
                return 0
            numerator = (p * eff_total) - attended
            denominator = 1.0 - p
            return max(0, math.ceil(numerator / denominator))
        else:
            # (Attended + Medical + x) / (Total + x) >= p
            eff_attended = attended + medical
            if total > 0 and (eff_attended / total) >= p:
                return 0
            numerator = (p * total) - eff_attended
            denominator = 1.0 - p
            return max(0, math.ceil(numerator / denominator))

    @staticmethod
    def calculate_max_bunks(total: int, attended: int, medical: int, target_pct: float = 75.0, formula_mode='standard_addition', max_benefit=15.0, weight=1.0) -> int:
        """
        Calculates how many classes student can miss consecutively without dropping below target_pct.
        """
        p = target_pct / 100.0
        if p <= 0:
            return 999

        if formula_mode == 'exemption_subtraction':
            eff_total = max(1, total - medical)
            if (attended / eff_total) < p:
                return 0
            # attended / (eff_total + y) >= p => eff_total + y <= attended / p => y <= (attended / p) - eff_total
            return max(0, math.floor((attended / p) - eff_total))
        else:
            eff_attended = attended + medical
            if total <= 0:
                return 0
            if (eff_attended / total) < p:
                return 0
            # eff_attended / (total + y) >= p => y <= (eff_attended / p) - total
            return max(0, math.floor((eff_attended / p) - total))

    @staticmethod
    def run_smart_calculator(total: int, attended: int, medical: int, upcoming: int = 0, target_pct: float = 75.0) -> dict:
        """
        Full dynamic calculation logic consumed by the interactive UI and API.
        """
        settings = SystemSetting.get_all_settings()
        formula_mode = settings.get('medical_formula_mode', 'standard_addition')
        max_benefit = settings.get('max_medical_benefit_percent', 15.0)
        weight = settings.get('medical_weight', 1.0)
        threshold = target_pct or settings.get('required_attendance_threshold', 75.0)

        # Baseline stats
        reg_pct = round((attended / total * 100), 2) if total > 0 else 100.0
        med_pct = round((medical / total * 100), 2) if total > 0 else 0.0

        if total <= 0:
            adjusted_pct = 100.0
        elif formula_mode == 'exemption_subtraction':
            eff_total = max(1, total - medical)
            adjusted_pct = round(min(100.0, (attended / eff_total) * 100), 2)
        elif formula_mode == 'capped_benefit':
            adjusted_pct = round(min(100.0, reg_pct + min(med_pct, max_benefit)), 2)
        elif formula_mode == 'weighted_benefit':
            eff_att = attended + (medical * weight)
            adjusted_pct = round(min(100.0, (eff_att / total) * 100), 2)
        else:
            adjusted_pct = round(min(100.0, ((attended + medical) / total) * 100), 2)

        # Recovery classes
        needed_for_target = AttendanceService.calculate_required_classes(
            total, attended, medical, threshold, formula_mode, max_benefit, weight
        )
        
        # Max bunks allowed
        max_bunks = AttendanceService.calculate_max_bunks(
            total, attended, medical, threshold, formula_mode, max_benefit, weight
        )

        # Projection after upcoming classes
        projected_total = total + upcoming
        projected_attended = attended + upcoming
        if projected_total <= 0:
            projected_pct = 100.0
        elif formula_mode == 'exemption_subtraction':
            eff_proj_tot = max(1, projected_total - medical)
            projected_pct = round(min(100.0, (projected_attended / eff_proj_tot) * 100), 2)
        else:
            projected_pct = round(min(100.0, ((projected_attended + medical) / projected_total) * 100), 2)

        return {
            'total_conducted': total,
            'attended': attended,
            'medical_approved': medical,
            'upcoming': upcoming,
            'regular_pct': reg_pct,
            'medical_pct': med_pct,
            'adjusted_pct': adjusted_pct,
            'target_threshold': threshold,
            'required_classes_to_reach_target': needed_for_target,
            'max_allowed_bunks': max_bunks,
            'projected_pct': projected_pct,
            'is_currently_safe': adjusted_pct >= threshold,
            'status_label': 'Safe' if adjusted_pct >= threshold else ('Warning' if adjusted_pct >= 65 else 'Shortage')
        }
