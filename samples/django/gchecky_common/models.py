from django.db import models
#from django.db.models import permalink
from gchecky import model as gmodel

def tuplize_for_django(VALUES):
    """
    Convert a list of string constants into a tuple of 2-tuples as expected
    by Django.
    """
    return tuple([(value,value) for value in VALUES])

def FloatField(verbose_name=None, name=None,
               max_digits=6, decimal_places=3,
               *args, **kwargs):
    """
    A workaround helper for the incompatibility in FloatField parameter list
    introduced in version Django-0.97.
    """
    import django
    if django.VERSION[0] >= 0 and django.VERSION[1] >= 97:
        # The new version of django does not allow max_digits and decimal_places
        return models.FloatField(verbose_name, name, *args, **kwargs)
    else:
        # The old version does expect max_digits and decimal_places
        return models.FloatField(verbose_name, name,
                                 max_digits=max_digits,
                                 decimal_places=decimal_places,
                                 *args,
                                 **kwargs)

ORDER_NATURE=(
    ('digital', 'Digital'),
    ('donation', 'Donations'),
    ('normal', 'Normal'),
    ('unknown', 'Unrecognized')
)

class Order(models.Model):
    # The user owning the Order
    user_id         = models.CharField('User (owner)',
                                       max_length=255, blank=True, null=True)
    nature          = models.CharField('Order nature',
                                       max_length=64, blank=True, null=True,
                                       choices=ORDER_NATURE)
    # The id assigned to this order by google checkout
    google_id       = models.CharField('Google order id',
                                       max_length=255, blank=False)
    # The raw xml data representing this order cart (as it was sent to GC)
    cart_xml        = models.TextField('Order cart xml',
                                       blank=False)
    # The current order state as seen by GC, one of:
    # ('NEW', 'PROCESSING', 'DELIVERED', 'WILL_NOT_DELIVER')
    state           = models.CharField('Processing state',
                                       max_length=32, blank=False,
                                       choices=tuplize_for_django(gmodel.FULFILLMENT_ORDER_STATE))
    # Payment processing related fields: total, payed, pending, recurrent, etc.
    payment         = models.CharField('Payment state',
                                       max_length=32, blank=False,
                                       choices=tuplize_for_django(gmodel.FINANCIAL_ORDER_STATE))
    # The currency used
    currency        = models.CharField('Price currency',
                                       max_length=3, blank=False,
                                       choices=tuplize_for_django(gmodel.CURRENCIES))
    # Total amount to charge
    total           = FloatField('Total price',
                                 default=0.0)
    # The amount authorized (so far) by GC
    authorized      = FloatField('Amount authorized',
                                 default=0.0)
    # The total amount already charged
    charges         = FloatField('Amount charged',
                                 default=0.0)
    # The total amount requested to GC to be charged (but not yet charged)
    charges_pending = FloatField('Pending charges',
                                 default=0.0)
    # The total amount already refunded
    refunds         = FloatField('Amount refunded',
                                 default=0.0)
    # The total amount of refunds requested to GC (but not yet applied)
    refunds_pending = FloatField('Pending refunds',
                                 default=0.0)
    # TODO: what the heck is this field for?
    chargebacks     = FloatField('Chargebacks (?)',
                                 default=0.0)
    # Creation/modification timestamp
    created         = models.DateTimeField(auto_now_add=True, blank=False)
    updated         = models.DateTimeField(auto_now=True, blank=False)

    class Meta:
        verbose_name = 'Order'
        ordering = ('-updated',)

    class Admin:
        list_display = ('google_id', 'nature', 'created', 'get_friendly_total_price',
                        'state', 'payment')
        list_display_links = ('google_id', 'created', )
        list_filter = ('state', 'payment', )
        search_fields = ['^google_id', '^user_id']
        fields = ((None,          {'fields': ('nature',
                                              'total',
                                              'currency',
                                              'state',
                                              'payment')
                                  }),
                  ('Information', {'fields': ('user_id',
                                              'google_id',
                                              'cart_xml',),
                                   'classes':'wide',
                                   'description':'Order additional information'
                                  }),
                  ('Payment',     {'fields': ('total',
                                              'authorized',
                                              'charges',
                                              'charges_pending',
                                              'refunds',
                                              'refunds_pending',
                                              'chargebacks'),
                                   'classes':'collapse',
                                   'description':'Payment processing'
                                  }))

    def get_cart_total_price(self):
        """
        Calculate the full price of a cart as a sum of cart items
        """
        price = 0
        for p in self.purchase_set.all():
            price += p.price * p.quantity
        return price

    def get_friendly_total_price(self):
        """
        Return human friendly total price of the order.
        """
        return '%.2f %s' % (self.get_cart_total_price(), self.currency, )
    get_friendly_total_price.short_description = 'Order total'

    def __unicode__(self):
        return "Cart '%s'" % (self.google_id,)

    #@permalink
    def get_absolute_url(self):
        #TODO: It does not work with permalink - understand why it does not.
        #return ('gchecky_django.gchecky_common.views.order_details', None, {'order_id':self.id})
        return '/common/order/%d/' % (self.id,)

