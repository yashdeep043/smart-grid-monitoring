import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def create_phase1_pdf():
    pdf_path = r"C:\Users\yashd\.gemini\antigravity\scratch\smart_grid_monitoring\Smart_Grid_Master_Textbook_Phase1.pdf"
    
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0366d6'),
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#586069'),
        spaceAfter=20
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0366d6'),
        spaceBefore=15,
        spaceAfter=8
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1b1f23'),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#24292e'),
        spaceAfter=8
    )
    
    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#032f62'),
        backColor=colors.HexColor('#f6f8fa'),
        spaceBefore=6,
        spaceAfter=8,
        leftIndent=10,
        rightIndent=10
    )
    
    callout_style = ParagraphStyle(
        'Callout_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#24292e'),
        backColor=colors.HexColor('#f1f8ff'),
        borderColor=colors.HexColor('#0366d6'),
        borderWidth=1,
        borderPadding=8,
        spaceBefore=8,
        spaceAfter=8
    )

    story = []
    
    # Title Header
    story.append(Paragraph("⚡ ESP32 Smart Grid Monitoring & Fault Analysis System", title_style))
    story.append(Paragraph("Comprehensive University Master Textbook & Reverse Engineering Manual — Phase 1", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0366d6'), spaceAfter=15))

    # Phase 1 Content
    story.append(Paragraph("Phase 1: Project Overview & Strategic Foundations", h1_style))
    
    # Question 1
    story.append(Paragraph("1. What Problem Does This Project Solve?", h2_style))
    story.append(Paragraph(
        "Modern electrical distribution networks face severe operational challenges due to traditional 'dumb' infrastructure. "
        "When an outage, voltage sag, or short circuit occurs, utility companies historically rely on manual customer phone complaints "
        "to discover that a power line has failed. This causes massive delays in fault location, equipment destruction from unmitigated "
        "overload spikes, and severe financial losses. This project solves this by placing IoT sensor nodes (ESP32) on power lines "
        "that continuously stream 3-phase voltage, current, active/reactive power, power factor, and frequency data every 1 second over "
        "MQTT to a central Python server. The server instantly calculates AC power flow physics (Pandapower), evaluates short-circuit fault "
        "currents and relay trip times (OpenDSS), and executes AI models (IsolationForest & RandomForest) to catch anomalies and predict 24-hour demand.",
        body_style
    ))
    
    # Question 2
    story.append(Paragraph("2. Why is This Project Important?", h2_style))
    story.append(Paragraph(
        "Power distribution grids are undergoing the global '3Ds Energy Transition': Decarbonization (shifting to solar/wind), "
        "Decentralization (rooftop solar feeding power back into local feeders), and Digitalization. Without digital monitoring, "
        "reverse power flows from rooftop solar panels cause distribution line overvoltages and transformer overheating. This project "
        "is critical because it provides an open-source, sub-second telemetry and AI intelligence platform at 1% of the cost of legacy industrial SCADA systems.",
        body_style
    ))

    # Question 3
    story.append(Paragraph("3. Real World Applications", h2_style))
    story.append(Paragraph("• <b>Smart Cities</b>: Neighborhood 3-phase voltage balance and automated transformer health surveillance.<br/>"
                           "• <b>Solar & Wind Microgrids</b>: Tracking reverse energy feed-in and managing solar intermittency.<br/>"
                           "• <b>Industrial Plants</b>: Monitoring heavy motor power factor (cos φ ≥ 0.90) to prevent utility penalty charges.<br/>"
                           "• <b>EV Fast-Charging Hubs</b>: Dynamic load management to prevent substation transformer overloads.", body_style))

    # Question 4
    story.append(Paragraph("4. Target Users", h2_style))
    story.append(Paragraph("• <b>Electrical Distribution Utilities (Discoms)</b>: Control room operators monitoring substations.<br/>"
                           "• <b>Microgrid & Renewable Energy Engineers</b>: Managing localized solar PV farms.<br/>"
                           "• <b>Factory Energy Managers</b>: Preventing industrial motor burnout from low voltage sags.<br/>"
                           "• <b>Smart City Municipal Engineers</b>: Municipal power efficiency and streetlight telemetry.", body_style))

    # Question 5 & 6
    story.append(Paragraph("5 & 6. Existing Solutions & Limitations of Traditional Systems", h2_style))
    story.append(Paragraph(
        "Existing industrial SCADA solutions (Siemens Spectrum Power, Schneider EcoStruxure, ABB Ability, GE GridIQ) cost $500,000 to $5,000,000+ "
        "per substation. Traditional systems suffer from:<br/>"
        "1. <b>High Cost</b>: Multi-million dollar hardware & software licensing.<br/>"
        "2. <b>Slow Refresh Rates</b>: Legacy utility meters sample data only once every 15 to 60 minutes.<br/>"
        "3. <b>Proprietary Lock-in</b>: Siemens software works only with Siemens hardware controllers.<br/>"
        "4. <b>Siloed Architectures</b>: Physics engines and AI analytics are sold as separate, disconnected enterprise applications.",
        body_style
    ))

    # Question 7
    story.append(Paragraph("7. Why This Approach is Better", h2_style))
    story.append(Paragraph(
        "Your project is superior because it uses standard open-source Python, lightweight MQTT Wi-Fi messaging (1-second latency), "
        "low-cost ESP32 microcontrollers ($15 per node), and natively unifies non-linear AC Newton-Raphson power flow physics with "
        "Machine Learning AI inside a single high-density cyber web dashboard accessible on any mobile browser.",
        body_style
    ))

    # Question 8 & 9
    story.append(Paragraph("8 & 9. Business Value & Technical Value", h2_style))
    story.append(Paragraph(
        "<b>Business Value</b>: Saves utility companies millions by preventing transformer explosions, reducing outage repair times from hours to seconds, "
        "and eliminating reactive power penalty fees.<br/>"
        "<b>Technical Value</b>: Combines Kirchhoff's electrical laws (Pandapower), OpenDSS sequence matrix fault math, and Scikit-Learn unsupervised IsolationForest "
        "anomaly scoring into a unified multi-threaded architecture.",
        body_style
    ))

    # Question 10
    story.append(Paragraph("10. Future Scope", h2_style))
    story.append(Paragraph(
        "1. <b>Hardware Relay Tripping</b>: Program ESP32 outputs to trigger physical circuit breaker relays on short circuits.<br/>"
        "2. <b>LoRaWAN / 4G Cellular</b>: Deploy SIM800L LTE modems for remote rural power lines up to 15 km.<br/>"
        "3. <b>LSTM Deep Learning</b>: Upgrade load forecasting to Long Short-Term Memory neural networks.<br/>"
        "4. <b>Blockchain P2P Energy Trading</b>: Smart contracts allowing solar households to sell excess power to neighbors.",
        body_style
    ))

    doc.build(story)
    print(f"Generated PDF at: {pdf_path}")

if __name__ == "__main__":
    create_phase1_pdf()
