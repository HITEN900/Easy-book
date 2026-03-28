from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def render_to_pdf(template_src, context_dict={}):
    """Generate PDF from HTML template"""
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    
    # Create PDF
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def generate_ticket_pdf(booking, booked_seats, route, bus):
    """Generate ticket PDF for a booking"""
    context = {
        'booking': booking,
        'booked_seats': booked_seats,
        'route': route,
        'bus': bus,
        'total_amount': booking.total_amount,
        'booking_date': booking.booking_date,
        'journey_date': booking.journey_date,
    }
    return render_to_pdf('customer/ticket_pdf.html', context)