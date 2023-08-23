from decimal import Decimal
from django.db.models import Q, Count
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
import pandas as pd
import numpy as np
from django.http import JsonResponse
from cmath import sqrt
from django.http import JsonResponse
from django.views import View
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import redirect
from django.urls import reverse
from E_Commerce import settings
from django.utils import timezone
from .models import (
    Slider,
    Banner,
    Category,
    SubCategory,
    MainCategory,
    Product,
    Color,
    Brand,
    Cart,
    Coupon_Code,
    ReviewRating,
    Address,
    Order,
    Refund,
    Post,
    BlogCategory,
    Signup,
    Author,
    PostView,
    C2CUploadProductModel,
    FriendModel,
    ChatMessage,
    FriendRequest,
    Message,
    ChatRoom,
    CustomUser,
)
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Min
import stripe
from .forms import (
    ReviewForm,
    AddressForm,
    RefundForm,
    CommentForm,
    PostForm,
    C2CUploadProductForm,
    ChatMessageForm,
    OrderForm,
)
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.loader import render_to_string
import random
import string
from django.core.mail import EmailMessage, send_mail
import os
from twilio.rest import Client
import requests
# importing chatbot code
from app.chatbot_code.chat import get_chatbot_response
import requests

stripe.api_key = "sk_test_51Lhx5XHYuFGYD1XqC1CMimNsVB146a0a8jMYlSjbbAqKpQfYgY9vASBqVr06ux9sJo4JOYbkcs7z1rOSdmM7N5LD00nIJXkZxl"


def generate_otp():
    return str(random.randint(100000, 999999))


def get_author(user):
    qs = Author.objects.filter(user=user)
    if qs.exists():
        return qs[0]
    return None


def create_ref_code():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=10))


def get_category_count():
    queryset = Post.objects.values("categories__title").annotate(Count("categories"))
    return queryset


# Create your views here.
def BASE(request):
    return render(request, "base.html")


def HOME(request):
    

    sliders = Slider.objects.all().order_by("-id")[0:3]
    banners = Banner.objects.all().order_by("-id")[0:3]
    maincategory = MainCategory.objects.all().order_by("-id")

    product = Product.objects.filter(section__name="Top Deal of the Day")

    for prod in product:
        reviews = ReviewRating.objects.filter(product__id=prod.id)

    context = {
        "sliders": sliders,
        "banners": banners,
        "maincategory": maincategory,
        "product": product,
        "reviews": reviews,
    }
    return render(request, "Main/home.html", context)


def PRODUCT_DETAILS(request, slug):
    maincategory = MainCategory.objects.all().order_by("-id")

    product = Product.objects.filter(slug=slug)
    if product.exists():
        product = Product.objects.get(slug=slug)
    else:
        return redirect("404")

    reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        "product": product,
        "reviews": reviews,
        "maincategory": maincategory,
    }

    return render(request, "product/product_detail.html", context)


def Error404(request):
    return render(request, "errors/404.html")


def MY_ACCOUNT(request):
    maincategory = MainCategory.objects.all().order_by("-id")

    return render(request, "account/my-account.html", {"maincategory": maincategory})


