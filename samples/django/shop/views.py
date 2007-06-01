import traceback
from base64 import b64encode

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response

from shop.checkout import handle_notification, prepare_items
from shop.models import Item, Log, Package

def index(request):
    if request.POST:
        items = []
        for name in request.POST:
            name[:5] == "item_"
            try:
                item = Item.objects.get(id=int(name[5:]))
                items.append(item)
            except Exception,msg:
                pass
        if items:
            gbasket = prepare_items(items)
            weight = price = 0
            for item in items:
                price += item.price
                weight += item.weight
            return render_to_response('shop/checkout.html', {'items':Item.objects.all(),
                                                             'total_price':price,
                                                             'total_weight':weight,
                                                             'gbasket':gbasket})
    error = request.GET and request.GET.has_key('error') and request.GET['error']
    return render_to_response('shop/index.html', {'items':Item.objects.all(),
                                                  'packages':Package.objects.all(),
                                                  'error':error or ''})

def checkout(request):
    package = Package()
    package.items = items
    package.save()
    return HttpResponseRedirect('/shop/checkout/')

def log_grequest(ixml, oxml, error=None):
    log = Log()
    log.input = ixml or '--'
    log.output = oxml or '--'
    try:
        from gchecky.gxml import Document
        i = Document.fromxml(ixml)
        log.order_id = i.google_order_number
    except Exception, msg:
        # TODO ?? do not cut off the message tail
        log.order_id = str(msg[:200])
    log.order_id = log.order_id or '--'
    log.code = (error is None and 'ok') or 'error'
    log.error = error or '--'
    log.save()

def gdo(request):
    error = ''
    if request.POST and request.POST.has_key('p_id'):
        try:
            package = Package.objects.get(id=int(request.POST['p_id']))
            from shop.checkout import controller
            if request.POST.has_key('charge'):
                controller.charge_order(package.google_id,
                                        package.get_rest())
            elif request.POST.has_key('charge10'):
                controller.charge_order(package.google_id,
                                        10)
            elif request.POST.has_key('refund'):
                controller.refund_order(package.google_id,
                                        package.charged,
                                        'TEST REFUND')
            elif request.POST.has_key('archive'):
                controller.archive_order(package.google_id)
            elif request.POST.has_key('unarchive'):
                controller.unarchive_order(package.google_id)
            elif request.POST.has_key('process'):
                controller.process_order(package.google_id)
            elif request.POST.has_key('deliver'):
                controller.deliver_order(package.google_id)
            elif request.POST.has_key('cancel'):
                controller.cancel_order(package.google_id,
                                        'TEST CANCEL')
            else:
                raise Exception('Unknown action requested!')
        except Exception, exc:
            error = u'%s\n%s' % (exc.message, traceback.format_exc())
    return HttpResponseRedirect('/shop/?error=%s' % (error.encode('ASCII', 'replace'),))

def ghandler(request):
    try:
        output_xml = ''
        if not request.POST:
            raise Exception('ghandler: Not a POST method')
        output_xml = handle_notification(request.raw_post_data)
        log_grequest(request.raw_post_data, output_xml)
        return HttpResponse(output_xml, mimetype='text/xml')
    except Exception, exc:
        message = 'Exception: %s\nTrace:\n%s' % (exc, traceback.format_exc())
        log_grequest(request.raw_post_data, output_xml,
                     message)
    raise Http404('Error processing the request: ' + message)

