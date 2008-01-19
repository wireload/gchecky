from django.shortcuts import get_object_or_404
from django.views.generic.simple import redirect_to
from gchecky_common import render_to_response
from gchecky_common.controller import get_controller
from gchecky_digital.models import DigitalItem

def make_back_url(request, url):
    return '%s://%s%s' % ((request.is_secure() and 'https') or 'http',
                          request.get_host(),
                          url)

def item_details(request, item_id, template, template_object):
    item = get_object_or_404(DigitalItem, id=item_id)
    return render_to_response(template, {template_object:item}, request=request)

def new_order(request, template):
    item_list = DigitalItem.objects.all()
    return render_to_response(template, {'item_list':item_list}, request=request)

def confirm_order(request, template):
    # TODO: any other prettier way to get an array input parameter value?
    ITEMS_VAR_NAME = 'item_'
    CONTINUE_SHOPPING_URL = make_back_url(request, '/digital/thanks')
    FRENCH_TAX = 0.196 # In France in general they apply the TAX of 19.6%
    if request.method == 'POST':
        items = []
        for key in request.POST.keys():
            if key[:len(ITEMS_VAR_NAME)] == ITEMS_VAR_NAME:
                try:
                    items.append(int(request.POST[key]))
                except: pass
        try:
            items = [DigitalItem.objects.get(id=i) for i in items]
            if len(items) > 0:
                controller = get_controller()
                from gchecky.model import *
                cart = controller.prepare_order(
                    order = checkout_shopping_cart_t(
                        shopping_cart=shopping_cart_t(
                            items = [
                                item_t(
                                    name=item.title,
                                    description=item.description,
                                    unit_price=price_t(
                                        value=item.price,
                                        currency=item.currency
                                    ),
                                    # TODO: Does it make sense to buy more than one of the same digital?
                                    quantity=1,
                                    merchant_item_id=item.id,
                                    digital_content=digital_content_t(
                                        description=item.brief,
                                        email_delivery=True,
                                        #TODO: get view url
                                        url = make_back_url(request,
                                                            '/digital/item/%d/' % (item.id,))
                                    )
                                )
                                for item in items
                            ],
                            merchant_private_data = 'digital'
                        ),
                        checkout_flow_support = checkout_flow_support_t(
                            edit_cart_url = None,
                            continue_shopping_url = CONTINUE_SHOPPING_URL,
                            tax_tables = tax_tables_t(
                                merchant_calculated = False,
                                default = default_tax_table_t(
                                    tax_rules = [
                                        default_tax_rule_t(
                                            shipping_taxed = True,
                                            rate = FRENCH_TAX,
                                            tax_area = tax_area_t(
                                                world_area = True
                                            )
                                        )
                                    ]
                                )
                            )
                        ),
                        request_initial_auth_details=False
                    )
                )
                total = 0.
                for item in items:
                    total += item.price
                total = '%s%.2f' % (items[0].currency, total)
                return render_to_response(template,
                                          {'items':items,
                                           'cart':cart,
                                           'total':total},
                                          request=request)
        except:
            raise
    # TODO: get view url
    return redirect_to(request=request, url=make_back_url(request, '/digital/order/'))

