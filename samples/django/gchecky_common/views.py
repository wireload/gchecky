from django.http import Http404, HttpResponse, HttpResponseServerError
from gchecky_common import render_to_response
from gchecky_common.controller import get_controller

def process_google_message(request, input_xml=None, safe_to_raise=False):
    controller = get_controller()
    if input_xml is None:
        if not request.POST:
            raise Http404('Has to be a POST request')
        input_xml = request.raw_post_data
    try:
        output_xml = controller.receive_xml(input_xml)
        return HttpResponse(output_xml, mimetype='text/xml')
    except Exception, exc:
        # For testing -- propagate the exception
        if safe_to_raise:
            raise
        return HttpResponseServerError(str(exc))

def test_processing_message(request, template):
    input = None
    output = None
    if request.POST and request.POST.has_key('input'):
        input = request.POST['input']
        try:
            output = process_google_message(request, input, safe_to_raise=True)
        except Exception, e:
            output = 'Error in process_google_message: %s' % (unicode(e),)
    if input is None:
        input = '<?xml version="1.0" encoding="UTF-8"?><hello xmlns="http://checkout.google.com/schema/2" />'
    return render_to_response(template,
                              {'input':input, 'output':output},
                              request=request)

def order_details(request, order_id, template, template_object):
    from gchecky_common.models import Order
    order = Order.objects.get(id=order_id)
    return render_to_response(template, {template_object:order}, request=request)
