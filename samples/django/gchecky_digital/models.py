from django.db import models
from gchecky.model import CURRENCIES
from gchecky_common.models import tuplize_for_django, FloatField

class DigitalItem(models.Model):
    """
    An item available for purchasing.
    """
    title       = models.CharField('Short title',
                                   max_length=255, blank=False)
    brief       = models.CharField('Brief description',
                                   max_length=255, blank=False)
    image        = models.ImageField('Picture',
                                     height_field='image_height',
                                     width_field='image_width',
                                     upload_to='digital/')
    description = models.TextField('Full description',
                                   blank=False)
    price       = FloatField('Price',
                             blank=False)
    currency    = models.CharField('Price currency',
                                   max_length=3, blank=False,
                                   choices=tuplize_for_django(CURRENCIES))

    class Meta:
        verbose_name = 'Digital item'

    class Admin:
        list_display = ('title', 'get_friendly_price', 'brief',)
        list_display_links = ('title', )
        list_filter = ('price', )
        search_fields = ['^title']

    def get_friendly_price(self):
        """Human friendly price of the item"""
        return '%s %.2f' % (self.currency, self.price)
    get_friendly_price.short_description = 'Item price'