# adding function for the product recommendation product
# adding function for the product recommendation product
def generateRecommendation(request):
    maincategory = MainCategory.objects.all().order_by("-id")

    productsAll = Product.objects.all()
    productRating = ReviewRating.objects.filter(rating__gte=4.0)
    x = []
    y = []
    A = []
    B = []
    C = []
    D = []
    params = {}
    # here we all data set into the Product Frame
    for item in productsAll:
        x = [
            item.id,
            item.featured_image,
            item.product_name,
            item.Product_information,
            item.Description,
            item.price,
            item.Categories,
        ]
        y += [x]

    products_df = pd.DataFrame(
        y,
        columns=[
            "productId",
            "featured_image",
            "product_name",
            "product_information",
            "Description",
            "price",
            "Categories",
        ],
    )

    # rating data frames
    print(productRating)

    for item in productRating:
        A = [item.user.id, item.product, item.rating]
        B += [A]

    rating_df = pd.DataFrame(B, columns=["userId", "productName", "rating"])
    print("Rating Data Frame")

    rating_df["userId"] = rating_df["userId"].astype(int)
    rating_df["productName"] = rating_df["productName"].astype(str)
    rating_df["rating"] = rating_df["rating"].astype(float)
    # .astype(np.float64)
    print(rating_df)

    if request.user.is_authenticated:
        userId = request.user.id
        userInput = ReviewRating.objects.select_related("product").filter(user=userId)

        print("user le review gareko kati wota", userInput)
        if userInput.count() == 0:
            userInput = None
            params = {}
            params["recommended"] = None
            return render(request, "product/product_recommendation.html", params)

        else:
            for item in userInput:
                C = [item.product.product_name, item.rating]
                D += [C]

            inputProduct = pd.DataFrame(D, columns=["product_name", "rating"])
            print("product by the user Data Frame")
            inputProduct["rating"] = inputProduct["rating"].astype(str).astype(float)
            print(inputProduct)

            # filtering out the product by title
            inputId = products_df[
                products_df["product_name"].isin(inputProduct["product_name"].tolist())
            ]
            inputProduct = pd.merge(inputId, inputProduct)

            print(inputProduct)

            # filtering out users that have watched product that the input has watched and storing it

            userSubset = rating_df[
                rating_df["productName"].isin(inputProduct["product_name"].tolist())
            ]
            print(userSubset.head())

            userSubsetGroup = userSubset.groupby(["userId"])

            userSubsetGroup = sorted(
                userSubsetGroup, key=lambda x: len(x[1]), reverse=True
            )

            print(userSubsetGroup[0:])

            userSubsetGroup = userSubsetGroup[0:]

            pearsonCorrelationDict = {}

            for name, group in userSubsetGroup:
                group = group.sort_values(by="userId")
                inputProduct = inputProduct.sort_values(by="product_name")

                nRatings = len(group)

                temp_df = inputProduct[
                    inputProduct["product_name"].isin(group["productName"].tolist())
                ]

                tempRatingList = temp_df["rating"].tolist()

                tempGroupList = group["rating"].tolist()

                # Now let's calculate the pearson correlation between two users, so called, x and y
                Sxx = sum([i**2 for i in tempRatingList]) - pow(
                    sum(tempRatingList), 2
                ) / float(nRatings)
                Syy = sum([i**2 for i in tempGroupList]) - pow(
                    sum(tempGroupList), 2
                ) / float(nRatings)
                Sxy = sum(i * j for i, j in zip(tempRatingList, tempGroupList)) - sum(
                    tempRatingList
                ) * sum(tempGroupList) / float(nRatings)

                # If the denominator is different than zero, then divide, else, 0 correlation.
                if Sxx != 0 and Syy != 0:
                    pearsonCorrelationDict[name] = Sxy / sqrt(Sxx * Syy)
                else:
                    pearsonCorrelationDict[name] = 0

            print(pearsonCorrelationDict.items())
            try:
                pearsonDF = pd.DataFrame.from_dict(
                    pearsonCorrelationDict, orient="index"
                )
                pearsonDF.columns = ["similarityIndex"]
                pearsonDF["userId"] = pearsonDF.index
                pearsonDF.index = range(len(pearsonDF))
                print(pearsonDF.head())

                topUsers = pearsonDF.sort_values(by="similarityIndex", ascending=False)[
                    0:
                ]
                print(topUsers.head())

                topUserRating = topUsers.merge(
                    rating_df, left_on="userId", right_on="userId", how="inner"
                )
                topUserRating.head()

                # Multiplies the similarity by the user's ratings
                topUserRating["weightedRating"] = (
                    topUserRating["similarityIndex"] * topUserRating["rating"]
                )
                topUserRating.head()

                # Applies a sum to the topUsers after grouping it up by userId
                tempTopUsersRating = topUserRating.groupby("productName").sum()[
                    ["similarityIndex", "weightedRating"]
                ]
                tempTopUsersRating.columns = [
                    "sum_similarityIndex",
                    "sum_weightedRating",
                ]
                tempTopUsersRating.head()

                # creates an empty dataframe
                recommendation_df = pd.DataFrame()

                # now we take the weighted average
                recommendation_df["weighted average recommendation score"] = (
                    tempTopUsersRating["sum_weightedRating"]
                    / tempTopUsersRating["sum_similarityIndex"]
                )
                recommendation_df["productName"] = tempTopUsersRating.index
                recommendation_df.head()

                recommendation_df = recommendation_df.sort_values(
                    by="weighted average recommendation score", ascending=False
                )
                recommender = products_df.loc[
                    products_df["product_name"].isin(
                        recommendation_df.head(5)["productName"].tolist()
                    )
                ]
                print(recommender)
                print("helllooooo")
                params = {}
                params["recommended"] = recommender.to_dict("records")
                params["maincategory"] = maincategory

                return render(request, "product/product_recommendation.html", params)
            except Exception as e:
                print(e)

                userInput = None
                params = {}
                params["recommended"] = None
                params["maincategory"] = maincategory
                return render(request, "product/product_recommendation.html", params)

    return render(request, "product/product_recommendation.html", params)


