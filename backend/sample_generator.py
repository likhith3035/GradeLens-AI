import os
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "sample_memos"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_sample_memos():
    print("Generating synthetic marks memos for automated testing...")
    styles = getSampleStyleSheet()

    # Custom paragraph styles
    title_style = ParagraphStyle(
        'UnivTitle',
        parent=styles['Heading1'],
        fontSize=15,
        leading=18,
        alignment=1, # Center
        textColor=colors.HexColor("#1E3A8A"),
        fontName="Helvetica-Bold"
    )

    sub_title_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        alignment=1,
        textColor=colors.HexColor("#374151")
    )

    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1F2937")
    )

    val_style = ParagraphStyle(
        'Value',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        fontName="Helvetica",
        textColor=colors.HexColor("#111827")
    )

    cell_style = ParagraphStyle(
        'Cell',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        alignment=1,
        fontName="Helvetica"
    )

    # 1. JNTU Style Passed Memo
    pdf_path_1 = OUTPUT_DIR / "memo_1_jntu_passed.pdf"
    doc1 = SimpleDocTemplate(str(pdf_path_1), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story1 = []

    story1.append(Paragraph("JAWAHARLAL NEHRU TECHNOLOGICAL UNIVERSITY HYDERABAD", title_style))
    story1.append(Paragraph("Kukatpally, Hyderabad - 500 085, Telangana (India)", sub_title_style))
    story1.append(Paragraph("<b>GRADE CARD / MARKS MEMORANDUM</b>", ParagraphStyle('GC', parent=sub_title_style, fontSize=11, fontName="Helvetica-Bold")))
    story1.append(Spacer(1, 10))

    info_data1 = [
        [Paragraph("<b>H.T. No:</b>", label_style), Paragraph("20671A0512", val_style),
         Paragraph("<b>Course:</b>", label_style), Paragraph("B.TECH", val_style)],
        [Paragraph("<b>Name:</b>", label_style), Paragraph("K. RAHUL REDDY", val_style),
         Paragraph("<b>Branch:</b>", label_style), Paragraph("COMPUTER SCIENCE AND ENGINEERING", val_style)],
        [Paragraph("<b>College:</b>", label_style), Paragraph("J.B. INSTITUTE OF ENGINEERING & TECHNOLOGY (AUTONOMOUS)", val_style),
         Paragraph("<b>Regulation:</b>", label_style), Paragraph("R18", val_style)],
        [Paragraph("<b>Semester:</b>", label_style), Paragraph("III Year II Semester (III-II)", val_style),
         Paragraph("<b>Month & Year:</b>", label_style), Paragraph("JULY 2024", val_style)],
    ]
    t_info1 = Table(info_data1, colWidths=[1.1*inch, 2.5*inch, 1.1*inch, 2.5*inch])
    t_info1.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story1.append(t_info1)
    story1.append(Spacer(1, 12))

    subjects_data1 = [
        ["Sub Code", "Subject Name", "Int", "Ext", "Tot", "Max", "Grade", "Credits", "Result"],
        ["18CS601", "COMPILER DESIGN", "26", "48", "74", "100", "A", "3.0", "P"],
        ["18CS602", "WEB TECHNOLOGIES", "28", "56", "84", "100", "A+", "3.0", "P"],
        ["18CS603", "CRYPTOGRAPHY & NETWORK SECURITY", "25", "46", "71", "100", "A", "3.0", "P"],
        ["18CS604", "MACHINE LEARNING", "29", "62", "91", "100", "O", "4.0", "P"],
        ["18CS605", "CLOUD COMPUTING", "24", "44", "68", "100", "B+", "3.0", "P"],
        ["18CS606", "COMPILER DESIGN LAB", "23", "45", "68", "75", "O", "1.5", "P"],
        ["18CS607", "WEB TECHNOLOGIES LAB", "24", "48", "72", "75", "O", "1.5", "P"],
        ["18CS608", "ADVANCED ENGLISH COMMUNICATION", "22", "42", "64", "75", "A+", "1.0", "P"]
    ]
    t_sub1 = Table(subjects_data1, colWidths=[0.8*inch, 2.6*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.6*inch, 0.6*inch, 0.6*inch])
    t_sub1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#9CA3AF")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F9FAFB")]),
    ]))
    story1.append(t_sub1)
    story1.append(Spacer(1, 14))

    summary_data1 = [
        ["Total Credits: 20.0", "SGPA: 8.75", "CGPA: 8.65", "Result: PASSED"]
    ]
    t_sum1 = Table(summary_data1, colWidths=[1.8*inch, 1.8*inch, 1.8*inch, 1.8*inch])
    t_sum1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#1E3A8A")),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#BFDBFE")),
    ]))
    story1.append(t_sum1)
    doc1.build(story1)

    # 2. JNTU Style Memo with 1 Backlog
    pdf_path_2 = OUTPUT_DIR / "memo_2_jntu_backlog.pdf"
    doc2 = SimpleDocTemplate(str(pdf_path_2), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story2 = []

    story2.append(Paragraph("JAWAHARLAL NEHRU TECHNOLOGICAL UNIVERSITY HYDERABAD", title_style))
    story2.append(Paragraph("Kukatpally, Hyderabad - 500 085, Telangana (India)", sub_title_style))
    story2.append(Paragraph("<b>GRADE CARD / MARKS MEMORANDUM</b>", ParagraphStyle('GC2', parent=sub_title_style, fontSize=11, fontName="Helvetica-Bold")))
    story2.append(Spacer(1, 10))

    info_data2 = [
        [Paragraph("<b>H.T. No:</b>", label_style), Paragraph("20671A0545", val_style),
         Paragraph("<b>Course:</b>", label_style), Paragraph("B.TECH", val_style)],
        [Paragraph("<b>Name:</b>", label_style), Paragraph("P. PRIYA SHARMA", val_style),
         Paragraph("<b>Branch:</b>", label_style), Paragraph("COMPUTER SCIENCE AND ENGINEERING", val_style)],
        [Paragraph("<b>College:</b>", label_style), Paragraph("J.B. INSTITUTE OF ENGINEERING & TECHNOLOGY (AUTONOMOUS)", val_style),
         Paragraph("<b>Regulation:</b>", label_style), Paragraph("R18", val_style)],
        [Paragraph("<b>Semester:</b>", label_style), Paragraph("III Year II Semester (III-II)", val_style),
         Paragraph("<b>Month & Year:</b>", label_style), Paragraph("JULY 2024", val_style)],
    ]
    t_info2 = Table(info_data2, colWidths=[1.1*inch, 2.5*inch, 1.1*inch, 2.5*inch])
    story2.append(t_info2)
    story2.append(Spacer(1, 12))

    subjects_data2 = [
        ["Sub Code", "Subject Name", "Int", "Ext", "Tot", "Max", "Grade", "Credits", "Result"],
        ["18CS601", "COMPILER DESIGN", "15", "18", "33", "100", "F", "0.0", "F"],  # Failed subject!
        ["18CS602", "WEB TECHNOLOGIES", "26", "48", "74", "100", "A", "3.0", "P"],
        ["18CS603", "CRYPTOGRAPHY & NETWORK SECURITY", "24", "45", "69", "100", "B+", "3.0", "P"],
        ["18CS604", "MACHINE LEARNING", "25", "45", "70", "100", "A", "4.0", "P"],
        ["18CS605", "CLOUD COMPUTING", "22", "40", "62", "100", "B", "3.0", "P"],
        ["18CS606", "COMPILER DESIGN LAB", "22", "42", "64", "75", "A+", "1.5", "P"],
        ["18CS607", "WEB TECHNOLOGIES LAB", "23", "45", "68", "75", "O", "1.5", "P"],
        ["18CS608", "ADVANCED ENGLISH COMMUNICATION", "20", "38", "58", "75", "A", "1.0", "P"]
    ]
    t_sub2 = Table(subjects_data2, colWidths=[0.8*inch, 2.6*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.5*inch, 0.6*inch, 0.6*inch, 0.6*inch])
    t_sub2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#9CA3AF")),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#FEE2E2")), # Highlight failure row
        ('ROWBACKGROUNDS', (0,2), (-1,-1), [colors.white, colors.HexColor("#F9FAFB")]),
    ]))
    story2.append(t_sub2)
    story2.append(Spacer(1, 14))

    summary_data2 = [
        ["Total Credits: 17.0", "SGPA: 6.45", "CGPA: 7.12", "Result: FAILED"]
    ]
    t_sum2 = Table(summary_data2, colWidths=[1.8*inch, 1.8*inch, 1.8*inch, 1.8*inch])
    t_sum2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEF2F2")),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#991B1B")),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#FECACA")),
    ]))
    story2.append(t_sum2)
    doc2.build(story2)

    # 3. Anna University Style Memo
    pdf_path_3 = OUTPUT_DIR / "memo_3_anna_univ.pdf"
    doc3 = SimpleDocTemplate(str(pdf_path_3), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story3 = []

    story3.append(Paragraph("ANNA UNIVERSITY :: CHENNAI - 600 025", title_style))
    story3.append(Paragraph("OFFICE OF THE CONTROLLER OF EXAMINATIONS", sub_title_style))
    story3.append(Paragraph("<b>GRADE SHEET — B.E. DEGREE EXAMINATIONS</b>", ParagraphStyle('GC3', parent=sub_title_style, fontSize=11, fontName="Helvetica-Bold")))
    story3.append(Spacer(1, 10))

    info_data3 = [
        [Paragraph("<b>Register No:</b>", label_style), Paragraph("312218104001", val_style),
         Paragraph("<b>Degree:</b>", label_style), Paragraph("B.E.", val_style)],
        [Paragraph("<b>Student Name:</b>", label_style), Paragraph("S. KARTHIK", val_style),
         Paragraph("<b>Branch:</b>", label_style), Paragraph("ELECTRONICS & COMMUNICATION ENGINEERING", val_style)],
        [Paragraph("<b>College:</b>", label_style), Paragraph("UNIVERSITY DEPARTMENTS OF ANNA UNIVERSITY", val_style),
         Paragraph("<b>Regulation:</b>", label_style), Paragraph("2017", val_style)],
        [Paragraph("<b>Semester:</b>", label_style), Paragraph("Semester 06", val_style),
         Paragraph("<b>Month & Year:</b>", label_style), Paragraph("APRIL 2022", val_style)],
    ]
    t_info3 = Table(info_data3, colWidths=[1.1*inch, 2.5*inch, 1.1*inch, 2.5*inch])
    story3.append(t_info3)
    story3.append(Spacer(1, 12))

    subjects_data3 = [
        ["Course Code", "Course Title", "Grade", "Credits", "Result"],
        ["EC8691", "MICROPROCESSORS AND MICROCONTROLLERS", "A+", "3.0", "PASS"],
        ["EC8095", "VLSI DESIGN", "O", "3.0", "PASS"],
        ["EC8652", "WIRELESS COMMUNICATION", "A", "3.0", "PASS"],
        ["MG8591", "PRINCIPLES OF MANAGEMENT", "A+", "3.0", "PASS"],
        ["EC8651", "TRANSMISSION LINES AND RF SYSTEMS", "B+", "3.0", "PASS"],
        ["EC8681", "MICROPROCESSORS & MICROCONTROLLERS LAB", "O", "2.0", "PASS"],
        ["EC8611", "VLSI DESIGN LABORATORY", "O", "2.0", "PASS"],
    ]
    t_sub3 = Table(subjects_data3, colWidths=[1.2*inch, 3.4*inch, 0.8*inch, 0.8*inch, 1.0*inch])
    t_sub3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F766E")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#9CA3AF")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F0FDFA")]),
    ]))
    story3.append(t_sub3)
    story3.append(Spacer(1, 14))

    summary_data3 = [
        ["Total Credits Earned: 19.0", "SGPA: 8.84", "CGPA: 8.72", "Result: PASSED"]
    ]
    t_sum3 = Table(summary_data3, colWidths=[1.8*inch, 1.8*inch, 1.8*inch, 1.8*inch])
    t_sum3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0FDFA")),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#0F766E")),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#99F6E4")),
    ]))
    story3.append(t_sum3)
    doc3.build(story3)

    # 4. Memo with Discrepancy / Missing Fields (for testing Verification & Issue Flags)
    pdf_path_4 = OUTPUT_DIR / "memo_4_flagged_review.pdf"
    doc4 = SimpleDocTemplate(str(pdf_path_4), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story4 = []

    story4.append(Paragraph("STATE TECHNICAL BOARD OF EXAMINATIONS", title_style))
    story4.append(Paragraph("PROVISIONAL CERTIFICATE OF MARKS", sub_title_style))
    story4.append(Spacer(1, 10))

    # Missing student name and regulation intentionally to trigger verification queue
    info_data4 = [
        [Paragraph("<b>Roll No:</b>", label_style), Paragraph("20B91A0499", val_style),
         Paragraph("<b>Course:</b>", label_style), Paragraph("B.TECH", val_style)],
        [Paragraph("<b>Branch:</b>", label_style), Paragraph("ELECTRONICS & COMMUNICATION", val_style),
         Paragraph("<b>Semester:</b>", label_style), Paragraph("IV-I", val_style)],
    ]
    t_info4 = Table(info_data4, colWidths=[1.1*inch, 2.5*inch, 1.1*inch, 2.5*inch])
    story4.append(t_info4)
    story4.append(Spacer(1, 12))

    subjects_data4 = [
        ["Sub Code", "Subject Name", "Tot", "Grade", "Credits", "Result"],
        ["EC401", "DIGITAL SIGNAL PROCESSING", "72", "A", "3.0", "P"],
        ["EC402", "ANTENNAS & PROPAGATION", "65", "B+", "3.0", "P"],
        ["EC403", "CONTROL SYSTEMS", "58", "B", "3.0", "P"],
        ["EC404", "EMBEDDED SYSTEMS DESIGN", "85", "A+", "4.0", "P"]
    ]
    t_sub4 = Table(subjects_data4, colWidths=[1.2*inch, 3.2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
    t_sub4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4338CA")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#9CA3AF")),
    ]))
    story4.append(t_sub4)
    story4.append(Spacer(1, 14))

    # Intentionally false SGPA (9.80 vs calculated ~7.46) to trigger CALCULATION_MISMATCH issue!
    summary_data4 = [
        ["Total Credits: 13.0", "SGPA: 9.80", "CGPA: 8.00", "Result: PASSED"]
    ]
    t_sum4 = Table(summary_data4, colWidths=[1.8*inch, 1.8*inch, 1.8*inch, 1.8*inch])
    t_sum4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EEF2FF")),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#4338CA")),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#C7D2FE")),
    ]))
    story4.append(t_sum4)
    doc4.build(story4)

    # 5. Multi-Semester Student Progression (3-Page PDF for a Single Student)
    from reportlab.platypus import PageBreak
    pdf_path_5 = OUTPUT_DIR / "memo_multi_semester.pdf"
    doc5 = SimpleDocTemplate(str(pdf_path_5), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story5 = []

    sem_info_list = [
        {
            "sem": "I Year I Semester (I-I)",
            "sgpa": "8.25", "cgpa": "8.25", "res": "PASSED",
            "subjects": [
                ["18CS101", "MATHEMATICS - I", "25", "45", "70", "A", "4.0", "P"],
                ["18CS102", "APPLIED PHYSICS", "24", "46", "70", "A", "4.0", "P"],
                ["18CS103", "PROGRAMMING FOR PROBLEM SOLVING", "28", "58", "86", "A+", "4.0", "P"],
                ["18CS104", "ENGINEERING GRAPHICS", "26", "44", "70", "A", "3.0", "P"],
                ["18CS105", "BASIC ELECTRICAL ENGG LAB", "24", "48", "72", "O", "1.5", "P"],
                ["18CS106", "PHYSICS LAB", "23", "47", "70", "A+", "1.5", "P"]
            ]
        },
        {
            "sem": "I Year II Semester (I-II)",
            "sgpa": "6.85", "cgpa": "7.55", "res": "PROMOTED",
            "subjects": [
                ["18CS201", "MATHEMATICS - II", "22", "42", "64", "B+", "4.0", "P"],
                ["18CS202", "CHEMISTRY", "24", "44", "68", "B+", "4.0", "P"],
                ["18CS203", "DATA STRUCTURES", "15", "20", "35", "F", "0.0", "F"], # Backlog!
                ["18CS204", "BASIC ELECTRONICS", "25", "48", "73", "A", "3.0", "P"],
                ["18CS205", "DATA STRUCTURES LAB", "24", "46", "70", "A+", "1.5", "P"],
                ["18CS206", "CHEMISTRY LAB", "23", "45", "68", "O", "1.5", "P"]
            ]
        },
        {
            "sem": "II Year I Semester (II-I)",
            "sgpa": "8.70", "cgpa": "7.95", "res": "PASSED",
            "subjects": [
                ["18CS301", "DISCRETE MATHEMATICS", "27", "52", "79", "A+", "4.0", "P"],
                ["18CS302", "DIGITAL LOGIC DESIGN", "26", "50", "76", "A+", "3.0", "P"],
                ["18CS303", "OBJECT ORIENTED PROGRAMMING (JAVA)", "28", "58", "86", "O", "4.0", "P"],
                ["18CS304", "COMPUTER ORGANIZATION & ARCHITECTURE", "25", "48", "73", "A", "3.0", "P"],
                ["18CS305", "DATABASE MANAGEMENT SYSTEMS", "29", "59", "88", "O", "4.0", "P"],
                ["18CS306", "JAVA PROGRAMMING LAB", "24", "48", "72", "O", "1.5", "P"]
            ]
        }
    ]

    for idx, s_data in enumerate(sem_info_list):
        story5.append(Paragraph("INSTITUTE OF AERONAUTICAL ENGINEERING (AUTONOMOUS)", title_style))
        story5.append(Paragraph("Dundigal, Hyderabad - 500 043, Telangana", sub_title_style))
        story5.append(Paragraph(f"<b>GRADE CARD / MARKS MEMORANDUM</b>", ParagraphStyle(f'GC_{idx}', parent=sub_title_style, fontSize=11, fontName="Helvetica-Bold")))
        story5.append(Spacer(1, 10))

        info5 = [
            [Paragraph("<b>H.T. No:</b>", label_style), Paragraph("21B01A0588", val_style),
             Paragraph("<b>Course:</b>", label_style), Paragraph("B.TECH", val_style)],
            [Paragraph("<b>Name:</b>", label_style), Paragraph("V. ADITYA VARMA", val_style),
             Paragraph("<b>Branch:</b>", label_style), Paragraph("COMPUTER SCIENCE & ENGINEERING", val_style)],
            [Paragraph("<b>Regulation:</b>", label_style), Paragraph("R20", val_style),
             Paragraph("<b>Semester:</b>", label_style), Paragraph(s_data["sem"], val_style)],
        ]
        t_info5 = Table(info5, colWidths=[1.1*inch, 2.5*inch, 1.1*inch, 2.5*inch])
        story5.append(t_info5)
        story5.append(Spacer(1, 12))

        sub_table_data = [["Sub Code", "Subject Name", "Int", "Ext", "Tot", "Grade", "Credits", "Result"]]
        sub_table_data.extend(s_data["subjects"])
        t_subs5 = Table(sub_table_data, colWidths=[0.9*inch, 3.2*inch, 0.5*inch, 0.5*inch, 0.6*inch, 0.6*inch, 0.6*inch, 0.6*inch])
        t_subs5.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#065F46")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#9CA3AF")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ALIGN', (1,1), (1,-1), 'LEFT'),
        ]))
        story5.append(t_subs5)
        story5.append(Spacer(1, 14))

        sum_data5 = [[f"SGPA: {s_data['sgpa']}", f"Cumulative CGPA: {s_data['cgpa']}", f"Result: {s_data['res']}"]]
        t_sum5 = Table(sum_data5, colWidths=[2.4*inch, 2.4*inch, 2.4*inch])
        t_sum5.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#ECFDF5")),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#065F46")),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#A7F3D0")),
        ]))
        story5.append(t_sum5)

        if idx < len(sem_info_list) - 1:
            story5.append(PageBreak())

    doc5.build(story5)

    # 6. Multi-Student Class Gazette (3 Students across 3 Pages in 1 PDF)
    pdf_path_6 = OUTPUT_DIR / "memo_class_gazette.pdf"
    doc6 = SimpleDocTemplate(str(pdf_path_6), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story6 = []

    gazette_students = [
        {"roll": "21671A0501", "name": "CH. SAI KUMAR", "sgpa": "8.80", "grade": "A+", "res": "PASSED"},
        {"roll": "21671A0502", "name": "G. DIVYA TEJA", "sgpa": "9.15", "grade": "O", "res": "PASSED"},
        {"roll": "21671A0503", "name": "M. NIKHIL REDDY", "sgpa": "7.40", "grade": "B+", "res": "PASSED"},
    ]

    for idx, g_stud in enumerate(gazette_students):
        story6.append(Paragraph("JAWAHARLAL NEHRU TECHNOLOGICAL UNIVERSITY HYDERABAD", title_style))
        story6.append(Paragraph("OFFICIAL CLASS TABULATION & MARKS GAZETTE", sub_title_style))
        story6.append(Paragraph("<b>GRADE CARD / MARKS MEMORANDUM</b>", ParagraphStyle(f'GZ_{idx}', parent=sub_title_style, fontSize=11, fontName="Helvetica-Bold")))
        story6.append(Spacer(1, 10))

        info6 = [
            [Paragraph("<b>H.T. No:</b>", label_style), Paragraph(g_stud["roll"], val_style),
             Paragraph("<b>Course:</b>", label_style), Paragraph("B.TECH", val_style)],
            [Paragraph("<b>Name:</b>", label_style), Paragraph(g_stud["name"], val_style),
             Paragraph("<b>Branch:</b>", label_style), Paragraph("INFORMATION TECHNOLOGY", val_style)],
            [Paragraph("<b>College:</b>", label_style), Paragraph("J.B. INSTITUTE OF ENGINEERING & TECHNOLOGY", val_style),
             Paragraph("<b>Semester:</b>", label_style), Paragraph("III Year I Semester (III-I)", val_style)],
        ]
        t_info6 = Table(info6, colWidths=[1.1*inch, 2.5*inch, 1.1*inch, 2.5*inch])
        story6.append(t_info6)
        story6.append(Spacer(1, 12))

        sub_table_data6 = [
            ["Sub Code", "Subject Name", "Tot", "Grade", "Credits", "Result"],
            ["IT501", "DESIGN & ANALYSIS OF ALGORITHMS", "82", g_stud["grade"], "4.0", "P"],
            ["IT502", "SOFTWARE ENGINEERING", "78", "A", "3.0", "P"],
            ["IT503", "WEB TECHNOLOGIES", "86", "A+", "3.0", "P"],
            ["IT504", "DATA MINING & WAREHOUSING", "74", "A", "3.0", "P"],
            ["IT505", "ALGORITHMS LAB", "90", "O", "1.5", "P"],
            ["IT506", "WEB DEVELOPMENT LAB", "92", "O", "1.5", "P"]
        ]
        t_subs6 = Table(sub_table_data6, colWidths=[1.0*inch, 3.4*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch])
        t_subs6.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#9CA3AF")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ALIGN', (1,1), (1,-1), 'LEFT'),
        ]))
        story6.append(t_subs6)
        story6.append(Spacer(1, 14))

        sum_data6 = [[f"Total Credits: 16.0", f"SGPA: {g_stud['sgpa']}", f"Result: {g_stud['res']}"]]
        t_sum6 = Table(sum_data6, colWidths=[2.4*inch, 2.4*inch, 2.4*inch])
        t_sum6.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#1E3A8A")),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#93C5FD")),
        ]))
        story6.append(t_sum6)

        if idx < len(gazette_students) - 1:
            story6.append(PageBreak())

    doc6.build(story6)

    # 7. Create ZIP archive packaging sample memos
    import zipfile
    zip_path = OUTPUT_DIR / "batch_sample_memos.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in [pdf_path_1, pdf_path_2, pdf_path_3, pdf_path_4]:
            if p.exists():
                z.write(p, arcname=p.name)

    print("Successfully generated all synthetic memos (Single, Multi-Semester, Gazette, ZIP):")
    print(f" - {pdf_path_1.name}")
    print(f" - {pdf_path_2.name}")
    print(f" - {pdf_path_3.name}")
    print(f" - {pdf_path_4.name}")
    print(f" - {pdf_path_5.name} (Multi-Semester 3-Page Document)")
    print(f" - {pdf_path_6.name} (Multi-Student Class Gazette)")
    print(f" - {zip_path.name} (Compressed Batch Archive)")

if __name__ == "__main__":
    generate_sample_memos()

