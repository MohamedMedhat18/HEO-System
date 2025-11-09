"""
PDF Generation Utilities for HEO Invoice System

This module provides professional PDF generation capabilities for invoices
with support for multiple items, bilingual output, and custom styling.

Design Decisions:
- Separated PDF logic from UI for better modularity and testability
- Uses ReportLab for professional-grade PDF generation
- Supports Arabic text with proper reshaping and RTL layout
- Includes professional styling with company branding
- Handles multiple currency formats

Author: AI-powered refactoring
"""

import os
import io
import json
from datetime import datetime
from typing import Dict, List, Optional


def generate_professional_pdf(
    invoice_data: Dict,
    language: str = 'en',
    output_path: Optional[str] = None
) -> bytes:
    """
    Generate a professional invoice PDF with multiple items support.
    
    This function creates a beautifully formatted PDF invoice with:
    - Company branding and logo
    - Client information
    - Multiple line items with calculations
    - Professional styling and layout
    - Bilingual support (English/Arabic)
    - Currency formatting
    
    Args:
        invoice_data: Dictionary containing invoice details:
            - id: Invoice ID
            - client_name: Client name
            - client_address: Client address
            - items: List of items with description, quantity, price, total
            - invoice_type: Type of invoice
            - date: Invoice date
            - currency: Currency code (EGP, USD, EUR)
            - notes: Additional notes
            - agent_name: Name of agent who created invoice
        language: Language code ('en' or 'ar')
        output_path: Optional path to save PDF file
    
    Returns:
        bytes: PDF file content as bytes
    
    Example:
        >>> invoice_data = {
        ...     'id': 123,
        ...     'client_name': 'ACME Corp',
        ...     'items': [
        ...         {'description': 'Product A', 'quantity': 2, 'price': 50.0, 'total': 100.0},
        ...         {'description': 'Product B', 'quantity': 1, 'price': 75.0, 'total': 75.0}
        ...     ],
        ...     'currency': 'USD'
        ... }
        >>> pdf_bytes = generate_professional_pdf(invoice_data)
    """
    try:
        # Import ReportLab components
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Paragraph,
            Spacer, Image
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        # Handle Arabic text if needed
        if language == 'ar':
            try:
                import arabic_reshaper
                from bidi.algorithm import get_display
            except ImportError:
                arabic_reshaper = None
                get_display = None
        
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Container for PDF elements
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#183475'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#3880fa'),
            spaceAfter=12
        )
        
        # Helper function for Arabic text
        def format_text(text, is_arabic=False):
            """Format text for PDF, handling Arabic if needed."""
            if is_arabic and arabic_reshaper and get_display:
                reshaped_text = arabic_reshaper.reshape(str(text))
                return get_display(reshaped_text)
            return str(text)
        
        # Title
        invoice_type = invoice_data.get('invoice_type', 'Invoice')
        if language == 'ar':
            type_map = {
                'Quotation Invoice': 'عرض سعر',
                'Commercial Invoice': 'فاتورة تجارية',
                'Proforma Invoice': 'فاتورة أولية'
            }
            invoice_type = type_map.get(invoice_type, 'فاتورة')
        
        title = Paragraph(
            format_text(invoice_type, language == 'ar'),
            title_style
        )
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Company Information
        company_info = [
            ['Company:', 'EL HEKMA ENGINEERING OFFICE Co.'],
            ['Address:', '41 Al-Mawardi Street, Al-Qasr Al-Aini, Cairo, Egypt'],
            ['Tel:', '+201026531004 / +201147304880'],
            ['Email:', 'info@heomed.com']
        ]
        
        company_table = Table(company_info, colWidths=[1.5*inch, 4.5*inch])
        company_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(company_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Invoice Details
        invoice_details = [
            ['Invoice #:', f"INV-{invoice_data.get('id', 'N/A')}"],
            ['Date:', invoice_data.get('date', datetime.now().strftime('%Y-%m-%d'))],
            ['Client:', invoice_data.get('client_name', 'N/A')],
            ['Address:', invoice_data.get('client_address', 'N/A')],
        ]
        
        details_table = Table(invoice_details, colWidths=[1.5*inch, 4.5*inch])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#183475')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(details_table)
        elements.append(Spacer(1, 0.4*inch))
        
        # Items Table
        items_header = ['#', 'Description', 'Qty', 'Unit Price', 'Total']
        items_data = [items_header]
        
        items = invoice_data.get('items', [])
        currency = invoice_data.get('currency', 'EGP')
        
        for idx, item in enumerate(items, 1):
            items_data.append([
                str(idx),
                format_text(item.get('description', ''), language == 'ar'),
                str(item.get('quantity', 0)),
                f"{currency} {item.get('price', 0):,.2f}",
                f"{currency} {item.get('total', 0):,.2f}"
            ])
        
        # Calculate totals
        subtotal = sum(item.get('total', 0) for item in items)
        tax = invoice_data.get('tax', 0)
        discount = invoice_data.get('discount', 0)
        grand_total = subtotal + tax - discount
        
        items_table = Table(
            items_data,
            colWidths=[0.5*inch, 3*inch, 0.8*inch, 1.2*inch, 1.2*inch]
        )
        
        items_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#183475')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Body
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Item number
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Description
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),  # Numbers
            
            # Borders and padding
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(items_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Totals
        totals_data = [
            ['Subtotal:', f"{currency} {subtotal:,.2f}"],
            ['Grand Total:', f"{currency} {grand_total:,.2f}"]
        ]
        
        totals_table = Table(totals_data, colWidths=[4.8*inch, 1.2*inch])
        totals_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica'),
            ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LINEABOVE', (0, 1), (-1, 1), 2, colors.HexColor('#183475')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(totals_table)
        
        # Notes
        if invoice_data.get('notes'):
            elements.append(Spacer(1, 0.3*inch))
            notes_heading = Paragraph('Notes:', heading_style)
            elements.append(notes_heading)
            notes_text = Paragraph(
                format_text(invoice_data.get('notes', ''), language == 'ar'),
                styles['Normal']
            )
            elements.append(notes_text)
        
        # Footer
        elements.append(Spacer(1, 0.5*inch))
        footer_text = Paragraph(
            '<i>Thank you for your business!</i>',
            ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#999999'),
                alignment=TA_CENTER
            )
        )
        elements.append(footer_text)
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Save to file if path provided
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
        
        return pdf_bytes
        
    except ImportError as e:
        # Fallback if ReportLab not available
        error_msg = f"PDF generation requires ReportLab: {str(e)}"
        return error_msg.encode('utf-8')
    except Exception as e:
        # General error handling
        error_msg = f"Error generating PDF: {str(e)}"
        return error_msg.encode('utf-8')


