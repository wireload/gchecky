from gchecky import model as gmodel
from gchecky.controller import Controller as GController
from models import Item, Package

# custom version of controller
class MyController(GController):
    # Helper -- dumps the recieved info
    def _dump_notification_info(self, str, notification, order_id):
        message = """NOTIFICATION: %s (order_id: %s):
%s
<<<<<<<<<<<<<<<<""" % (str, order_id, notification.toxml())
        print message
        return message
    # Override gcontroller handlers to dump the info about notifications
    def on_new_order(self, notification, order_id):
        items = [Item.objects.get(id=gitem.merchant_item_id)
                 for gitem in notification.shopping_cart.items]
        if not items:
            raise Exception('No known items in the shopping cart')
        # Some safety checks
        total = 0
        for item in items:
            total += item.price
        if total != notification.order_total.value:
            raise Exception('The order_total does not match: got (%f) from gcheckout, but it should be (%f).'
                            % (notification.order_total.value, total))
        package = Package()
        package.google_id = order_id
        package.save()
        package.items = items
        package.state = notification.fulfillment_order_state
        package.financial_state = notification.financial_order_state
        package.save()

    def on_order_state_change(self, notification, order_id):
        package = Package.objects.get(google_id=order_id)
        # GCHECK ?? When an order is partially charged its 'new-state' goes into
        # 'CHARGED'. But when it is charged again the 'previous-state' is
        # 'CHARGEABLE', which does not match 'CHARGED'.
#        if package.state != notification.previous_fulfillment_order_state:
#            raise Exception('Fulfillment order state does not match! "%s" vs "%s"'
#                            % (notification.previous_fulfillment_order_state, package.state))
#        if package.financial_state != notification.previous_financial_order_state:
#            raise Exception('Fulfillment order state does not match! "%s" vs "%s"'
#                            % (notification.previous_financial_order_state,
#                               package.financial_state))
        package.state = notification.new_fulfillment_order_state
        package.financial_state = notification.new_financial_order_state
        package.save()
    def on_authorization_amount(self, notification, order_id):
        package = Package.objects.get(google_id=order_id)
        return 'we are not interested in this message'
    def on_risk_information(self, notification, order_id):
        # Just discard the info we are not interested in.
        # But check for the package to be valid anyway
        package = Package.objects.get(google_id=order_id)
        return 'we are not interested in this message'
    def on_charge_amount(self, notification, order_id):
        package = Package.objects.get(google_id=order_id)
        assert notification.total_charge_amount.value == (notification.latest_charge_amount.value + package.charged)
        package.charged = notification.total_charge_amount.value
        package.save()
    def on_refund_amount(self, notification, order_id):
        # TODO !! do the same as in on_charge_amount
        return 'we are not interested in this message'
    def on_chargeback_amount(self, notification, order_id):
        raise Exception("Not yet implemented")

def createController():
    from settings import gcheckout_vendor_id, gcheckout_merchant_key
    return MyController(vendor_id    = gcheckout_vendor_id,
                        merchant_key = gcheckout_merchant_key,
                        is_sandbox   = True)

controller = createController()


def prepare_items(items):
    order = gmodel.checkout_shopping_cart_t(
        shopping_cart = gmodel.shopping_cart_t(items = [
            gmodel.item_t(merchant_item_id = str(item.id),
                          name             = item.title,
                          description      = item.description,
                          unit_price       = gmodel.price_t(value    = item.price,
                                                            currency = 'GBP'),
                          quantity = 1)
            for item in items
            ]),
        checkout_flow_support          = gmodel.checkout_flow_support_t(
            continue_shopping_url      = 'http://gchecky.com/shop/',
            request_buyer_phone_number = False))
    return controller.prepare_order(order)

def handle_notification(input_xml):
    return controller.recieve(input_xml)

