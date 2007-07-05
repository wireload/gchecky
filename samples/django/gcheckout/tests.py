import unittest
import random

from gcheckout import DjangoGController
from gcheckout import test_data
from gcheckout.models import Cart, Item, Message

class TestController(DjangoGController):
    def send_xml(self, msg):
        return test_data.REQUEST_RECEIVED
    
class TestControllerCase(unittest.TestCase):
    def setUp(self):
        self.controller = TestController('lala', 'blabla', True)
        self.order_id = str(random.randint(1000, 6000))

    def tearDown(self):
        cart = Cart.objects.get(google_id=self.order_id)
        for item in Item.objects.filter(cart=cart):
            item.delete()
        for msg in Message.objects.filter(cart=cart):
            msg.delete()

    def testSimpleOrder(self):
        self.assert_(self.controller.process(test_data.NEW_ORDER % (self.order_id,))
                     == test_data.OK, 'on_new_order')
        self.assert_(self.controller.process(test_data.ORDER_STATE_CHARGEABLE % (self.order_id,))
                     == test_data.OK, 'on_state_chargeable')
        self.assert_(self.controller.process(test_data.RISK_NOTIFICATION % (self.order_id,))
                     == test_data.OK, 'on_risk_notification')
        self.assert_(self.controller.process(test_data.ORDER_STATE_CHARGING % (self.order_id,))
                     == test_data.OK, 'on_state_charging')
        self.assert_(self.controller.process(test_data.CHARGE_AMOUNT_NOTIFICATION % (self.order_id,))
                     == test_data.OK, 'on_charge_amount_notif')

def allTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(TestControllerCase('testSimpleOrder'))
    return suite
 
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(allTestSuite)