def REGISTER(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        delivery = request.POST.get("delivery")
        phone = request.POST.get("phone")
        dob = request.POST.get("dateField")
        if delivery == "on":
            delivery = True
        else:
            delivery = False

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("login")

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email id already exists")
            return redirect("login")
        # Generate and send OTP
        otp = generate_otp()
        email_subject = "OTP Verification"
        email_message = f"Your OTP is: {otp}"
        send_mail(email_subject, email_message, settings.EMAIL_HOST_USER, [email])

        # Store the user data and OTP in the session for validation
        request.session["user_data"] = {
            "username": username,
            "email": email,
            "password": password,
            "firstname": firstname,
            "lastname": lastname,
            "phone_number": phone,
            "date_of_birth": dob,
            "otp": otp,
        }
        messages.info(request, "Please enter the OTP sent to your email.")
        return redirect("verify_otp")

    return render(request, "account/my-account.html")


# Create a new view to handle OTP verification
def verify_otp(request):
    if request.method == "POST":
        user_data = request.session.get("user_data")
        if user_data:
            entered_otp = request.POST.get("otp")
            if entered_otp == user_data["otp"]:
                # OTP is correct, save the user in the database
                user = CustomUser(
                    username=user_data["username"],
                    email=user_data["email"],
                    first_name=user_data["firstname"],
                    last_name=user_data["lastname"],
                    phone_number=user_data["phone_number"],
                    date_of_birth=user_data["date_of_birth"],
                )
                user.set_password(user_data["password"])
                user.save()
                messages.success(request, "Profile Is Successfully Registered!")
                del request.session[
                    "user_data"
                ]  # Remove the user data from the session
                return redirect("login")
            else:
                messages.error(request, "Invalid OTP. Please try again.")
                return redirect("verify_otp")
        else:
            messages.error(request, "Session expired. Please register again.")
            return redirect("register")

    return render(request, "otp/verify-otp.html")


def LOGIN(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            return redirect("home")

        else:
            messages.error(request, "Email and Password are Invalid !")
            return redirect("login")


@login_required(login_url="/accounts/login/")
def PROFILE(request):
    maincategory = MainCategory.objects.all().order_by("-id")

    return render(request, "profile/profile.html", {"maincategory": maincategory})


@login_required(login_url="/accounts/login/")
def PROFILE_UPDATE(request):
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        user_id = request.user.id

        user = CustomUser.objects.get(id=user_id)
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email

        if password != None and password != "":
            user.set_password(password)
        user.save()
        messages.success(request, "Profile Is Successfully Updated !")

        return redirect("profile")


def CONTACT(request):
    maincategory = MainCategory.objects.all().order_by("-id")

    return render(request, "Main/contact.html", {"maincategory": maincategory})


def PRODUCT(request):
    category = Category.objects.all()
    product = Product.objects.all()
    color = Color.objects.all()
    brand = Brand.objects.all
    maincategory = MainCategory.objects.all().order_by("-id")
    min_price = Product.objects.all().aggregate(Min("price"))
    max_price = Product.objects.all().aggregate(Max("price"))
    ColorID = request.GET.get("colorID")
    FilterPrice = request.GET.get("FilterPrice")
    total_data = Product.objects.count()

    for prod in product:
        reviews = ReviewRating.objects.filter(product__id=prod.id)

    if FilterPrice:
        Int_FilterPrice = int(FilterPrice)
        paged_products = Product.objects.filter(price__lte=Int_FilterPrice)

    elif ColorID:
        paged_products = Product.objects.filter(color=ColorID)

    else:
        paged_products = Product.objects.all()

    context = {
        "category": category,
        "product": paged_products,
        "min_price": min_price,
        "max_price": max_price,
        "FilterPrice": FilterPrice,
        "color": color,
        "brand": brand,
        "reviews": reviews,
        "total_data": total_data,
        "maincategory": maincategory,
    }

    return render(request, "product/product.html", context)


def filter_data(request):
    categories = request.GET.getlist("category[]")
    print(categories)
    brands = request.GET.getlist("brand[]")
    colors = request.GET.getlist("color[]")

    allProducts = Product.objects.all().order_by("id").distinct()
    if len(categories) > 0:
        allProducts = allProducts.filter(Categories__id__in=categories).distinct()
    if len(brands) > 0:
        allProducts = allProducts.filter(Brand__id__in=brands).distinct()
    if len(colors) > 0:
        allProducts = allProducts.filter(color__id__in=colors).distinct()
    t = render_to_string("ajax/product.html", {"product": allProducts})

    return JsonResponse({"data": t})


def load_more_data(request):
    offset = int(request.GET["offset"])
    limit = int(request.GET["limit"])
    data = Product.objects.all().order_by("id")[offset : offset + limit]
    t = render_to_string("ajax/product.html", {"product": data})
    return JsonResponse({"data": t})


@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get("prod_id")
    product = get_object_or_404(Product, id=product_id)

    # Check whether the Product is already in Cart or Not
    item_already_in_cart = Cart.objects.filter(product=product_id, user=user)
    if item_already_in_cart:
        cp = get_object_or_404(Cart, product=product_id, user=user)
        cp.quantity += 1
        cp.save()
    else:
        Cart(user=user, product=product).save()

    return redirect("cart")


@login_required
def cart(request):
    maincategory = MainCategory.objects.all().order_by("-id")

    # logic of cart
    user = request.user
    cart_products = Cart.objects.filter(user=user)

    # Display Total on Cart Page
    tax = Decimal(50)
    amount = Decimal(0)
    shipping_amount = Decimal(20)
    # using list comprehension to calculate total amount based on quantity and shipping
    cp = [p for p in Cart.objects.all() if p.user == user]
    if cp:
        for p in cp:
            temp_amount = p.quantity * p.product.price
            amount += temp_amount
    context = {
        "cart_products": cart_products,
        "amount": amount,
        "tax": tax,
        "shipping_amount": shipping_amount,
        "total_amount": int(amount + shipping_amount + tax),
        "maincategory": maincategory,
    }
    return render(request, "cart/cart.html", context)


@login_required
def remove_cart(request, cart_id):
    if request.method == "GET":
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
        messages.success(request, "Product removed from Cart.")
    return redirect("cart")


@login_required
def plus_cart(request):
    if request.method == "GET":
        prod_id = request.GET["prod_id"]
        c = get_object_or_404(Cart, id=prod_id)
        c.quantity += 1
        c.save()

        user = request.user
        # Display Total on Cart Page
        tax = Decimal(50)
        amount = Decimal(0)
        shipping_amount = Decimal(20)
        # using list comprehension to calculate total amount based on quantity and shipping
        cp = [p for p in Cart.objects.all() if p.user == user]
        for p in cp:
            temp_amount = p.quantity * p.product.price
            amount += temp_amount
        data = {
            "unit_total_price": c.unit_total_price,
            "quantity": c.quantity,
            "amount": amount,
            "tax": tax,
            "shipping_amount": shipping_amount,
            "total_amount": int(amount + shipping_amount + tax),
        }
    return JsonResponse(data)


@login_required
def minus_cart(request):
    if request.method == "GET":
        prod_id = request.GET["prod_id"]
        c = get_object_or_404(Cart, id=prod_id)
        c.quantity -= 1
        c.save()

        user = request.user
        # Display Total on Cart Page
        tax = Decimal(50)
        amount = Decimal(0)
        shipping_amount = Decimal(20)
        # using list comprehension to calculate total amount based on quantity and shipping
        cp = [p for p in Cart.objects.all() if p.user == user]
        for p in cp:
            temp_amount = p.quantity * p.product.price
            amount += temp_amount
        data = {
            "unit_total_price": c.unit_total_price,
            "quantity": c.quantity,
            "amount": amount,
            "tax": tax,
            "shipping_amount": shipping_amount,
            "total_amount": int(amount + shipping_amount + tax),
        }
    return JsonResponse(data)


def charge(request):
    amount = int(request.POST.get("total_amount"))

    print(amount)
    customer = None
    if request.method == "POST":
        print("Data:", request.POST)
        try:
            customer = stripe.Customer.create(
                email=request.POST["email"],
                name=request.POST["username"],
                source=request.POST["stripeToken"],
            )
            charge = stripe.Charge.create(
                customer=customer,
                amount=amount * 100,
                currency="npr",
                description="Payment",
            )
        except (
            stripe.error.RateLimitError,
            stripe.error.StripeError,
            stripe.error.AuthenticationError,
            stripe.error.CardError,
        ) as error:
            return redirect("failure")

    user = request.user
    address_id = request.POST.get("address")
    print(address_id)
    address = get_object_or_404(Address, id=address_id)

    # Get all the products of User in Cart
    cart = Cart.objects.filter(user=user)
    for c in cart:
        # Saving all the products from Cart to Order
        Order(
            user=user,
            address=address,
            product=c.product,
            price=c.product.price,
            unit_total_price=c.unit_total_price,
            ref_code=create_ref_code(),
            quantity=c.quantity,
        ).save()
        # And Deleting from Cart
        c.delete()
    return redirect(reverse("success", args=[amount]))


def failure(request):
    return render(request, "cart/failure.html")


def successMsg(request, args):
    amount = args
    template = render_to_string(
        "cart/email_template.html", {"name": request.user.username, "amount": amount}
    )
    email = EmailMessage(
        "Thanks for purchasing the eCommerce products !",
        template,
        settings.EMAIL_HOST_USER,
        [request.user.email],
    )
    email.content_subtype = "html"
    email.fail_silently = False
    email.send()

    return render(request, "cart/success.html", {"amount": amount})


def submit_review(request, product_id):
    url = request.META.get("HTTP_REFERER")

    if request.method == "POST":
        try:
            reviews = ReviewRating.objects.get(
                user__id=request.user.id, product__id=product_id
            )
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, "Thank you! Your review has been updated.")
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data["subject"]
                data.rating = form.cleaned_data["rating"]
                data.review = form.cleaned_data["review"]
                data.ip = request.META.get("REMOTE_ADDR")
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, "Thank you! Your review has been submitted.")
                return redirect(url)


