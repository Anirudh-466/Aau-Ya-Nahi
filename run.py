import os
from app import create_app, db
from app.models import User, Subject, SubjectAttendance, AttendanceRecord, MedicalApplication, SystemSetting, AuditLog

app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.cli.command("init-db")
def init_db():
    """Initializes database schema."""
    with app.app_context():
        db.create_all()
        print("Database schema created successfully.")

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Subject': Subject,
        'SubjectAttendance': SubjectAttendance,
        'AttendanceRecord': AttendanceRecord,
        'MedicalApplication': MedicalApplication,
        'SystemSetting': SystemSetting,
        'AuditLog': AuditLog
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    # Ensure database tables exist on startup
    with app.app_context():
        db.create_all()
    print(f"SmartAttend server starting on http://127.0.0.1:{port}")
    app.run(host='127.0.0.1', port=port, debug=True)
