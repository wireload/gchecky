from gchecky import model as gmodel
from gchecky.controller import Controller

# Google checkout information
# Gchecky demo sandbox account info:
GCHECKOUT_VENDOR_ID    = '618492934414682'
GCHECKOUT_MERCHANT_KEY = 't2mBWWytbm_JlIiLzaemoQ'
GCHECKOUT_IS_SANDBOX   = True # True for testing, False for production
GCHECKOUT_CURRENCY     = 'GBP' # 'USD' or 'GBP'

def create_cart():
    """
    Create a sample cart which will be then encoded into html for the sake
    of the sample.
    The cart contains 2 apples and 5 oranges. It also indicates to GC to prompt
    the user for a phone number.
    """
    cart = gmodel.checkout_shopping_cart_t(
        shopping_cart = gmodel.shopping_cart_t(
            items = [gmodel.item_t(
                name = 'Apple',
                description = 'A Golden Apple for You, my dear',
                unit_price = gmodel.price_t(
                    value=0.15,
                    currency = GCHECKOUT_CURRENCY
                ),
                quantity = 2
            ),
            gmodel.item_t(
                name = 'Orange',
                description = 'Vitamin C is the powa',
                unit_price = gmodel.price_t(
                    value=.07,
                    currency = GCHECKOUT_CURRENCY
                ),
                quantity = 5
            )]
        ),
        checkout_flow_support = gmodel.checkout_flow_support_t(
            # TODO: Does it really ask for the phone number?
            request_buyer_phone_number = True
        )
    )
    return cart

def get_controller():
    """
    Creates a sample controller instance.
    In a real application the controller should be a singleton, and should
    be obtained accordingly.
    """
    controller = Controller(vendor_id    = GCHECKOUT_VENDOR_ID,
                            merchant_key = GCHECKOUT_MERCHANT_KEY,
                            is_sandbox   = GCHECKOUT_IS_SANDBOX,
                            currency     = GCHECKOUT_CURRENCY)
    return controller

def cart_to_html(cart, controller):
    """
    This method transforms the information about a cart into
    html form data ready to be submitted to Google Checkout.
    @param cart The cart to encode and sign, before inserting into html.
    @param controller The system controller instance.
    @return: An instance of html_order and has the follow fields:
        - cart - signed and base64 encoded XML representing the shopping cart
        - signature - base64 encoded signature (composed from your ID and KEY)
        - url - address where the cart should be sent
        - button - url of the Google Checkout button image
        - xml - the full XML represnting the cart
        - html - the complete html snippet for the GButton - a form with
                 the correct URL, hidden data - GButton is the only visible
                 input.
    """
    prepared = controller.prepare_order(cart)
    return prepared

if __name__ == '__main__':
    html = cart_to_html(
        create_cart(),
        get_controller()
    )
    print """
Google Button generated for your shopping cart:
~~~~~~~~~~~~~~~~~~
Signature:
------------------
%s
~~~~~~~~~~~~~~~~~~
Cart:
------------------
%s
~~~~~~~~~~~~~~~~~~
Url:
------------------
%s
~~~~~~~~~~~~~~~~~~
Button image:
------------------
%s
~~~~~~~~~~~~~~~~~~
XML:
------------------
%s
~~~~~~~~~~~~~~~~~~
Full html:
------------------
%s        """ % (html.signature, html.cart, html.url, html.button, html.xml, html.html())