def search(request):
    maincategory = MainCategory.objects.all().order_by("-id")
    category = Category.objects.all()
    product = Product.objects.all()
    color = Color.objects.all()
    brand = Brand.objects.all
    min_price = Product.objects.all().aggregate(Min("price"))
    max_price = Product.objects.all().aggregate(Max("price"))
    ColorID = request.GET.get("colorID")
    FilterPrice = request.GET.get("FilterPrice")
    for prod in product:
        reviews = ReviewRating.objects.filter(product__id=prod.id)

    if FilterPrice:
        Int_FilterPrice = int(FilterPrice)
        product = Product.objects.filter(price__lte=Int_FilterPrice)

    elif ColorID:
        product = Product.objects.filter(color=ColorID)

    else:
        query = request.GET["query"]
        multiple_queries = (
            Q(product_name__icontains=query)
            | Q(Categories__name__icontains=query)
            | Q(Brand__name__icontains=query)
        )
        product = Product.objects.filter(multiple_queries)

    context = {
        "category": category,
        "product": product,
        "min_price": min_price,
        "max_price": max_price,
        "FilterPrice": FilterPrice,
        "color": color,
        "brand": brand,
        "reviews": reviews,
        "maincategory": maincategory,
    }

    return render(request, "product/search.html", context)


