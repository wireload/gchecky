from gchecky import model as gmodel
from gchecky_common.controller import get_controller

# The available donations list: [(amount, label)+]
AVAILABLE_DONATIONS=(
    (5.,   'Small donation'),
    (15.,  'Bandwidth costs'),
    (25.,  'Development support'),
    (50.,  'Important contribution'),
    (150., 'Generous gift'),
    (250., 'New server HDD'),
)

def prepare_simple_donation(controller, amount, title):
    # TODO: get view url
    CONTINUE_SHOPPING_URL = '%s/donation/continue' % ('http://demo.gchecky.com',)
    return controller.prepare_donation(
        order = gmodel.checkout_shopping_cart_t(
            shopping_cart = gmodel.shopping_cart_t(
                items = [gmodel.item_t(
                    name = title,
                    description = title,
                    unit_price = gmodel.price_t(
                        value = amount,
                        currency = controller.currency
                    ),
                    quantity = 1
                )],
                merchant_private_data = 'donation'
            ),
            checkout_flow_support = gmodel.checkout_flow_support_t(
                continue_shopping_url = CONTINUE_SHOPPING_URL
            )
        )
    )

def get_available_donations():
    controller = get_controller()
    return [{'cart':prepare_simple_donation(controller, amount, title),
             'amount':('%s %.2f' % (controller.currency, amount)),
             'title':title}
            for (amount, title) in AVAILABLE_DONATIONS]
