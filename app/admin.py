from django.contrib import admin
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from E_Commerce import settings
from .models import *


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_granted=True, refund_requested=False)


make_refund_accepted.short_description = 'Update orders to refund granted'


class Product_Images(admin.TabularInline):
    model = Product_Image


class Additional_Informations(admin.TabularInline):
    model = Additional_Information


class Product_Admin(admin.ModelAdmin):
    inlines = (Product_Images, Additional_Informations)
    list_display = ('product_name', 'Categories', 'section', 'price', 'color', 'Brand')
    list_editable = ('Categories', 'section', 'color', 'Brand')


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'product', 'quantity', 'price', 'status', 'ordered_date', 'refund_requested', 'refund_granted',)
    list_editable = ('status',)
    list_filter = ('status', 'ordered_date', 'refund_requested', 'refund_granted',)
    list_per_page = 20
    search_fields = ('user', 'product')
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'locality', 'city', 'state')
    list_filter = ('city', 'state')
    list_per_page = 10
    search_fields = ('locality', 'city', 'state')


class RefundAdmin(admin.ModelAdmin):
    list_display = ('order', 'accepted', 'email',)


# Register your models here.
admin.site.register(Slider)
admin.site.register(Banner)
admin.site.register(MainCategory)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Section)
admin.site.register(Product, Product_Admin)
admin.site.register(Product_Image)
admin.site.register(Additional_Information)
admin.site.register(Color)
admin.site.register(Brand)
admin.site.register(Cart)
admin.site.register(Coupon_Code)
admin.site.register(ReviewRating)
admin.site.register(Order, OrderAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Refund, RefundAdmin)
admin.site.register(Author)
admin.site.register(BlogCategory)
admin.site.register(Post)
admin.site.register(Signup)
admin.site.register(Comment)
admin.site.register(Rating)
admin.site.register(PostView)
