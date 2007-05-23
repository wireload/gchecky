"""
Gchecky.model module describes the mapping between Google Checkout API (GC API)
XML messages (GC API XML Schema) and data classes.

This module uses L{gchecky.gxml} to automate much of the work so that
the actual logic is not cluttered with machinery.

The module code is simple and self-documenting. Please read the source code for
simple description of the data-structures. Note that it tries to follow exactly
the official GC API XML Schema.

All the comments for the GC API are at U{Google Chackout API documentation
<http://code.google.com/apis/checkout/developer/>}. Please consult it for any
questions about GC API functioning.

@author: etarassov
@version: $revision: $
@contact: gchecky at gmail
"""

from gchecky import gxml

class price_t(gxml.Node):
    value    = gxml.Double('', default=0)
    currency = gxml.String('@currency', values=('USD', 'GBP'))

class item_t(gxml.Node):
    name                = gxml.String('item-name')
    description         = gxml.String('item-description')
    unit_price          = gxml.Complex('unit-price', price_t)
    quantity            = gxml.Decimal('quantity')
    merchant_item_id           = gxml.String('merchant-item-id', required=False)
    merchant_private_item_data = gxml.Any('merchant-private-item-data', required=False)
    tax_table_selector         = gxml.String('tax-table-selector', required=False)

