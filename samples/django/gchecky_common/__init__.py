
def render_to_response(template, context, request, *args, **kwargs):
    """
    Custom version of render_to_response helper that uses RequestContext
    instead of the dummy Context class.
    """
    from django.shortcuts import render_to_response as rtr
    from django.template import RequestContext
    return rtr(template, context, context_instance=RequestContext(request), *args, **kwargs)