def place_order(request):
    maincategory = MainCategory.objects.all().order_by("-id")
    coupon = Coupon_Code.objects.all()
    coupon.discount = 0
    valid_coupon = None
    invalid_coupon = None
    if request.method == "GET":
        coupon_code = request.GET.get("coupon_code")
        if coupon_code:
            try:
                coupon = Coupon_Code.objects.get(code=coupon_code)
                valid_coupon = "Are Applicable on Current Order ! "
            except:
                invalid_coupon = "Invalid Coupon Code !"

    # logic of cart
    user = request.user
    cart_products = Cart.objects.filter(user=user)

    # Display Total on Cart Page
    tax = Decimal(50)
    amount = Decimal(0)
    shipping_amount = Decimal(20)
    # using list comprehension to calculate total amount based on quantity and shipping
    cp = [p for p in Cart.objects.all() if p.user == user]
    if cp:
        for p in cp:
            temp_amount = p.quantity * p.product.price
            amount += temp_amount
    addresses = Address.objects.filter(user=user)

    context = {
        "cart_products": cart_products,
        "amount": amount,
        "tax": tax,
        "shipping_amount": shipping_amount,
        "total_amount": int(
            float(
                round(
                    (amount + shipping_amount + tax)
                    - amount * Decimal(coupon.discount / 100),
                    1,
                )
            )
        ),
        "coupon": coupon,
        "valid_coupon": valid_coupon,
        "invalid_coupon": invalid_coupon,
        "addresses": addresses,
        "maincategory": maincategory,
    }
    return render(request, "checkout/checkout.html", context)


@login_required
def profile(request):
    maincategory = MainCategory.objects.all().order_by("-id")
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(
        request,
        "profile/profile_detail.html",
        {"addresses": addresses, "orders": orders, "maincategory": maincategory},
    )


@method_decorator(login_required, name="dispatch")
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        maincategory = MainCategory.objects.all().order_by("-id")

        return render(
            request,
            "profile/add_address.html",
            {"form": form, "maincategory": maincategory},
        )

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user = request.user
            locality = form.cleaned_data["locality"]
            city = form.cleaned_data["city"]
            state = form.cleaned_data["state"]
            reg = Address(user=user, locality=locality, city=city, state=state)
            reg.save()
            messages.success(request, "New Address Added Successfully.")
        return redirect("profile_detail")


@login_required
def orders(request):
    all_orders = Order.objects.filter(user=request.user).order_by("-ordered_date")
    maincategory = MainCategory.objects.all().order_by("-id")

    return render(
        request,
        "checkout/orders.html",
        {"orders": all_orders, "maincategory": maincategory},
    )


