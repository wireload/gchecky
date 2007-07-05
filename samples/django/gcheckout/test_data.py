NEW_ORDER = """<?xml version="1.0" encoding="UTF-8"?>
<new-order-notification xmlns="http://checkout.google.com/schema/2" serial-number="221799950156128-00001-7">
  <timestamp>2007-07-04T21:22:06.000Z</timestamp>
  <shopping-cart>
    <items>
      <item>
        <quantity>1</quantity>
        <unit-price currency="GBP">7.5</unit-price>
        <merchant-item-id>3</merchant-item-id>
        <item-name>Card 7.5</item-name>
        <item-description>A card of 7.5 euros. Luli-luli.</item-description>
        <merchant-private-item-data>Any</merchant-private-item-data>
      </item>
    </items>
  </shopping-cart>
  <order-adjustment>
    <merchant-codes />
    <total-tax currency="GBP">1.13</total-tax>
    <shipping>
      <pickup-shipping-adjustment>
        <shipping-name>Our Website</shipping-name>
        <shipping-cost currency="GBP">0.0</shipping-cost>
      </pickup-shipping-adjustment>
    </shipping>
    <adjustment-total currency="GBP">1.13</adjustment-total>
  </order-adjustment>
  <google-order-number>%s</google-order-number>
  <buyer-shipping-address>
    <contact-name>Evgeniy Tarassov</contact-name>
    <company-name>TT soul</company-name>
    <email>Evgeniy-bu07ikfu7ag@sandbox.google.com</email>
    <phone></phone>
    <fax></fax>
    <address1>7 Carmine St #</address1>
    <address2></address2>
    <country-code>US</country-code>
    <city>New-York</city>
    <region>NY</region>
    <postal-code>10014</postal-code>
  </buyer-shipping-address>
  <buyer-billing-address>
    <contact-name>Some One</contact-name>
    <company-name></company-name>
    <email>Evgeniy-bu07ikfu7ag@sandbox.google.com</email>
    <phone></phone>
    <fax></fax>
    <address1>1, rue Somerue</address1>
    <address2></address2>
    <country-code>FR</country-code>
    <city>Paris</city>
    <region></region>
    <postal-code>75001</postal-code>
  </buyer-billing-address>
  <buyer-marketing-preferences>
    <email-allowed>false</email-allowed>
  </buyer-marketing-preferences>
  <order-total currency="GBP">8.63</order-total>
  <fulfillment-order-state>NEW</fulfillment-order-state>
  <financial-order-state>REVIEWING</financial-order-state>
  <buyer-id>270642604806238</buyer-id>
</new-order-notification>
"""

OK = """<?xml version='1.0' encoding='UTF-8'?>
<ok xmlns='http://checkout.google.com/schema/2'/>
"""

ORDER_STATE_CHARGEABLE = """<?xml version="1.0" encoding="UTF-8"?>
<order-state-change-notification xmlns="http://checkout.google.com/schema/2" serial-number="221799950156128-00005-1">
  <timestamp>2007-07-04T21:22:10.000Z</timestamp>
  <google-order-number>%s</google-order-number>
  <new-fulfillment-order-state>NEW</new-fulfillment-order-state>
  <new-financial-order-state>CHARGEABLE</new-financial-order-state>
  <previous-fulfillment-order-state>NEW</previous-fulfillment-order-state>
  <previous-financial-order-state>REVIEWING</previous-financial-order-state>
</order-state-change-notification>
"""

ORDER_STATE_CHARGING = """<?xml version="1.0" encoding="UTF-8"?>
<order-state-change-notification xmlns="http://checkout.google.com/schema/2" serial-number="900343549837133-00007-1">
  <timestamp>2007-07-04T22:23:09.000Z</timestamp>
  <google-order-number>%s</google-order-number>
  <new-fulfillment-order-state>NEW</new-fulfillment-order-state>
  <new-financial-order-state>CHARGING</new-financial-order-state>
  <previous-fulfillment-order-state>NEW</previous-fulfillment-order-state>
  <previous-financial-order-state>CHARGEABLE</previous-financial-order-state>
</order-state-change-notification>
"""

CHARGE_AMOUNT_NOTIFICATION = """<?xml version="1.0" encoding="UTF-8"?>
<charge-amount-notification xmlns="http://checkout.google.com/schema/2" serial-number="900343549837133-00008-2">
  <timestamp>2007-07-04T22:24:34.000Z</timestamp>
  <google-order-number>%s</google-order-number>
  <latest-charge-amount currency="GBP">17.25</latest-charge-amount>
  <total-charge-amount currency="GBP">17.25</total-charge-amount>
</charge-amount-notification>
"""

REQUEST_RECEIVED = """<?xml version="1.0" encoding="UTF-8"?>
<request-received xmlns="http://checkout.google.com/schema/2"
    serial-number="58ea39d3-025b-4d52-a697-418f0be74bf9"/>"""


RISK_NOTIFICATION = """<?xml version="1.0" encoding="UTF-8"?>
<risk-information-notification xmlns="http://checkout.google.com/schema/2" serial-number="900343549837133-00005-5">
  <timestamp>2007-07-04T22:23:08.000Z</timestamp>
  <google-order-number>%s</google-order-number>
  <risk-information>
    <billing-address>
      <contact-name>Some One</contact-name>
      <company-name></company-name>
      <email>Evgeniy-bu07ikfu7ag@sandbox.google.com</email>
      <phone></phone>
      <fax></fax>
      <address1>1, rue Somerue</address1>
      <address2></address2>
      <country-code>FR</country-code>
      <city>Paris</city>
      <region></region>
      <postal-code>75001</postal-code>
    </billing-address>
    <ip-address>10.0.0.1</ip-address>
    <avs-response>Y</avs-response>
    <cvn-response>U</cvn-response>
    <eligible-for-protection>true</eligible-for-protection>
    <partial-cc-number>1111</partial-cc-number>
    <buyer-account-age>136</buyer-account-age>
  </risk-information>
</risk-information-notification>
"""




