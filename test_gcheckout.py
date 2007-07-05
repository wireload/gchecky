from shop.gcheckout import *

messages = {
'new_order':"""<?xml version="1.0" encoding="UTF-8"?>
<new-order-notification xmlns="http://checkout.google.com/schema/2" serial-number="6237fc4a-a99a-4847-8467-79a40207a8c3">
  <timestamp>2007-05-18T14:00:02.000Z</timestamp>
  <shopping-cart>
    <items>
      <item>
        <quantity>1</quantity>
        <unit-price currency="GBP">1599.0</unit-price>
        <merchant-item-id>3</merchant-item-id>
        <item-name>Notebook</item-name>
        <item-description>Toshiba notebook</item-description>
      </item>
    </items>
  </shopping-cart>
  <order-adjustment>
    <merchant-codes />
    <total-tax currency="GBP">0.0</total-tax>
    <adjustment-total currency="GBP">0.0</adjustment-total>
  </order-adjustment>
  <google-order-number>166958488006047</google-order-number>
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
  <order-total currency="GBP">1599.0</order-total>
  <fulfillment-order-state>NEW</fulfillment-order-state>
  <financial-order-state>REVIEWING</financial-order-state>
  <buyer-id>270642604806238</buyer-id>
</new-order-notification>"""
}

def test_message(message):
#    try:
        out = gcontroller.recieve(message)
#    except Exception, error:
#        print 'ERROR:'
#        print '-----------------------'
#        print message
#        print '-----------------------'
#        import traceback
#        print 'Exception:' + error
#        #print traceback.format_exc()
#        print '======================='

test_message(messages['new_order'])