def blog(request):
    maincategory = MainCategory.objects.all().order_by("-id")
    blogcategories = BlogCategory.objects.all()
    category_count = get_category_count()
    print(category_count)
    blogsidelist = Post.objects.all().order_by("-timestamp")[:4]
    bloglist = Post.objects.filter(featured=True)
    paginator = Paginator(bloglist, 2)
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    if request.method == "POST":
        email = request.POST.get("email")
        signup_object = Signup()
        signup_object.email = email
        signup_object.save()

    context = {
        "bloglist": paginated_queryset,
        "blogcategories": blogcategories,
        "maincategory": maincategory,
        "page_request_var": page_request_var,
        "blogsidelist": blogsidelist,
        "category_count": category_count,
    }

    return render(request, "blog/blog.html", context)


def blog_details(request, id):
    maincategory = MainCategory.objects.all().order_by("-id")
    blogsidelist = Post.objects.all().order_by("-timestamp")[:4]
    post = get_object_or_404(Post, id=id)
    category_count = get_category_count()
    if request.user.is_authenticated:
        PostView.objects.get_or_create(user=request.user, post=post)

    form = CommentForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.instance.user = request.user
            form.instance.post = post
            form.save()
            return redirect(reverse("blog_detail", kwargs={"id": post.pk}))

    context = {
        "post": post,
        "maincategory": maincategory,
        "blogsidelist": blogsidelist,
        "category_count": category_count,
        "form": form,
    }

    return render(request, "blog/blog_details.html", context)


@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Address removed.")
    return redirect("profile_detail")


def faq(request):
    maincategory = MainCategory.objects.all().order_by("-id")
    return render(request, "Main/faq.html", {"maincategory": maincategory})


@method_decorator(login_required, name="dispatch")
class RequestRefundView(View):
    def get(self, request):
        maincategory = MainCategory.objects.all().order_by("-id")

        form = RefundForm()
        context = {"form": form, "maincategory": maincategory}
        return render(request, "refund/request_refund.html", context)

    def post(self, request):
        form = RefundForm(request.POST, request.FILES)
        if form.is_valid():
            ref_code = form.cleaned_data.get("ref_code")
            message = form.cleaned_data.get("message")
            email = form.cleaned_data.get("email")
            image = form.cleaned_data.get("image")

            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund

                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.Image = image
                refund.save()

                messages.success(
                    request,
                    "Your request was received. You will shortly receive an email if refund is successfully granted.",
                )
                return redirect("request-refund")

            except ObjectDoesNotExist:
                messages.error(request, "This order does not exist.")
                return redirect("request-refund")

        else:
            return HttpResponse("Form Failed, Go back")


@login_required
def refunds(request):
    refunds = Order.objects.filter(
        Q(user=request.user),
        (Q(refund_requested=True) & Q(refund_granted=False))
        | (Q(refund_requested=False) & Q(refund_granted=True)),
    )

    refunds_sent = Order.objects.filter(
        user=request.user, refund_requested=False, refund_granted=True, email_sent=False
    )
    if refunds_sent:
        sum = 0

        for refund in refunds_sent:
            refund.email_sent = True
            refund.save()
            sum = refund.product.price + sum

        template = render_to_string(
            "refund/refund_email.html",
            {"name": request.user.username, "sum": sum, "refunds": refunds_sent},
        )
        email = EmailMessage(
            "Your order has been refunded !",
            template,
            settings.EMAIL_HOST_USER,
            [request.user.email],
        )

        email.fail_silently = False
        email.send()

    maincategory = MainCategory.objects.all().order_by("-id")

    context = {
        "orders": refunds,
        "maincategory": maincategory,
    }

    return render(request, "refund/refunds.html", context)


def categorization(request, category_id):
    maincategory = MainCategory.objects.all().order_by("-id")

    items_of_maincategory = Product.objects.filter(
        Categories__main_category__id=category_id
    )
    context = {
        "items": items_of_maincategory,
        "maincategory": maincategory,
    }

    return render(request, "product/categorization.html", context)


def search_blog(request):
    queryset = Post.objects.all()
    query = request.GET.get("q")
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) | Q(overview__icontains=query)
        ).distinct()

    context = {
        "queryset": queryset,
    }
    return render(request, "blog/search_results.html", context)


# chatbot responses
def getResponse(request):
    userMessage = request.GET.get("userMessage")
    prediction = get_chatbot_response(userMessage)
    response = {"response": str(prediction)}
    return JsonResponse(response)


def post_create(request):
    form = PostForm(request.POST or None, request.FILES or None)
    author = get_author(request.user)

    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author

            form.save()
            return redirect(reverse("blog_detail", kwargs={"id": form.instance.id}))
    context = {"form": form}
    return render(request, "blog/post_create.html", context)


