from django.http import HttpResponse, HttpResponseServerError

def process_google_message(request, controller, input_xml=None):
    if input_xml is None:
        if not request.POST:
            raise Http404('Not a POST method')
        input_xml = request.raw_post_data
    try:
        output_xml = controller.receive_xml(input_xml)
        return HttpResponse(output_xml, mimetype='text/xml')
    except Exception, exc:
        return HttpResponseServerError(str(exc))
