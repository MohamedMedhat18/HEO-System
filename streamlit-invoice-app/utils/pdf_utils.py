def generate_pdf(invoice_data, rtl=False):
    import io
    import os
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    import arabic_reshaper
    from bidi.algorithm import get_display

    buf = io.BytesIO()
    try:
        c = canvas.Canvas(buf, pagesize=letter)
        width, height = letter
        logo_w = 3.77 * 72
        logo_h = 1.9 * 72
        logo_path = invoice_data.get("logo")
        if logo_path and os.path.exists(logo_path):
            try:
                c.drawImage(logo_path, width - logo_w - 40, height - logo_h - 30, logo_w, logo_h)
            except Exception:
                pass
        company_lines = [
            "HEO",
            "🏭 ADDRESS : 41 Al-Mawardi Street, Al-Qasr Al-Aini, Cairo, Egypt",
            "📞 Tel: +201026531004 / +201147304880",
            "📭 Fax: +2027932115",
            "📝 Email : info@heomed.com",
            "🌍 Web Site : www.heomed.com",
        ]
        y = height - 50
        for line in company_lines:
            c.setFont("Helvetica", 8)
            out = _shape_text_for_pdf(line, rtl=rtl)
            c.drawString(40, y, out)
            y -= 12
        title = invoice_data.get("title", "Quotation Invoice / عرض سعر")
        c.setFont("Helvetica-Bold", 16)
        title_out = _shape_text_for_pdf(title, rtl=rtl)
        c.drawCentredString(width / 2, height - 120, title_out)
        meta_y = height - 160
        c.setFont("Helvetica", 10)
        c.drawString(40, meta_y, _shape_text_for_pdf(f"Client: {invoice_data.get('client_name','')}", rtl=rtl))
        c.drawString(40, meta_y - 14, _shape_text_for_pdf(f"Date: {invoice_data.get('date', '')}", rtl=rtl))
        c.drawString(40, meta_y - 28, _shape_text_for_pdf(f"Invoice #: {invoice_data.get('invoice_number','')}", rtl=rtl))
        table_y = meta_y - 70
        c.setLineWidth(0.5)
        c.rect(40, table_y - 200, width - 80, 200, stroke=1, fill=0)
        items = invoice_data.get('items', [])
        item_y = table_y - 20
        c.setFont("Helvetica", 9)
        c.drawString(50, item_y + 10, _shape_text_for_pdf("Item", rtl=rtl))
        c.drawString(width/2 - 40, item_y + 10, _shape_text_for_pdf("Qty", rtl=rtl))
        c.drawString(width - 180, item_y + 10, _shape_text_for_pdf("Price", rtl=rtl))
        c.drawString(width - 80, item_y + 10, _shape_text_for_pdf("Total", rtl=rtl))
        item_y -= 10
        for it in items:
            desc = _shape_text_for_pdf(it.get('description', ''), rtl=rtl)
            qty = str(it.get('quantity', ''))
            price = str(it.get('price', ''))
            total = str(it.get('total', ''))
            c.drawString(50, item_y, desc)
            c.drawString(width/2 - 40, item_y, qty)
            c.drawString(width - 180, item_y, price)
            c.drawString(width - 80, item_y, total)
            item_y -= 18
            if item_y < 60:
                c.showPage()
                item_y = height - 60
        c.setFont("Helvetica-Bold", 11)
        c.drawRightString(width - 50, item_y - 10, _shape_text_for_pdf(f"Total: {invoice_data.get('total','')}", rtl=rtl))
        c.save()
        buf.seek(0)
        return buf.getvalue()
    except Exception:
        return b""

def _shape_text_for_pdf(text, rtl=False):
    if not isinstance(text, str):
        text = str(text)
    if rtl and arabic_reshaper and get_display:
        try:
            shaped = arabic_reshaper.reshape(text)
            return get_display(shaped)
        except Exception:
            return text
    return text