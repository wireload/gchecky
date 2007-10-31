import django
from django.db import models
from gchecky import model as gmodel

def list_for_django(VALUES):
    return tuple([(value,value) for value in VALUES])

if django.VERSION[0] >= 0 and django.VERSION[1] >= 97:
    float_field = models.FloatField(blank=False, default=0)
else:
    float_field = models.FloatField(max_digits=6, decimal_places=3, blank=False, default=0)

class Cart(models.Model):
    user_id   = models.CharField(maxlength=255, blank=True, null=True)
    google_id = models.CharField(maxlength=255, blank=False)
    xml       = models.TextField(blank=False)
    state     = models.CharField(maxlength=32, blank=False,
                                 choices=list_for_django(gmodel.FULFILLMENT_ORDER_STATE))
    payment   = models.CharField(maxlength=32, blank=False,
                                 choices=list_for_django(gmodel.FINANCIAL_ORDER_STATE))
    total           = float_field
    authorized      = float_field
    charges         = float_field
    charges_pending = float_field
    refunds         = float_field
    refunds_pending = float_field
    chargebacks     = float_field
    created   = models.DateTimeField(auto_now_add=True, blank=False)
    updated   = models.DateTimeField(auto_now=True, blank=False)

    class Admin:
        list_display = ['google_id', 'state', 'payment', 'created']

    def get_price(self):
        price = 0
        for i in self.items.all():
            price += i.price
        return price
    def get_rest(self):
        return self.get_price() - self.charged
    def __str__(self):
        return 'Cart \'%s\'' % (self.google_id,)

class Item(models.Model):
    cart        = models.ForeignKey(Cart, blank=False)
    name        = models.CharField(maxlength=255, blank=False, null=True)
    description = models.TextField(blank=False, null=True)
    price       = float_field
    currency    = models.CharField(maxlength=8, blank=False,
                                   choices=list_for_django(gmodel.CURRENCIES))
    quantity    = models.PositiveIntegerField(blank=False)
    merchant_id = models.CharField(maxlength=255, blank=False)
    merchant_data = models.TextField(blank=True, null=True)

    class Admin:
        pass

class Message(models.Model):
    serial_number = models.CharField(maxlength=128, blank=True, null=True)
    cart       = models.ForeignKey(Cart, blank=True, null=True)
    tag        = models.CharField(maxlength=16, default='', blank=True, null=False)
    input_xml  = models.TextField(blank=False)
    output_xml = models.TextField(blank=True, null=True)
    no_errors  = models.BooleanField(default=False, null=False)
    comment    = models.TextField(blank=True, null=True)
    created    = models.DateTimeField(auto_now_add=True, blank=False)
    updated    = models.DateTimeField(auto_now=True, blank=False)

    class Meta:
        ordering = ['-created']

    class Admin:
        list_display = ['no_errors', 'created', 'cart', 'tag', 'short_input', 'short_output', 'short_comment']
        list_display_links = ['created', 'short_input', 'tag', 'short_output', 'short_comment']
        fields = (
            (None, {
                'fields': ('no_errors', 'cart', 'input_xml', 'output_xml',
                           'comment',)
            }),
            ('Additional Information', {
                'fields': ('serial_number', 'created', 'updated')
            }),
        )

    def shorten(self, value, start=39, length=40):
        if value is None:
            return 'None'
        start = min(start, max(0, len(value) - length))
        return value[start:(start + length)]
    def short_input(self):   return self.shorten(self.input_xml)
    def short_output(self):  return self.shorten(self.output_xml)
    def short_comment(self): return self.shorten(self.comment, 0)

