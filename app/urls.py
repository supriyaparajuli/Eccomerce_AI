from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from app import views as chat_views

from .views import RequestRefundView

urlpatterns = [
    path('base/', views.BASE, name='base'),
    path('', views.HOME, name='home'),
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
    path('createpost/', views.post_create, name='post-create'),
    path('post/<id>/update/', views.post_update, name='post-update'),
    path('post/<id>/delete/', views.post_delete, name='post-delete'),
    path('faq/', views.faq, name="faq"),
    # chatbot url
    path('faq/getResponse', views.getResponse, name='get_response'),

    path('request-refund/', RequestRefundView.as_view(), name="request-refund"),
    path('refunds/', views.refunds, name="refunds"),
    path('category/<int:category_id>/', views.categorization, name="category"),
    path('search_blog/', views.search_blog, name="search_blog"),
    path('delivery/', views.delivery, name="delivery"),
    path('delivery_update/<str:id>', views.delivery_update, name="delivery-update"),
    path('delivery_report/',views.delivery_report, name="delivery-report"),
    path('verify-otp/', views.verify_otp, name='verify_otp'),



#for C2C
    path('c2c_upload_product/',views.C2CUploadProduct,name="C2CUploadProduct"),
    path('c2c_product_list/',views.C2CProductList,name="C2CProductList"),
    #path('chat/',views.chat,name="chat"),
    path('friend/<id>/', views.detail, name="detail"),
    path('product-details/<int:product_id>/', views.product_details, name="product_details"),  # Add this line for product details
    path('my-products/', views.my_products, name='my_products'),


#FOr chat message
    path('send_friend_request/<int:receiver_id>/', views.send_friend_request, name='send_friend_request'),
    path('received_friend_requests/', views.received_friend_requests, name='received_friend_requests'),
    path('accept_friend_request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('reject_friend_request/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
   # path('chat/<int:friend_id>/', views.chat, name='chat'),
    path("chatsss/", chat_views.chatPage, name="chat-page"),
    path('product-details/<int:product_id>/', views.get_product_details, name='get_product_details'),


# for sending chat message 
    path('chat_room/<int:id>/', views.chat_room, name='chat_room'),
    path('send_message/<int:id>/', views.send_message, name='send_message'),
    path('khalti-request/', views.KhaltiRequestView.as_view(), name='khaltirequest'),
    path('khalti-verify/', views.KhaltiVerifyView.as_view(), name='khaltiverify'),
]
