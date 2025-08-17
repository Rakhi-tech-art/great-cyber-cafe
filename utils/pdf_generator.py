from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import os
from datetime import datetime

def generate_bill_pdf(bill):
    """Generate PDF for a bill"""
    
    # Create pdfs directory if it doesn't exist
    pdf_dir = os.path.join(os.getcwd(), 'static', 'pdfs')
    os.makedirs(pdf_dir, exist_ok=True)
    
    # PDF file path
    pdf_filename = f"{bill.bill_number}.pdf"
    pdf_path = os.path.join(pdf_dir, pdf_filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Company Header
    story.append(Paragraph("GREAT CYBER CAFE", title_style))
    story.append(Paragraph("Great Cyber Cafe", header_style))
    story.append(Paragraph("Email: greatcybercafe852@gmail.com | Phone: 9004398030", normal_style))
    story.append(Spacer(1, 20))
    
    # Invoice Header
    invoice_data = [
        ['INVOICE', ''],
        [f'Invoice Number: {bill.bill_number}', f'Date: {bill.created_at.strftime("%d/%m/%Y")}'],
        ['', f'Time: {bill.created_at.strftime("%I:%M %p")}'],
        ['', f'Due Date: {bill.due_date.strftime("%d/%m/%Y") if bill.due_date else "N/A"}']
    ]
    
    invoice_table = Table(invoice_data, colWidths=[3*inch, 3*inch])
    invoice_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 16),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(invoice_table)
    story.append(Spacer(1, 20))
    
    # Bill To Section
    story.append(Paragraph("BILL TO:", header_style))
    story.append(Paragraph(f"<b>{bill.customer.name}</b>", normal_style))
    if bill.customer.phone:
        story.append(Paragraph(f"Phone: {bill.customer.phone}", normal_style))
    if bill.customer.email:
        story.append(Paragraph(f"Email: {bill.customer.email}", normal_style))
    
    story.append(Spacer(1, 20))
    
    # Items Table
    items_data = [['Description', 'Quantity', 'Rate', 'Total']]
    
    for item in bill.items:
        items_data.append([
            item.description,
            f"{item.quantity:.2f}",
            f"Rs {item.rate:.2f}",
            f"Rs {item.total:.2f}"
        ])
    
    # Add subtotal, tax, discount, and total rows
    summary_rows = []

    # Only show subtotal if there's tax or discount
    if bill.tax_rate > 0 or bill.discount > 0:
        summary_rows.append(['', '', 'Subtotal:', f"Rs {bill.subtotal:.2f}"])
        if bill.tax_rate > 0:
            summary_rows.append(['', '', f'Tax ({bill.tax_rate}%):', f"Rs {bill.tax_amount:.2f}"])
        if bill.discount > 0:
            summary_rows.append(['', '', 'Discount:', f"Rs {bill.discount:.2f}"])

    # Total amount
    summary_rows.append(['', '', 'TOTAL AMOUNT:', f"Rs {bill.total_amount:.2f}"])

    # Payment status
    if bill.status == 'paid':
        summary_rows.extend([
            ['', '', 'PAID AMOUNT:', f"Rs {bill.total_amount:.2f}"],
            ['', '', 'REMAINING:', f"Rs 0.00"]
        ])
    else:
        summary_rows.extend([
            ['', '', 'PAID AMOUNT:', f"Rs 0.00"],
            ['', '', 'REMAINING:', f"Rs {bill.total_amount:.2f}"]
        ])

    items_data.extend(summary_rows)
    
    # Calculate the number of item rows (excluding header and summary)
    num_items = len(bill.items)
    summary_start_row = num_items + 1  # +1 for header

    items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
    items_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

        # Data rows (items only)
        ('FONTNAME', (0, 1), (-1, summary_start_row-1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, summary_start_row-1), 10),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),

        # Summary rows
        ('FONTNAME', (0, summary_start_row), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, summary_start_row), (-1, -1), 10),
        ('BACKGROUND', (0, -3), (-1, -1), colors.lightgrey),  # Highlight last 3 rows (total, paid, remaining)

        # Borders
        ('GRID', (0, 0), (-1, summary_start_row-1), 1, colors.black),  # Grid for items
        ('LINEBELOW', (0, summary_start_row), (-1, -1), 1, colors.black),  # Lines for summary

        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 20))
    
    # Notes section
    if bill.notes:
        story.append(Paragraph("NOTES:", header_style))
        story.append(Paragraph(bill.notes, normal_style))
        story.append(Spacer(1, 20))
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph("Thank you for your support!",
                          ParagraphStyle('Footer', parent=styles['Normal'],
                                       fontSize=12, alignment=TA_CENTER,
                                       textColor=colors.darkblue)))
    
    # Build PDF
    doc.build(story)
    
    return pdf_path
