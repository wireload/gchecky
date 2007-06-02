from gchecky import model as gmodel
from gchecky.controller import Controller

def create_cart():
    """This method creates a sample shopping cart.
    The cart contain 2 apples and 5 oranges.
    Open checkout buyer is asked his phone number."""
    cart = gmodel.checkout_shopping_cart_t(
               shopping_cart = gmodel.shopping_cart_t(
                   items = [gmodel.item_t(
                                name = 'Apple',
                                description = 'A Golden Apple for You, my dear',
                                unit_price = gmodel.price_t(
                                    value=0.15, currency='GBP'
                                ),
                                quantity = 2
                            ),
                            gmodel.item_t(
                                name = 'Orange',
                                description = 'Vitamin C is the powa',
                                unit_price = gmodel.price_t(
                                    value=.07, currency='GBP'
                                ),
                                quantity = 5
                            )]
               ),
               checkout_flow_support = gmodel.checkout_flow_support_t(
                   request_buyer_phone_number = True
               )
           )
    return cart

def get_controller():
    """Creates a sample controller instance.
    In a real application the controller should be a singleton, and should
    be obtained accordingly."""
    controller = Controller(
                            vendor_id='my_vendro_ID_bla',
                            merchant_key='my_merchant_KEY_blabla'
                            )
    return controller

def cart_to_html(cart, controller):
    """This method transforms the information about a cart into
    html form data ready to be submitted to Google Checkout."""
    prepared = controller.prepare_order(cart)
    """prepared is an instance of html_order and has the follow fields:
        - cart - signed and base64 encoded XML representing the shopping cart
        - signature - base64 encoded signature (composed from your ID and KEY)
        - url - address where the cart should be sent
        - button - url of the Google Checkout button image
        - xml - the full XML represnting the cart
        - html - the complete html snippet for the GButton - a form with
                 the correct URL, hidden data - GButton is the only visible
                 input.
        """
    return prepared

if __name__ == '__main__':
    html = cart_to_html(
        create_cart(),
        get_controller()
    )
    print """
Google Button generated for your shopping cart:
Signature: %s
----------
Cart: %s
-----
Url: %s
----
Button image: %s
-------------
XML: %s
----
Full html: %s
----------

""" % (html.signature, html.cart, html.url, html.button, html.xml, html.html,)
