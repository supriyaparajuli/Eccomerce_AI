from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

from .views import RequestRefundView

urlpatterns = [
    path('base/', views.BASE, name='base'),
    path('', views.HOME, name='home'),
    path('about/', views.ABOUT, name='about'),
    path('productRecommend/', views.generateRecommendation, name='logic'),
    path('contact/', views.CONTACT, name='contact'),
    path('product/<slug:slug>', views.PRODUCT_DETAILS, name='product_detail'),
    path('product/', views.PRODUCT, name='product'),
    path('filter-data', views.filter_data, name='filter_data'),
    path('404/', views.Error404, name='404'),
    path('account/myaccount/', views.MY_ACCOUNT, name='my_account'),
    path('account/register/', views.REGISTER, name='handleregister'),
    path('account/login/', views.LOGIN, name='handlelogin'),
    path('account/profile', views.PROFILE, name='profile'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('account/profile/update', views.PROFILE_UPDATE, name='profile_update'),
    path('add-to-cart/', views.add_to_cart, name="add-to-cart"),
    path('remove-cart/<int:cart_id>/', views.remove_cart, name="remove-cart"),
    path('pluscart', views.plus_cart, name="plus_cart"),
    path('minuscart', views.minus_cart, name="minus-cart"),
    path('cart/', views.cart, name="cart"),
    path('charge/', views.charge, name="charge"),
    path('success/<str:args>/', views.successMsg, name="success"),
    path('submit_review/<int:product_id>/', views.submit_review, name="submit_review"),
    path('search/', views.search, name="search"),
    path('load-more-data', views.load_more_data, name="load_more_data"),
    path('place_order/', views.place_order, name="place_order"),
    path('orders/', views.orders, name="orders"),
    path('accounts/profile_detail/', views.profile, name="profile_detail"),
    path('accounts/add-address/', views.AddressView.as_view(), name="add-address"),
    path('accounts/remove-address/<int:id>/', views.remove_address, name="remove-address"),
    path('failure/', views.failure, name="failure"),
    path('blog/', views.blog, name="blog"),
    path('blog_details/<id>/', views.blog_details, name="blog_detail"),
    path('faq/', views.faq, name="faq"),
    path('request-refund/', RequestRefundView.as_view(), name="request-refund"),
    path('refunds/', views.refunds, name="refunds"),
    path('category/<int:category_id>/', views.categorization, name="category"),
    path('search_blog/', views.search_blog, name="search_blog"),
]
