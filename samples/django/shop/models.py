from django.db import models

class Item(models.Model):
    title = models.CharField(maxlength=255, null=True, blank=False)
    description = models.TextField(null=True, blank=False)
    price = models.PositiveIntegerField(null=True, blank=False)
    weight = models.PositiveIntegerField(null=True, blank=False)
    class Admin:
        pass
    def __str__(self):
        return '%s - %d' % (self.title, self.price)

def values_to_choices(VALUES):
    # DJANGO ?? do we really need tuple() here?
    return tuple([(value,value) for value in VALUES])

class Package(models.Model):
    from gchecky.model import FINANCIAL_ORDER_STATE, FULFILLMENT_ORDER_STATE
    google_id = models.CharField(maxlength=255, blank=False)
    items = models.ManyToManyField(Item)
    state = models.CharField(maxlength=32, blank=False,
                             choices=values_to_choices(FULFILLMENT_ORDER_STATE))
    financial_state = models.CharField(maxlength=32, blank=False,
                                       choices=values_to_choices(FINANCIAL_ORDER_STATE))
    charged = models.FloatField(blank=True, null=False, default=0)
    when = models.DateTimeField(auto_now_add=True, blank=False)
    class Admin:
        list_display = ['google_id', 'state', 'financial_state', 'when']

    def get_price(self):
        price = 0
        for i in self.items.all():
            price += i.price
        return price
    def get_rest(self):
        return self.get_price() - self.charged
    def __str__(self):
        return '%s - %s item(s) - total of %d' % (self.when,
                                                  'self.items.count()',
                                                  self.get_price())

class Log(models.Model):
#    when = models.DateTimeField(auto_now_add=True, blank=False)
    input = models.TextField(blank=True, null=True)
    output = models.TextField(blank=True, null=True)
    order_id = models.TextField(maxlength=128, blank=True, null=False)
    code = models.CharField(maxlength=128, default='ok')
    error = models.TextField(blank=True, null=True, default='ok')
    class Admin:
        list_display = ['short_input', 'short_output', 'code', 'order_id', 'short_error']
    def short_input(self):
        return (self.input or '')[:64]
    def short_output(self):
        return (self.output or '')[:64]
    def short_error(self):
        return (self.error or '')[:64]
