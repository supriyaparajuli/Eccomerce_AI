from django import template
import math

from app.models import Cart, Address

register = template.Library()


@register.simple_tag
def call_sellprice(price, Discount):
    if Discount is None or Discount == 0:
        return price

    sellprice = price
    sellprice = price - (price * Discount / 100)
    return math.floor(sellprice)


@register.simple_tag
def progress_bar(total_quantity, Availabiity):
    progress_bar = Availabiity
    progress_bar = Availabiity * (100 / total_quantity)
    return math.floor(progress_bar)


@register.simple_tag
def cart_total(user):
    cart_item = Cart.objects.filter(user=user)
    cart_total = cart_item.count()
    return cart_total


@register.simple_tag
def address_total(user):
    address = Address.objects.filter(user=user)
    address_total = address.count()
    return address_total