def post_update(request, id):
    post = get_object_or_404(Post, id=id)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    author = get_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse("blog_detail", kwargs={"id": form.instance.id}))
    context = {"form": form}
    return render(request, "blog/post_create.html", context)


def post_delete(request, id):
    post = get_object_or_404(Post, id=id)
    post.delete()
    return redirect(reverse("blog"))


# for C2C
def C2CUploadProduct(request):
    if request.method == "POST":
        form = C2CUploadProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.crcProductUploadId = request.POST.get('crcProductUploadId')
            product.approved = False  # Set the approved field to False
            product.date = timezone.now()  # Set the date field manually
            product.save()
            return redirect('my_products')
    form = C2CUploadProductForm()
    return render(request, "c2c/C2CUploadProductForm.html", {'form': form})


# for product list

#for product list 
@login_required
def product_details(request, product_id):
    product = C2CUploadProductModel.objects.get(productId=product_id)
    user = CustomUser.objects.get(id=product.crcProductUploadId)
    product.username = user.username

    context = {
        'product': product,
    }
    return render(request, 'c2c/product-details.html', context)


@login_required
def C2CProductList(request):
    c2cUploadData = C2CUploadProductModel.objects.filter(approved=True)
    for x in c2cUploadData:
        user = CustomUser.objects.get(id=x.crcProductUploadId)
        x.username = user.username
        if user != request.user:
            chat_room = ChatRoom.objects.filter(
                participant1=request.user,
                participant2=user
            ).first()

            if chat_room:
                x.chat_room_link = reverse('chat_room', args=[chat_room.id])
            else:
                x.chat_room_link = None

            friend_request = FriendRequest.objects.filter(
                sender=request.user,
                receiver=user
            ).first()

            if friend_request and friend_request.status == 'accepted':
                x.show_friend_request = False
            else:
                x.show_friend_request = True

    context = {
        'c2cUploadData': c2cUploadData,
    }
    return render(request, 'c2c/C2CProductList.html', context)

@login_required
def my_products(request):
    c2cUploadData = C2CUploadProductModel.objects.filter(crcProductUploadId=request.user.id)

    for x in c2cUploadData:
        user = CustomUser.objects.get(id=x.crcProductUploadId)
        x.username = user.username

    context = {
        'c2cUploadData': c2cUploadData,
    }
    return render(request, 'c2c/my_products.html', context)



#  here we show the product details
def get_product_details(request, product_id):
    try:
        product = get_object_or_404(C2CUploadProductModel, productId=product_id)
        product_details = {
            "name": product.productName,
            "description": product.productDescription,
            "image_url": product.image.url
            # Add other product details as needed
        }
        return JsonResponse(product_details)
    except C2CUploadProductModel.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)


# def chat(request):
#     friendList = User.objects.all()

#     return render(request,'chat/chat.html',{'friendList':friendList})


def detail(request, id):
    friendDetail = CustomUser.objects.get(id=id)
    user = request.user.id
    profile = CustomUser.objects.get(id=id)
    chats = ChatMessage.objects.all()
    form = ChatMessageForm()
    if request.method == "POST":
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            chat_message = form.save(commit=False)
            chat_message.msg_sender = user
            chat_message.msg_receiver = profile
            chat_message.save()
            return redirect("detail", pk=CustomUser.id)

    return render(
        request, "chat/detail.html", {"friendDetail": friendDetail, "form": form}
    )


# For making chat app
@login_required
def send_friend_request(request, receiver_id):
    if request.method == "POST":
        try:
            receiver = CustomUser.objects.get(id=receiver_id)
            users = CustomUser.objects.all()

            for user in users:
                pass
                print("users name", user.username)
                print("users id", user.id)

            friend_request = FriendRequest(
                sender=request.user, receiver=receiver, status="pending"
            )
            friend_request.save()
            return JsonResponse({"success": True})
        except Exception as e:
            print(str(e))
    return JsonResponse({"success": False})


@login_required
def accept_friend_request(request, request_id):
    if request.method == "POST":
        try:
            friend_request = FriendRequest.objects.get(id=request_id)
            friend_request.status = "accepted"
            friend_request.save()

            # Check if a chat room already exists for the participants
            chat_room = ChatRoom.objects.filter(
                participant1=friend_request.sender, participant2=friend_request.receiver
            ).first()

            # If chat room doesn't exist, create a new one
            if not chat_room:
                chat_room = ChatRoom.objects.create(
                    participant1=friend_request.sender,
                    participant2=friend_request.receiver,
                )

            # Add the chat room to participants' chat room lists
            friend_request.sender.chat_rooms_as_participant1.add(chat_room)
            friend_request.receiver.chat_rooms_as_participant2.add(chat_room)

            # Set chat room link in the friend request object
            chat_room_link = reverse("chat_room", args=[chat_room.id])
            friend_request.chat_room_link = chat_room_link
            friend_request.save()

            # Notify the users about the friend request acceptance
            messages.success(request, "Friend request accepted!")

            # Redirect both sender and receiver to the chat room page
            redirect_url = "/chat_room/" + str(chat_room.id) + "/"
            return JsonResponse({"success": True, "redirect_url": redirect_url})
        except FriendRequest.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": "Friend request does not exist."}
            )
    return JsonResponse({"success": False, "error": "Invalid request method."})