class tax_area_t(gxml.Node):
    """
    state        = gxml.String('us-state-area/state')
    zip_pattern  = gxml.String('us-zip-area/zip-pattern') # regex: [a-zA-Z0-9_]+\*? Note the optional asterisk
    country_area = gxml.String('us-country-area/country-area', values=('CONTINENTAL_48', 'FULL_50_STATES', 'ALL')) # enum('CONTINENTAL_48', 'FULL_50_STATES', 'ALL')

class areas_t(gxml.Node):
    states        = gxml.List('', gxml.String('us-state-area/state'))
    zip_patterns  = gxml.List('', gxml.String('us-zip-area/zip-pattern')) # regex: [a-zA-Z0-9_]+\*? Note the optional asterisk
    country_areas = gxml.List('', gxml.String('us-country-area/country-area'), values=('CONTINENTAL_48', 'FULL_50_STATES', 'ALL')) # enum('CONTINENTAL_48', 'FULL_50_STATES', 'ALL')

class tax_rule_t(gxml.Node):
    rate     = gxml.Double('rate', default=0.)
    tax_area = gxml.Complex('tax-area', tax_area_t)

class default_tax_rule_t(tax_rule_t):
    shipping_taxed = gxml.Boolean('@shipping-taxed', required=False)

class alternate_tax_rule_t(tax_rule_t):
    pass

class default_tax_table_t(gxml.Node):
    tax_rules = gxml.List('tax-rules', gxml.Complex('default-tax-rule', default_tax_rule_t))

class alternate_tax_table_t(gxml.Node):
    name                = gxml.String('@name')
    standalone          = gxml.Boolean('@standalone')
    alternate_tax_rules = gxml.List('alternate-tax-rules', gxml.Complex('alternate-tax-rule', alternate_tax_rule_t))

class tax_tables_t(gxml.Node):
    merchant_calculated = gxml.Boolean('merchant-calculated')
    default             = gxml.Complex('default-tax-table', default_tax_table_t)
    alternates          = gxml.List('alternate-tax-tables', gxml.Complex('alternate-tax-table', alternate_tax_table_t), required=False)

class merchant_calculations_t(gxml.Node):
    merchant_calculations_url = gxml.Url('merchant-calculations-url')
    accept_merchant_coupons   = gxml.Boolean('accept-merchant-coupons', required=False)
    accept_gift_certificates  = gxml.Boolean('accept-gift-certificates', required=False)

class shipping_option_t(gxml.Node):
    name = gxml.String('@name') # Attribute, len <= 255, not-empty
    price = gxml.Complex('price', price_t)
    allowed_areas  = gxml.Complex('shipping-restrictions/allowed-areas', areas_t, required=False)
    excluded_areas = gxml.Complex('shipping-restrictions/excluded-areas', areas_t, required=False)

class flat_rate_shipping_t(shipping_option_t):
    pass
class merchant_calculated_shipping_t(shipping_option_t):
    pass

class pickup_t(gxml.Node):
    name = gxml.String('@name')
    price = gxml.Decimal('')

class shipping_methods_t(gxml.Node):
    flat_rate_shippings           = gxml.List('', gxml.Complex('flat-rate-shipping', flat_rate_shipping_t)) # list of flat_rate_shipping_t
    merchant_calculated_shippings = gxml.List('', gxml.Complex('merchant-calculated-shipping', merchant_calculated_shipping_t)) # list of merchant_calculated_shipping_t
    pickups                       = gxml.List('', gxml.Complex('pickup', pickup_t)) # list of pickup_t

class checkout_flow_support_t(gxml.Node):
    edit_cart_url              = gxml.Url('edit-cart-url', required=False)         # optional, URL
    continue_shopping_url      = gxml.Url('continue-shopping-url', required=False) # optional, URL
    tax_tables                 = gxml.Complex('tax-tables', tax_tables_t, required=False) # optional, tax_tables_t
    shipping_methods           = gxml.Complex('shipping-methods', shipping_methods_t, required=False) # optional, shipping_methods_t
    merchant_calculations      = gxml.Complex('merchant-calculations', merchant_calculations_t, required=False) # optional, merchant_calculations_t
    request_buyer_phone_number = gxml.Boolean('request-buyer-phone-number', required=False) # optional, Boolean

class shopping_cart_t(gxml.Node):
    expiration            = gxml.Timestamp('cart-expiration/good-until-date', required=False)
    items                 = gxml.List('items', gxml.Complex('item', item_t))
    merchant_private_data = gxml.Any('merchant-private-data', required=False)

class checkout_shopping_cart_t(gxml.Document):
    tag_name = 'checkout-shopping-cart'
    shopping_cart                = gxml.Complex('shopping-cart', shopping_cart_t)
    checkout_flow_support        = gxml.Complex('checkout-flow-support/merchant-checkout-flow-support', checkout_flow_support_t)
    request_initial_auth_details = gxml.Boolean('order-processing-support/request-initial-auth-details', required=False)

class coupon_gift_adjustment_t(gxml.Node):
    code              = gxml.String('code')
    calculated_amount = gxml.Complex('calculated-amount', price_t, required=False)
    applied_amount    = gxml.Complex('applied-amount', price_t)
    message           = gxml.String('message', required=False)

class merchant_codes_t(gxml.Node):
    gift_certificate_adjustment = gxml.List('', gxml.Complex('gift-certificate-adjustment', coupon_gift_adjustment_t))
    coupon_adjustment           = gxml.List('', gxml.Complex('coupon-adjustment', coupon_gift_adjustment_t))

class shipping_adjustment_t(gxml.Node):
    shipping_name = gxml.String('shipping-name')
    shipping_cost = gxml.Complex('shipping-cost', price_t)

class shipping_t(gxml.Node):
    merchant_calculated_shipping_adjustment = gxml.Complex('merchant-calculated-shipping-adjustment', shipping_adjustment_t)
    flat_rate_shipping_adjustment           = gxml.Complex('flat-rate-shipping-adjustment', shipping_adjustment_t)
    pickup_shipping_adjustment              = gxml.Complex('pickup-shipping-adjustment', shipping_adjustment_t)
    methods                                 = gxml.List('', gxml.String('method/@name'))

class order_adjustment_t(gxml.Node):
    adjustment_total                = gxml.Complex('adjustment-total', price_t, required=False)
    merchant_calculation_successful = gxml.Boolean('merchant-calculation-successful', required=False)
    merchant_codes                  = gxml.Complex('merchant-codes', merchant_codes_t, required=False)
    shipping                        = gxml.Complex('shipping', shipping_t, required=False)
    total_tax                       = gxml.Complex('shipping', price_t, required=False)

class address_t(gxml.Node):
    address1     = gxml.String('address1')
    address2     = gxml.String('address2', required=False)
    city         = gxml.String('city')
    company_name = gxml.String('company-name', required=False)
    contact_name = gxml.String('contact-name', required=False)
    country_code = gxml.String('country-code')
    email        = gxml.Email('email', required=False)
    fax          = gxml.Phone('fax', required=False, empty=True)
    phone        = gxml.Phone('phone', required=False, empty=True)
    postal_code  = gxml.Zip('postal-code')
    region       = gxml.String('region', empty=True)

class buyer_billing_address_t(address_t):
    pass
class buyer_shipping_address_t(address_t):
    pass
class billing_address_t(address_t):
    # google docs do not say address_id is optional, but sandbox omits it.. :S bug?
    address_id = gxml.ID('@address-id', required=False)

class buyer_marketing_preferences_t(gxml.Node):
    email_allowed = gxml.Boolean('email-allowed')
    def read(self, node):
        return gxml.Node.read(self, node)
class abstract_notification_t(gxml.Document):
    tag_name = '-notification'
    serial_number       = gxml.ID('@serial-number')
    google_order_number = gxml.ID('google-order-number')
    timestamp                   = gxml.Timestamp('timestamp')

FINANCIAL_ORDER_STATE=('REVIEWING', 'CHARGEABLE', 'CHARGING', 'CHARGED', 'PAYMENT_DECLINED', 'CANCELLED', 'CANCELLED_BY_GOOGLE')
FULFILLMENT_ORDER_STATE=('NEW', 'PROCESSING', 'DELIVERED', 'WILL_NOT_DELIVER')

class new_order_notification_t(abstract_notification_t):
    tag_name = 'new-order-notification'
    buyer_billing_address       = gxml.Complex('buyer-billing-address', buyer_billing_address_t)
    buyer_id                    = gxml.Long('buyer-id')
    buyer_marketing_preferences = gxml.Complex('buyer-marketing-preferences', buyer_marketing_preferences_t)
    buyer_shipping_address      = gxml.Complex('buyer-shipping-address', buyer_shipping_address_t)
    financial_order_state       = gxml.String('financial-order-state', values=FINANCIAL_ORDER_STATE)
    fulfillment_order_state     = gxml.String('fulfillment-order-state', values=FULFILLMENT_ORDER_STATE)
    order_adjustment            = gxml.Complex('order-adjustment', order_adjustment_t)
    order_total                 = gxml.Complex('order-total', price_t)
    shopping_cart               = gxml.Complex('shopping-cart', shopping_cart_t)

class checkout_redirect_t(gxml.Document):
    tag_name = 'checkout-redirect'
    serial_number = gxml.ID('checkout-redirect')
    redirect_url  = gxml.Url('redirect-url')

class notification_acknowledgment_t(gxml.Document):
    tag_name = 'notification-acknowledgment'

class order_state_change_notification_t(abstract_notification_t):
    tag_name = 'order-state-change-notification'
    new_fulfillment_order_state      = gxml.String('new-fulfillment-order-state', values=FINANCIAL_ORDER_STATE)
    new_financial_order_state        = gxml.String('new-financial-order-state', values=FULFILLMENT_ORDER_STATE)
    previous_financial_order_state   = gxml.String('previous-financial-order-state', values=FINANCIAL_ORDER_STATE)
    previous_fulfillment_order_state = gxml.String('previous-fulfillment-order-state', values=FULFILLMENT_ORDER_STATE)
    reason                           = gxml.String('reason', required=False)

AVS_VALUES=('Y', 'P', 'A', 'N', 'U')
CVN_VALUES=('M', 'N', 'U', 'E')

class risk_information_t(gxml.Node):
    avs_response            = gxml.String('avs-response', values=AVS_VALUES)
    billing_address         = gxml.Complex('billing-address', billing_address_t)
    buyer_account_age       = gxml.Integer('buyer-account-age')
    cvn_response            = gxml.String('cvn-response', values=CVN_VALUES)
    eligible_for_protection = gxml.Boolean('eligible-for-protection')
    ip_address              = gxml.IP('ip-address')
    partial_cc_number       = gxml.String('partial-cc-number') # partial CC Number

class risk_information_notification_t(abstract_notification_t):
    tag_name = 'risk-information-notification'
    risk_information = gxml.Complex('risk-information', risk_information_t)

class abstract_order_t(gxml.Document):
    tag_name='-order'
    google_order_number = gxml.ID('@google-order-number')

class charge_order_t(abstract_order_t):
    tag_name = 'charge-order'
    amount = gxml.Complex('amount', price_t, required=False)

class refund_order_t(abstract_order_t):
    tag_name = 'refund-order'
    amount  = gxml.Complex('amount', price_t, required=False)
    comment = gxml.String('comment', required=False)
    reason  = gxml.String('reason')

class cancel_order_t(abstract_order_t):
    tag_name = 'cancel-order'
    comment = gxml.String('comment', required=False)
    reason  = gxml.String('reason')

class authorize_order_t(abstract_order_t):
    tag_name = 'authorize-order'

class process_order_t(abstract_order_t):
    tag_name = 'process-order'

class add_merchant_order_number_t(abstract_order_t):
    tag_name = 'add-merchant-order-number'
    merchant_order_number = gxml.String('merchant-order-number')

CARRIER_VALUES=('DHL', 'FedEx', 'UPS', 'USPS', 'Other')

class tracking_data_t(gxml.Node):
    carrier         = gxml.String('carrier', values=CARRIER_VALUES)
    tracking_number = gxml.String('tracking-number')

class deliver_order_t(abstract_order_t):
    tag_name='deliver-order'
    tracking_data = gxml.Complex('tracking-data', tracking_data_t, required=False)
    send_email    = gxml.Boolean('send-email', required=False)

class add_tracking_data_t(abstract_order_t):
    tag_name='add-tracking-data'
    tracking_data = gxml.Complex('tracking-data', tracking_data_t)

class send_buyer_message_t(abstract_order_t):
    tag_name='send-buyer-message'
    send_email = gxml.Boolean('send-email', required=False)
    message    = gxml.String('message')

class archive_order_t(abstract_order_t):
    tag_name='archive-order'

class unarchive_order_t(abstract_order_t):
    tag_name='unarchive-order'

class charge_amount_notification_t(abstract_notification_t):
    tag_name='charge-amount-notification'
    latest_charge_amount = gxml.Complex('latest-charge-amount', price_t)
    total_charge_amount  = gxml.Complex('total-charge-amount', price_t)

class refund_amount_notification_t(abstract_notification_t):
    tag_name='refund-amount-notification'
    latest_refund_amount = gxml.Complex('latest-refund-amount', price_t)
    total_refund_amount  = gxml.Complex('total-refund-amount', price_t)

class chargeback_amount_notification_t(abstract_notification_t):
    tag_name='chargeback-amount-notification'
    latest_chargeback_amount = gxml.Complex('latest-chargeback-amount', price_t)
    total_chargeback_amount  = gxml.Complex('total-chargeback-amount', price_t)

class authorization_amount_notification_t(abstract_notification_t):
    tag_name='authorization-amount-notification'
    authorization_amount          = gxml.Complex('authorization-amount', price_t)
    authorization_expiration_date = gxml.Timestamp('authorization-expiration-date')
    avs_response                  = gxml.String('avs-response', values=AVS_VALUES)
    cvn_response                  = gxml.String('cvn-response', values=CVN_VALUES)

class request_received_t(gxml.Document):
    tag_name = 'request-received'
    serial_number = gxml.ID('@serial-number')

class error_t(gxml.Document):
    tag_name = 'error'
    serial_number    = gxml.ID('@serial-number')
    error_message    = gxml.String('error-message')
    warning_messages = gxml.List('warning-messages',
                                 gxml.String('string'),
                                 required=False)

class diagnosis_t(gxml.Document):
    tag_name = 'diagnosis'
    input_xml = gxml.Any('input-xml')
    warnings  = gxml.List('warnings',
                          gxml.String('string'),
                          required=False)