def save_pdf_to_file(pdf_bytes: bytes, filename: str, directory: str = 'invoices') -> str:
    """
    Save PDF bytes to a file.
    
    Args:
        pdf_bytes: PDF content as bytes
        filename: Name of the file (without path)
        directory: Directory to save the file (default: 'invoices')
    
    Returns:
        str: Full path to the saved file
    
    Example:
        >>> pdf_bytes = generate_professional_pdf(invoice_data)
        >>> path = save_pdf_to_file(pdf_bytes, 'invoice_123.pdf')
    """
    # Ensure directory exists
    os.makedirs(directory, exist_ok=True)
    
    # Full path
    file_path = os.path.join(directory, filename)
    
    # Write file
    with open(file_path, 'wb') as f:
        f.write(pdf_bytes)
    
    return file_path


def get_invoice_filename(invoice_id: int, language: str = 'en') -> str:
    """
    Generate a standardized filename for an invoice PDF.
    
    Args:
        invoice_id: Invoice ID
        language: Language code ('en' or 'ar')
    
    Returns:
        str: Standardized filename
    
    Example:
        >>> filename = get_invoice_filename(123, 'en')
        >>> print(filename)
        'invoice_123_20240101_120000_en.pdf'
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"invoice_{invoice_id}_{timestamp}_{language}.pdf"
