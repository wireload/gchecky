new_order_notification_xml="""<?xml version="1.0" encoding="UTF-8"?>
<new-order-notification xmlns="http://checkout.google.com/schema/2" serial-number="2a260406-a426-4877-838b-0596d6a568a4">
  <timestamp>2007-04-23T23:34:14.000Z</timestamp>
  <shopping-cart>
    <items>
      <item>
        <quantity>3</quantity>
        <unit-price currency="GBP">1.55</unit-price>
        <item-name>Test_Item_1</item-name>
        <item-description>Test Item 1 for testing purposes.</item-description>
      </item>
      <item>
        <quantity>2</quantity>
        <unit-price currency="GBP">5.23</unit-price>
        <item-name>Test_Item_2</item-name>
        <item-description>Test Item 2 for testing purposes.</item-description>
      </item>
    </items>
  </shopping-cart>
  <order-adjustment>
    <merchant-codes />
    <total-tax currency="GBP">0.0</total-tax>
    <adjustment-total currency="GBP">0.0</adjustment-total>
  </order-adjustment>
  <google-order-number>874003160521390</google-order-number>
  <buyer-shipping-address>
    <contact-name>Evgeniy Tarassov</contact-name>
    <company-name>AA soul</company-name>
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
  <order-total currency="GBP">15.11</order-total>
  <fulfillment-order-state>NEW</fulfillment-order-state>
  <financial-order-state>REVIEWING</financial-order-state>
  <buyer-id>270642604806238</buyer-id>
</new-order-notification>
"""

order_state_change_notification_xml="""<?xml version="1.0" encoding="UTF-8"?>
<order-state-change-notification xmlns="http://checkout.google.com/schema/2" serial-number="b3381921-9e8d-4bc1-a214-0e3e133d1754">
  <timestamp>2007-04-23T23:34:15.000Z</timestamp>
  <google-order-number>874003160521390</google-order-number>
  <new-fulfillment-order-state>NEW</new-fulfillment-order-state>
  <new-financial-order-state>CHARGEABLE</new-financial-order-state>
  <previous-fulfillment-order-state>NEW</previous-fulfillment-order-state>
  <previous-financial-order-state>REVIEWING</previous-financial-order-state>
</order-state-change-notification>
"""

risk_information_notification_xml="""<?xml version="1.0" encoding="UTF-8"?>
<risk-information-notification xmlns="http://checkout.google.com/schema/2" serial-number="d7a898d5-b5a7-4f2f-a527-72b6c6539e58">
  <timestamp>2007-04-23T23:34:15.000Z</timestamp>
  <google-order-number>874003160521390</google-order-number>
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
    <ip-address>81.57.142.122</ip-address>
    <eligible-for-protection>true</eligible-for-protection>
    <avs-response>U</avs-response>
    <cvn-response>U</cvn-response>
    <partial-cc-number>1111</partial-cc-number>
    <buyer-account-age>64</buyer-account-age>
  </risk-information>
</risk-information-notification>
"""

authorization_amount_notification_xml="""<?xml version="1.0" encoding="UTF-8"?>
<authorization-amount-notification xmlns="http://checkout.google.com/schema/2" serial-number="b24ff45c-e32a-47ba-8616-a2059a0efaa0">
  <timestamp>2007-04-23T23:34:15.000Z</timestamp>
  <avs-response>U</avs-response>
  <cvn-response>U</cvn-response>
  <google-order-number>874003160521390</google-order-number>
  <authorization-amount currency="GBP">15.11</authorization-amount>
  <authorization-expiration-date>2007-04-30T23:34:14.000Z</authorization-expiration-date>
</authorization-amount-notification>
"""

