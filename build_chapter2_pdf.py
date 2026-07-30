import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_chapter2_pdf():
    pdf_path = r"C:\Users\yashd\.gemini\antigravity\scratch\smart_grid_monitoring\Smart_Grid_Textbook_Chapter_2_Python.pdf"
    
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
    story.append(Paragraph("Chapter 2: Python 3.12 Deep-Dive & CPython Memory Architecture", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0366d6'), spaceAfter=12))

    # Section 1: CPython Architecture
    story.append(Paragraph("Section 1: CPython Architecture & Execution Model", h1_style))
    story.append(Paragraph("1.1 How CPython Executes Code", h2_style))
    story.append(Paragraph(
        "Python is an interpreted, dynamically-typed programming language implemented primarily in C (CPython). "
        "When you run 'python script.py', CPython performs 4 steps:<br/>"
        "1. <b>Lexing & Parsing</b>: Converts source text into an Abstract Syntax Tree (AST).<br/>"
        "2. <b>Bytecode Compilation</b>: Compiles AST into platform-independent bytecode instructions (.pyc cached files).<br/>"
        "3. <b>Evaluation Loop (ceval.c)</b>: Executes bytecode stack machine instructions.<br/>"
        "4. <b>PyObject Memory Management</b>: Allocates and frees memory structures using Reference Counting and a Cyclic Garbage Collector.",
        body_style
    ))

    story.append(Paragraph("1.2 PyObject Structure & Memory Allocator (PyMalloc)", h2_style))
    story.append(Paragraph(
        "In CPython, everything is an object. Every variable points to a C struct called PyObject containing two header fields:<br/>"
        "• <b>ob_refcnt</b>: Reference count tracking how many pointers target this object.<br/>"
        "• <b>ob_type</b>: Pointer to the type object defining methods and data size.<br/>"
        "CPython uses PyMalloc, a small-object memory allocator that manages 256KB Arenas split into 4KB Pools to avoid OS malloc overhead.",
        body_style
    ))

    # Section 2: Global Interpreter Lock & Threading
    story.append(Paragraph("Section 2: The Global Interpreter Lock (GIL) & Concurrency", h1_style))
    story.append(Paragraph("2.1 What is the GIL?", h2_style))
    story.append(Paragraph(
        "The Global Interpreter Lock (GIL) is a mutual exclusion lock used by CPython to prevent multiple native CPU threads "
        "from executing Python bytecodes at the same time. The GIL guarantees thread safety for CPython's reference counting mechanism.<br/>"
        "• <b>I/O-Bound Tasks (MQTT / Sockets / File Writes)</b>: CPython releases the GIL during network I/O wait times, allowing multi-threaded speedups.<br/>"
        "• <b>In This Project</b>: run_system.py uses threading.Thread(target=run_simulator_background, daemon=True) to run 1-second telemetry generation in parallel with Streamlit without blocking the UI.",
        body_style
    ))

    # Section 3: Core Python Built-ins
    story.append(Paragraph("Section 3: Core Standard Library Modules Used", h1_style))
    story.append(Paragraph("3.1 Built-in Modules Breakdown", h2_style))
    story.append(Paragraph(
        "• <b>sqlite3</b>: Implements C-bindings for serverless SQL storage.<br/>"
        "• <b>subprocess</b>: Executes external operating system binaries (pip install, streamlit run).<br/>"
        "• <b>threading</b>: Manages OS-level background daemon threads.<br/>"
        "• <b>json</b>: Performs fast serialization (json.dumps) and deserialization (json.loads) between dicts and UTF-8 strings.",
        body_style
    ))

    doc.build(story)
    print(f"Generated Chapter 2 PDF at: {pdf_path}")

if __name__ == "__main__":
    create_chapter2_pdf()