class Purchase(models.Model):
    """
    An item purchased as part of an order.
    Belongs to an order, contains all the order-related information.
    """
    order       = models.ForeignKey(Order, verbose_name='The purchase order',
                                    blank=False)
    item_xml    = models.TextField('Raw xml',
                                   blank=False)
    title       = models.CharField('Short title',
                                   max_length=64, blank=False)
    brief       = models.CharField('Brief description',
                                   max_length=255, blank=False)
    price       = FloatField('Price',
                             blank=False)
    currency    = models.CharField('Currency',
                                   max_length=3, blank=False,
                                   choices=tuplize_for_django(gmodel.CURRENCIES))
    quantity    = models.PositiveIntegerField('Quantity of item',
                                              blank=False)
    merchant_id = models.CharField('Attached ID',
                                   max_length=255, blank=True, null=True)
    merchant_data = models.TextField('Associated data',
                                     blank=True, null=True)

    class Admin:
        list_display = ('title', 'order',
                        'quantity', 'get_friendly_price',
                        'get_friendly_total_price',
                        'brief',)
        list_display_links = ('title', 'quantity', 'get_friendly_total_price',)

    class Meta:
        verbose_name = 'Purchase'

    def get_friendly_price(self):
        """Human friendly price of the item"""
        return '%.2f %s' % (self.price, self.currency,)
    get_friendly_price.short_description = 'Item price'

    def get_friendly_total_price(self):
        """Human friendly price of the whole purchase"""
        return '%.2f %s' % (self.price * self.quantity, self.currency,)
    get_friendly_total_price.short_description = 'Item price'


class Message(models.Model):
    order       = models.ForeignKey(Order, blank=True, null=True)
    serial      = models.CharField(max_length=255, blank=True, null=True)
    tag         = models.CharField(max_length=16, default='', blank=False, null=False)
    input_xml   = models.TextField(blank=True, null=True)
    output_xml  = models.TextField(blank=True, null=True)
    error       = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True) # TODO: ??
    created     = models.DateTimeField(auto_now_add=True, blank=False)
    updated     = models.DateTimeField(auto_now=True, blank=False)

    class Meta:
        ordering = ['-created']

    class Admin:
        list_display = ['no_errors', 'created', 'order', 'tag', 'short_input', 'short_output', 'error', 'short_description']
        list_display_links = ['created', 'short_input', 'tag', 'short_output']
        fields = (
            (None, {
                'fields': ('order', 'error', 'description',
                           'input_xml', 'output_xml',)
            }),
            ('Additional Information', {
                'fields': ('serial', 'tag')
            }),
            ('Timestamps', {
                'fields': ('created', 'updated')
            })
        )

    def short_input(self):
        return self.__shorten(self.input_xml)
    def short_output(self):
        return self.__shorten(self.output_xml)
    def short_description(self):
        return self.__shorten(self.description, 0)

    def no_errors(self):
        return self.error is None

    def __shorten(self, value, start=39, length=40):
        if value is None:
            return 'None'
        start = min(start, max(0, len(value) - length))
        return value[start:(start + length)]

