import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def create_chapter1_pdf():
    pdf_path = r"C:\Users\yashd\.gemini\antigravity\scratch\smart_grid_monitoring\Smart_Grid_Textbook_Chapter_1_Power_Systems.pdf"
    
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0366d6'),
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#586069'),
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#0366d6'),
        spaceBefore=14,
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1b1f23'),
        spaceBefore=10,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#24292e'),
        spaceAfter=6
    )

    story = []
    
    # Title Header
    story.append(Paragraph("📘 Official University Master Textbook", title_style))
    story.append(Paragraph("Chapter 1: Electrical Power Engineering & Smart Grid Fundamentals from First Principles", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0366d6'), spaceAfter=12))

    # Section 1: Fundamental Electrical Physics
    story.append(Paragraph("Section 1: Fundamental Electrical Physics (Voltage, Current, Power)", h1_style))
    story.append(Paragraph("1.1 Definition of Electricity & Charge", h2_style))
    story.append(Paragraph(
        "Electricity is the set of physical phenomena associated with the presence and motion of matter that has a property of electric charge. "
        "The fundamental unit of charge is the electron, carrying -1.602 x 10^-19 Coulombs. Electric current (I) is the time rate of flow of electric charge: "
        "I = dQ / dt, measured in Amperes (Coulombs per second). Voltage (V) is the electric potential difference or electromotive force (EMF) that pushes electrons through a conductor, "
        "measured in Volts (Joules per Coulomb).",
        body_style
    ))
    
    story.append(Paragraph("1.2 Ohm's Law and Electrical Resistance", h2_style))
    story.append(Paragraph(
        "Ohm's Law states that the current flowing through a conductor between two points is directly proportional to the voltage across the two points: V = I * R, "
        "where R is resistance in Ohms. Resistance is determined by resistivity (rho), length (L), and cross-sectional area (A): R = rho * (L / A). "
        "In AC systems, opposition to current flow is called Impedance (Z), combining Resistance (R) and Inductive/Capacitive Reactance (X): Z = R + jX.",
        body_style
    ))

    # Section 2: AC Power Fundamentals
    story.append(Paragraph("Section 2: Alternating Current (AC) Power Fundamentals", h1_style))
    story.append(Paragraph("2.1 AC Sine Waves & RMS Voltage", h2_style))
    story.append(Paragraph(
        "Unlike Direct Current (DC) which flows in one direction, Alternating Current (AC) continuously reverses direction in a sinusoidal waveform: v(t) = V_peak * sin(2 * pi * f * t). "
        "In India and Europe, grid frequency (f) is 50.0 Hz (reversing 50 times per second). Root-Mean-Square (RMS) voltage represents the equivalent DC heating voltage: "
        "V_rms = V_peak / sqrt(2) = 230V for single phase, 400V for 3-phase line-to-line.",
        body_style
    ))

    story.append(Paragraph("2.2 Power Triangle (Active, Reactive, Apparent Power & Power Factor)", h2_style))
    story.append(Paragraph(
        "In AC power systems with inductive loads (motors, transformers), current lags behind voltage by phase angle (phi). Power is split into three components:<br/>"
        "• <b>Active Power (P)</b>: Real work consumed, measured in Kilowatts (kW). P = V * I * cos(phi).<br/>"
        "• <b>Reactive Power (Q)</b>: Magnetic field energy oscillating back and forth without doing work, measured in kVAR. Q = P * tan(arccos(phi)).<br/>"
        "• <b>Apparent Power (S)</b>: Total vector power capacity, measured in kVA. S = sqrt(P^2 + Q^2) = V * I.<br/>"
        "• <b>Power Factor (cos phi)</b>: Energy efficiency ratio (P / S). Power companies require cos phi >= 0.90 to prevent grid line losses.",
        body_style
    ))

    # Section 3: Distribution Network Architecture
    story.append(Paragraph("Section 3: Distribution Network Architecture & Transformers", h1_style))
    story.append(Paragraph("3.1 Grid Architecture (Generation -> Transmission -> Distribution)", h2_style))
    story.append(Paragraph(
        "1. <b>Generation</b>: Hydro, thermal, or solar plants generate power at 11kV to 25kV.<br/>"
        "2. <b>Transmission</b>: Step-up transformers raise voltage to 110kV - 765kV to minimize I^2 * R heat losses over long distances.<br/>"
        "3. <b>Substation</b>: Step-down transformers reduce voltage to 11kV distribution feeders.<br/>"
        "4. <b>Distribution Feeder</b>: 11kV radial lines carry power down streets to local distribution transformers.<br/>"
        "5. <b>Secondary Distribution</b>: Step-down transformers reduce 11kV to 400V 3-phase / 230V single-phase to power homes.",
        body_style
    ))

    # Section 4: Grid Faults & Relay Protection
    story.append(Paragraph("Section 4: Grid Short-Circuit Faults & Relay Protection", h1_style))
    story.append(Paragraph("4.1 Types of Short-Circuit Faults", h2_style))
    story.append(Paragraph(
        "• <b>3PH (Three-Phase Symmetrical)</b>: Severe fault where all 3 lines short-circuit together. I_f = V_ph / |Z1 + Rf|.<br/>"
        "• <b>SLG (Single Line-to-Ground)</b>: Most common fault (70-80% of events) where 1 phase touches ground. I_f = 3 * V_ph / |2*Z1 + Z0 + 3*Rf|.<br/>"
        "• <b>LL (Line-to-Line)</b>: Unsymmetrical fault between 2 phases. I_f = sqrt(3) * V_ph / |2*Z1 + 2*Rf|.",
        body_style
    ))

    story.append(Paragraph("4.2 Overcurrent Protection Relay Trip Curve (IEC Extremely Inverse)", h2_style))
    story.append(Paragraph(
        "Protection relays isolate short circuits before equipment explodes. Under IEC 60255 standards, trip time (t) follows the Extremely Inverse curve: "
        "t = 80 / ((I_fault / I_pickup)^2 - 1) seconds, ensuring higher fault currents trip the relay faster (in milliseconds).",
        body_style
    ))

    doc.build(story)
    print(f"Generated Chapter 1 PDF at: {pdf_path}")

if __name__ == "__main__":
    create_chapter1_pdf()