def received_friend_requests(request):
    user = request.user
    received_requests = FriendRequest.objects.filter(receiver=user)
    return render(
        request,
        "c2c/received_friend_requests.html",
        {"received_requests": received_requests},
    )


@login_required
def reject_friend_request(request, request_id):
    if request.method == "POST":
        try:
            friend_request = FriendRequest.objects.get(id=request_id)
            friend_request.delete()
            return JsonResponse({"success": True})
        except FriendRequest.DoesNotExist:
            pass

    return JsonResponse({"success": False})


def received_friend_requests(request):
    user = request.user
    received_requests = FriendRequest.objects.filter(receiver=user)
    return render(
        request,
        "c2c/received_friend_requests.html",
        {"received_requests": received_requests},
    )


@login_required
def chat_room(request, id):
    chat_room = get_object_or_404(ChatRoom, id=id)

    # Check if the user is a participant in the chat room
    if (
        chat_room.participant1 != request.user
        and chat_room.participant2 != request.user
    ):
        return HttpResponseForbidden("You are not a participant in this chat room.")

    messages = Message.objects.filter(chat_room=chat_room).order_by("timestamp")
    return render(
        request, "chat/chat_room.html", {"chat_room": chat_room, "messages": messages}
    )


@login_required
def send_message(request, id, message=None):
    if request.method == "POST":
        content = request.POST.get("content")
        chat_room = get_object_or_404(ChatRoom, id=id)

        # Determine the receiver based on the chat room participants
        if chat_room.participant1 == request.user:
            receiver = chat_room.participant2
        else:
            receiver = chat_room.participant1

        if message is None:
            message = content

        message = Message(
            sender=request.user, receiver=receiver, content=message, chat_room=chat_room
        )
        message.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


# @login_required
# def chat(request, friend_id):
#     friend = User.objects.get(id=friend_id)
#     messages = Message.objects.filter(
#         (models.Q(sender=request.user) & models.Q(receiver=friend)) |
#         (models.Q(sender=friend) & models.Q(receiver=request.user))
#     ).order_by('timestamp')
#     return render(request, 'chat.html', {'friend': friend, 'messages': messages})


def chatPage(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login-user")
    context = {}
    return render(request, "chat/chatPage.html", context)


class KhaltiRequestView(View):
    def post(self, request):
        amount = int(request.POST.get("total_amount"))
        user = request.user
        address_id = request.POST.get("address")
        print(address_id)
        address = get_object_or_404(Address, id=address_id)

        # Get all the products of User in Cart
        cart = Cart.objects.filter(user=user)
        for c in cart:
            # Saving all the products from Cart to Order
            Order(
                user=user,
                address=address,
                product=c.product,
                price=c.product.price,
                unit_total_price=c.unit_total_price,
                ref_code=create_ref_code(),
                quantity=c.quantity,
            ).save()
            # And Deleting from Cart
            c.delete()
            
        



        context = {
            'amount' : amount
        }

        return render(request, 'khalti/khaltirequest.html', context)
    


class KhaltiVerifyView(View):
    def get(self, request):
        token = request.GET.get('token')
        amount = request.GET.get('amount')
        print("Amount is", amount)
        print("Token is", token)
        url = "https://khalti.com/api/v2/payment/verify/"

        payload = {
        'token': token,
        'amount': amount
        }

        headers = {
        'Authorization': 'Key test_secret_key_953f493ab03745eea15dfd470576db59'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response, "Successful response")
        resp_obj = response.json()
        print(resp_obj)
        if resp_obj.get("idx"):
            success = True
        else:
            success = False    
        data = {
            "success": success,
            "Client Verified": True
        }
        account_sid = "ACca6b2dd2f80dfc614461015f442fd2d8"
        auth_token = "18d630fd41e6d8ddbdf3cfaea4a7a1db"
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body="Hi there, your payment of khalti was successful",
            from_="+15419334578",
            to="+9779861388667",
        )

        print("message sms sent successfully")
        print(message.sid)

        return JsonResponse(data)
