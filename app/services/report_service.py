import io
import csv
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from app.models.user import User
from app.models.attendance import SubjectAttendance
from app.models.system_setting import SystemSetting
from app.services.attendance_service import AttendanceService

class ReportService:
    @staticmethod
    def generate_student_pdf(student: User) -> io.BytesIO:
        """
        Generates a professional, watermarked PDF report of the student's attendance & medical records.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#0f172a'),
            alignment=1, # Center
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'ReportSubTitle',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#64748b'),
            alignment=1,
            spaceAfter=15
        )
        meta_label_style = ParagraphStyle(
            'MetaLabel',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#475569'),
            fontName='Helvetica-Bold'
        )
        meta_value_style = ParagraphStyle(
            'MetaValue',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#0f172a')
        )
        section_style = ParagraphStyle(
            'SectionHeader',
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#1e293b'),
            fontName='Helvetica-Bold',
            spaceBefore=12,
            spaceAfter=6
        )

        elements = []

        # Header Title
        settings = SystemSetting.get_all_settings()
        elements.append(Paragraph(settings.get('university_name', 'SmartAttend University'), title_style))
        elements.append(Paragraph(f"Official Student Attendance & Medical Assessment Report • {settings.get('semester_name', 'Spring 2026')}", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=12))

        # Student Profile Info Table
        meta_data = [
            [
                Paragraph("Student Name:", meta_label_style), Paragraph(student.full_name, meta_value_style),
                Paragraph("Registration No.:", meta_label_style), Paragraph(student.registration_number or 'N/A', meta_value_style)
            ],
            [
                Paragraph("Program / Course:", meta_label_style), Paragraph(f"{student.course} ({student.branch})", meta_value_style),
                Paragraph("Semester:", meta_label_style), Paragraph(f"Semester {student.semester}", meta_value_style)
            ],
            [
                Paragraph("Student Email:", meta_label_style), Paragraph(student.email, meta_value_style),
                Paragraph("Report Date:", meta_label_style), Paragraph(datetime.now().strftime("%B %d, %Y %I:%M %p"), meta_value_style)
            ]
        ]
        meta_table = Table(meta_data, colWidths=[1.3*inch, 2.3*inch, 1.4*inch, 2.0*inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#edf2f7')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 14))

        # Attendance Metrics Summary
        dash_data = AttendanceService.get_student_dashboard_data(student.id)
        
        stat_data = [
            [
                Paragraph("Total Conducted Classes", meta_label_style),
                Paragraph("Classes Attended", meta_label_style),
                Paragraph("Medical Classes", meta_label_style),
                Paragraph("Regular Attendance", meta_label_style),
                Paragraph("Final Attendance", meta_label_style),
                Paragraph("Eligibility Status", meta_label_style)
            ],
            [
                Paragraph(str(dash_data['total_conducted']), meta_value_style),
                Paragraph(str(dash_data['total_attended']), meta_value_style),
                Paragraph(str(dash_data['total_medical_classes']), meta_value_style),
                Paragraph(f"{dash_data['overall_regular_pct']}%", meta_value_style),
                Paragraph(f"{dash_data['overall_final_pct']}%", meta_value_style),
                Paragraph(dash_data['overall_eligibility']['status'], meta_value_style)
            ]
        ]
        stat_table = Table(stat_data, colWidths=[1.15*inch, 1.15*inch, 1.1*inch, 1.2*inch, 1.1*inch, 1.3*inch])
        stat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#eff6ff')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#bfdbfe')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dbeafe')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(Paragraph("Overall Attendance Summary", section_style))
        elements.append(stat_table)
        elements.append(Spacer(1, 15))

        # Subject-wise Breakdown Table
        elements.append(Paragraph("Subject-wise Attendance & Medical Breakdown", section_style))
        
        header = ["Subject Code", "Subject Name", "Total", "Attended", "Missed", "Regular %", "Medical %", "Final %", "Status"]
        table_rows = [header]

        for s in dash_data['subjects']:
            table_rows.append([
                s['subject_code'],
                s['subject_name'][:24],
                str(s['total_classes']),
                str(s['attended_classes']),
                str(s['missed_classes']),
                f"{s['regular_percentage']}%",
                f"{s['medical_percentage']}%",
                f"{s['final_percentage']}%",
                s['eligibility']['status']
            ])

        sub_table = Table(table_rows, colWidths=[0.85*inch, 1.8*inch, 0.55*inch, 0.65*inch, 0.55*inch, 0.75*inch, 0.75*inch, 0.65*inch, 0.75*inch])
        sub_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(sub_table)
        elements.append(Spacer(1, 20))

        # Footer notes & Signatures
        formula_name = dash_data['formula_info']['mode'].replace('_', ' ').title()
        notice_text = f"Notice: Attendance calculated in accordance with institutional policy ({formula_name} formula, min threshold {dash_data['formula_info']['threshold']}%). Medical benefits are officially certified."
        elements.append(Paragraph(notice_text, ParagraphStyle('Notice', fontSize=8, textColor=colors.HexColor('#64748b'), spaceAfter=25)))

        sig_data = [
            [Paragraph("____________________________<br/>Student Signature", meta_value_style),
             Paragraph("____________________________<br/>Faculty Advisor / Dean", meta_value_style),
             Paragraph("____________________________<br/>Office of the Registrar", meta_value_style)]
        ]
        sig_table = Table(sig_data, colWidths=[2.3*inch, 2.3*inch, 2.3*inch])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(sig_table)

        doc.build(elements)
        buffer.seek(0)
        return buffer

    @staticmethod
    def generate_admin_attendance_csv() -> io.StringIO:
        """
        Exports comprehensive university-wide student attendance in CSV format.
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Student ID', 'Registration Number', 'Full Name', 'Email', 'Course', 'Branch', 'Semester',
            'Subject Code', 'Subject Name', 'Total Classes', 'Attended Classes', 'Missed Classes',
            'Medical Classes', 'Regular %', 'Medical %', 'Final %', 'Eligibility Status'
        ])

        settings = SystemSetting.get_all_settings()
        records = SubjectAttendance.query.join(User).filter(User.role == 'student').order_by(User.registration_number).all()

        for r in records:
            student = r.student
            sub = r.subject
            sub_dict = r.to_dict(
                formula_mode=settings.get('medical_formula_mode', 'standard_addition'),
                max_benefit=settings.get('max_medical_benefit_percent', 15.0),
                weight=settings.get('medical_weight', 1.0),
                threshold=settings.get('required_attendance_threshold', 75.0),
                warning_threshold=settings.get('warning_attendance_threshold', 65.0)
            )
            writer.writerow([
                student.id,
                student.registration_number or 'N/A',
                student.full_name,
                student.email,
                student.course,
                student.branch,
                student.semester,
                sub.code if sub else '',
                sub.name if sub else '',
                r.total_classes,
                r.attended_classes,
                r.missed_classes,
                r.medical_classes,
                sub_dict['regular_percentage'],
                sub_dict['medical_percentage'],
                sub_dict['final_percentage'],
                sub_dict['eligibility']['status']
            ])

        output.seek(0)
        return output
