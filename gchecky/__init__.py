"""
Gchecky provides an abstraction layer between google checkout API and user code.

It wraps-up the clumsy Level 2 integration API into a human-friendly form.

All the interaction between Checkout API and user code is handled by
the library, which includes the following topics:
  - generating/validating/parsing XML messages for/from Google Checkout API
  - transforming the xml DOM trees into a human-friendly structures
    almost word-by-word following the official specification from google.
  - does the technical low-level tasks such as generating authentication
    token from user vendor_id and merchant_key etc.
  - parses Google Checkout API notification messages and runs
    the corresponding hook methods.

Intergration of the library consists of four phases:
  1. gather your account settings such as your vendor_id, merchant_key,
     your local currency symbol (ATM either 'USD' or 'GBP')
  2. create a unique instance of L{gchecky.ControllerLevel_2} class by
     subclassing it. Provide custom implementation to the abstract methods.
     Basically all you need is to define your reaction to various API
     notifications (see step 5 for details).
  3. set up a separate background thread for sending requests to
     U{Google Checkout API <http://code.google.com/apis/checkout/developer/index.html#order_processing_api>}.
  4. set up a web-handler at a publicly accessible url. Refer to the 
     U{Google Checkout Notification API
     <http://code.google.com/apis/checkout/developer/index.html#handling_notifications>}.
     But instead of processing incoming XML messages yourself, it should
     pass the incoming request text to your customized instance of
     L{gchecky.ControllerLevel_2} (to L{gchecky.ControllerLevel_2.recieve}).
  5. Provide your local order-processing system integration by overriding
     abstract methods of your custom instance of L{gchecky.ControllerLevel_2}
     (see steps 2 and 3).
     Basically you will need to store Orders in your custom order-processing
     system, update it state every time you receive a notification from
     Google Checkout Notification API (notifications correspond to abstract
     Controller.on_XXX methods). Plus in the step 3 you will need to scan your
     Order list and perform actions on those orders which are ready for the
     further processing (charging, refunding, delivering etc.) 

@author: etarassov
@version: $Revision $
@contact: gchecky at gmail
"""
