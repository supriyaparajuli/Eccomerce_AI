from decimal import Decimal
from django.db.models import Q, Count
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
import pandas as pd
import numpy as np
from cmath import sqrt
from django.views import View

from E_Commerce import settings
from .models import Slider, Banner, Category, SubCategory, MainCategory, Product, Color, Brand, Cart, Coupon_Code, \
    ReviewRating, Address, Order, Refund, Post, BlogCategory, Signup
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Min
import stripe
from .forms import ReviewForm, AddressForm, RefundForm, CommentForm
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.template.loader import render_to_string
import random
import string
from django.core.mail import EmailMessage

stripe.api_key = "sk_test_51Lhx5XHYuFGYD1XqC1CMimNsVB146a0a8jMYlSjbbAqKpQfYgY9vASBqVr06ux9sJo4JOYbkcs7z1rOSdmM7N5LD00nIJXkZxl"


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))


def get_category_count():
    queryset = Post.objects.values('categories__title').annotate(Count('categories'))
    return queryset


# Create your views here.
def BASE(request):
    return render(request, 'base.html')


def HOME(request):
    sliders = Slider.objects.all().order_by('-id')[0:3]
    banners = Banner.objects.all().order_by('-id')[0:3]
    maincategory = MainCategory.objects.all().order_by('-id')

    product = Product.objects.filter(section__name="Top Deal of the Day")

    for prod in product:
        reviews = ReviewRating.objects.filter(product__id=prod.id)

    context = {
        'sliders': sliders,
        'banners': banners,
        'maincategory': maincategory,
        'product': product,
        'reviews': reviews,
    }
    return render(request, 'Main/home.html', context)


def PRODUCT_DETAILS(request, slug):
    maincategory = MainCategory.objects.all().order_by('-id')

    product = Product.objects.filter(slug=slug)
    if product.exists():
        product = Product.objects.get(slug=slug)
    else:
        return redirect('404')

    reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        'product': product,
        'reviews': reviews,
        'maincategory': maincategory,
    }

    return render(request, 'product/product_detail.html', context)


def Error404(request):
    return render(request, 'errors/404.html')


def MY_ACCOUNT(request):
    maincategory = MainCategory.objects.all().order_by('-id')

    return render(request, 'account/my-account.html', {'maincategory': maincategory})

# adding function for the product recommendation product
def generateRecommendation(request):
    productsAll= Product.objects.all()
    productRating=ReviewRating.objects.all()
    x=[] 
    y=[]
    A=[]
    B=[]
    C=[]
    D=[]
    # here we all data set into the Product Frame
    for item in productsAll:
        x=[item.id,item.featured_image,item.product_name,item.Product_information,item.Description,item.price,item.Categories]
        y+=[x]

    products_df=pd.DataFrame(y,columns=['productId','featured_image','product_name','product_information','Description','price','Categories'])
    print("Product Data Frame")
    print(products_df)
    # rating data frames
    print(productRating)

    for item in productRating:
        A= [item.user.id,item.product,item.rating]
        B+=[A]

    rating_df = pd.DataFrame(B,columns=['userId','productName','rating'])
    print("Rating Data Frame")

    rating_df['userId']=rating_df['userId'].astype(str).astype(np.int)
    rating_df['productName']=rating_df['productName'].astype(str)
    rating_df['rating']=rating_df['rating'].astype(str).astype(np.float)
    # .astype(np.float64)
    print(rating_df)
   
    if request.user.is_authenticated:
        userId = request.user.id
        userInput=ReviewRating.objects.select_related('product').filter(user=userId)

        print("user le review gareko kati wota",userInput)
        if  userInput.count()==0:
            userInput = None
            params={}
            params['recommended']=None
            return render(request,'product/product_recommendation.html',params)

        else:
            for item in userInput:
                C=[item.product.product_name,item.rating]
                D+=[C]

            inputProduct=pd.DataFrame(D,columns=['product_name','rating'])
            print("product by the user Data Frame")
            inputProduct['rating']=inputProduct['rating'].astype(str).astype(np.float)
            print(inputProduct)


            # filtering out the product by title
            inputId = products_df[products_df['product_name'].isin(inputProduct['product_name'].tolist())]
            inputProduct = pd.merge(inputId, inputProduct)

            print(inputProduct)

            # filtering out users that have watched product that the input has watched and storing it

            userSubset = rating_df[rating_df['productName'].isin(inputProduct['product_name'].tolist())]
            print(userSubset.head())

            userSubsetGroup = userSubset.groupby(['userId'])

            userSubsetGroup = sorted(userSubsetGroup, key=lambda x:len(x[1]),reverse=True)

            print(userSubsetGroup[0:])

            userSubsetGroup = userSubsetGroup[0:]

            pearsonCorrelationDict = {}


            for name, group in userSubsetGroup:
                group = group.sort_values(by='userId')
                inputProduct = inputProduct.sort_values(by='product_name')

                nRatings = len(group)

                temp_df = inputProduct[inputProduct['product_name'].isin(group['productName'].tolist())]

                tempRatingList=temp_df['rating'].tolist()

                tempGroupList = group['rating'].tolist()

                #Now let's calculate the pearson correlation between two users, so called, x and y
                Sxx = sum([i**2 for i in tempRatingList]) - pow(sum(tempRatingList),2)/float(nRatings)
                Syy = sum([i**2 for i in tempGroupList]) - pow(sum(tempGroupList),2)/float(nRatings)
                Sxy = sum( i*j for i, j in zip(tempRatingList, tempGroupList)) - sum(tempRatingList)*sum(tempGroupList)/float(nRatings)

                #If the denominator is different than zero, then divide, else, 0 correlation.
                if Sxx != 0 and Syy != 0:
                    pearsonCorrelationDict[name] = Sxy/sqrt(Sxx*Syy)
                else:
                    pearsonCorrelationDict[name] = 0

            print(pearsonCorrelationDict.items())

            pearsonDF = pd.DataFrame.from_dict(pearsonCorrelationDict, orient='index')
            pearsonDF.columns = ['similarityIndex']
            pearsonDF['userId'] = pearsonDF.index
            pearsonDF.index = range(len(pearsonDF))
            print(pearsonDF.head())


            topUsers=pearsonDF.sort_values(by='similarityIndex', ascending=False)[0:]
            print(topUsers.head())

            topUserRating=topUsers.merge(rating_df,left_on='userId',right_on='userId',how='inner')
            topUserRating.head()

            #Multiplies the similarity by the user's ratings
            topUserRating['weightedRating'] = topUserRating['similarityIndex']*topUserRating['rating']
            topUserRating.head()

            #Applies a sum to the topUsers after grouping it up by userId
            tempTopUsersRating = topUserRating.groupby('productName').sum()[['similarityIndex','weightedRating']]
            tempTopUsersRating.columns = ['sum_similarityIndex','sum_weightedRating']
            tempTopUsersRating.head()

            # creates an empty dataframe
            recommendation_df = pd.DataFrame()

            # now we take the weighted average
            recommendation_df['weighted average recommendation score'] = tempTopUsersRating['sum_weightedRating']/tempTopUsersRating['sum_similarityIndex']
            recommendation_df['productName'] = tempTopUsersRating.index
            recommendation_df.head()

            recommendation_df = recommendation_df.sort_values(by='weighted average recommendation score', ascending=False)
            recommender = products_df.loc[products_df['product_name'].isin(recommendation_df.head(5)['productName'].tolist())]
            print(recommender)
            # print("helllooooo")
            params={}
            params['recommended']=recommender.to_dict('records')
            print(recommender.to_dict('records'))
         
            return render(request,'product/product_recommendation.html',params)
            
    else:
        
            userInput = None
            params={}
            params['recommended']=None
            return render(request,'product/product_recommendation.html',params)

  

def REGISTER(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('login')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email id already exists')
            return redirect('login')
        user = User(
            username=username,
            email=email,
            first_name=firstname,
            last_name=lastname,
        )
        user.set_password(password)
        user.save()
        messages.success(request, 'Profile Is Successfully Registered !')

        return redirect('login')
    return render(request, 'account/my-account.html')


def LOGIN(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Email and Password are Invalid !')
            return redirect('login')


@login_required(login_url='/accounts/login/')
def PROFILE(request):
    maincategory = MainCategory.objects.all().order_by('-id')

    return render(request, 'profile/profile.html', {'maincategory': maincategory})


@login_required(login_url='/accounts/login/')
def PROFILE_UPDATE(request):
    if request.method == "POST":
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_id = request.user.id

        user = User.objects.get(id=user_id)
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email

        if password != None and password != "":
            user.set_password(password)
        user.save()
        messages.success(request, 'Profile Is Successfully Updated !')

        return redirect('profile')


def ABOUT(request):
    maincategory = MainCategory.objects.all().order_by('-id')

    return render(request, 'Main/about.html', {'maincategory': maincategory})


def CONTACT(request):
    maincategory = MainCategory.objects.all().order_by('-id')

    return render(request, 'Main/contact.html', {'maincategory': maincategory})


def PRODUCT(request):
    category = Category.objects.all()
    product = Product.objects.all()
    color = Color.objects.all()
    brand = Brand.objects.all
    maincategory = MainCategory.objects.all().order_by('-id')
    min_price = Product.objects.all().aggregate(Min('price'))
    max_price = Product.objects.all().aggregate(Max('price'))
    ColorID = request.GET.get('colorID')
    FilterPrice = request.GET.get('FilterPrice')
    total_data = Product.objects.count()

    for prod in product:
        reviews = ReviewRating.objects.filter(product__id=prod.id)

    if FilterPrice:
        Int_FilterPrice = int(FilterPrice)
        paged_products = Product.objects.filter(price__lte=Int_FilterPrice)


    elif ColorID:
        paged_products = Product.objects.filter(color=ColorID)


    else:
        paged_products = Product.objects.all()[:50]

    context = {
        'category': category,
        'product': paged_products,
        'min_price': min_price,
        'max_price': max_price,
        'FilterPrice': FilterPrice,
        'color': color,
        'brand': brand,
        'reviews': reviews,
        'total_data': total_data,
        'maincategory': maincategory,
    }

    return render(request, 'product/product.html', context)


def filter_data(request):
    categories = request.GET.getlist('category[]')
    print(categories)
    brands = request.GET.getlist('brand[]')
    colors = request.GET.getlist('color[]')

    allProducts = Product.objects.all().order_by('id').distinct()
    if len(categories) > 0:
        allProducts = allProducts.filter(Categories__id__in=categories).distinct()
    if len(brands) > 0:
        allProducts = allProducts.filter(Brand__id__in=brands).distinct()
    if len(colors) > 0:
        allProducts = allProducts.filter(color__id__in=colors).distinct()
    t = render_to_string('ajax/product.html', {'product': allProducts})

    return JsonResponse({'data': t})


def load_more_data(request):
    offset = int(request.GET['offset'])
    limit = int(request.GET['limit'])
    data = Product.objects.all().order_by('id')[offset:offset + limit]
    t = render_to_string('ajax/product.html', {'product': data})
    return JsonResponse({'data': t})


@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)

    # Check whether the Product is already in Cart or Not
    item_already_in_cart = Cart.objects.filter(product=product_id, user=user)
    if item_already_in_cart:
        cp = get_object_or_404(Cart, product=product_id, user=user)
        cp.quantity += 1
        cp.save()
    else:
        Cart(user=user, product=product).save()

    return redirect('cart')


@login_required
def cart(request):
    maincategory = MainCategory.objects.all().order_by('-id')

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
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount
    context = {
        'cart_products': cart_products,
        'amount': amount,
        'tax': tax,
        'shipping_amount': shipping_amount,
        'total_amount': int(amount + shipping_amount + tax),
        'maincategory': maincategory,

    }
    return render(request, 'cart/cart.html', context)


@login_required
def remove_cart(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
        messages.success(request, "Product removed from Cart.")
    return redirect('cart')


@login_required
def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
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
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount
        data = {
            'unit_total_price': c.unit_total_price,
            'quantity': c.quantity,
            'amount': amount,
            'tax': tax,
            'shipping_amount': shipping_amount,
            'total_amount': int(amount + shipping_amount + tax),
        }
    return JsonResponse(data)


@login_required
def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
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
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount
        data = {
            'unit_total_price': c.unit_total_price,
            'quantity': c.quantity,
            'amount': amount,
            'tax': tax,
            'shipping_amount': shipping_amount,
            'total_amount': int(amount + shipping_amount + tax),
        }
    return JsonResponse(data)


def charge(request):
    amount = int(request.POST.get('total_amount'))

    print(amount)
    customer = None
    if request.method == 'POST':
        print('Data:', request.POST)
        try:
            customer = stripe.Customer.create(
                email=request.POST['email'],
                name=request.POST['username'],
                source=request.POST['stripeToken'],
            )
            charge = stripe.Charge.create(customer=customer,
                                          amount=amount * 100,
                                          currency='npr',
                                          description="Payment",
                                          )
        except (stripe.error.RateLimitError, stripe.error.StripeError,
                stripe.error.AuthenticationError, stripe.error.CardError) as error:
            return redirect('failure')

    user = request.user
    address_id = request.POST.get('address')
    print(address_id)
    address = get_object_or_404(Address, id=address_id)

    # Get all the products of User in Cart
    cart = Cart.objects.filter(user=user)
    for c in cart:
        # Saving all the products from Cart to Order
        Order(user=user, address=address, product=c.product, price=c.product.price, unit_total_price=c.unit_total_price,
              ref_code=create_ref_code(), quantity=c.quantity).save()
        # And Deleting from Cart
        c.delete()
    return redirect(reverse('success', args=[amount]))


def failure(request):
    return render(request, 'cart/failure.html')


def successMsg(request, args):
    amount = args
    template = render_to_string('cart/email_template.html', {'name': request.user.username, 'amount': amount})
    email = EmailMessage(
        'Thanks for purchasing the eCommerce products !',
        template,
        settings.EMAIL_HOST_USER,
        [request.user.email]

    )

    email.fail_silently = False
    email.send()

    return render(request, 'cart/success.html', {'amount': amount})


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')

    if request.method == "POST":
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)


def search(request):
    maincategory = MainCategory.objects.all().order_by('-id')
    category = Category.objects.all()
    product = Product.objects.all()
    color = Color.objects.all()
    brand = Brand.objects.all
    min_price = Product.objects.all().aggregate(Min('price'))
    max_price = Product.objects.all().aggregate(Max('price'))
    ColorID = request.GET.get('colorID')
    FilterPrice = request.GET.get('FilterPrice')
    for prod in product:
        reviews = ReviewRating.objects.filter(product__id=prod.id)

    if FilterPrice:
        Int_FilterPrice = int(FilterPrice)
        product = Product.objects.filter(price__lte=Int_FilterPrice)

    elif ColorID:
        product = Product.objects.filter(color=ColorID)


    else:
        query = request.GET['query']
        multiple_queries = (Q(product_name__icontains=query) | Q(Categories__name__icontains=query) | Q(
            Brand__name__icontains=query))
        product = Product.objects.filter(multiple_queries)

    context = {
        'category': category,
        'product': product,
        'min_price': min_price,
        'max_price': max_price,
        'FilterPrice': FilterPrice,
        'color': color,
        'brand': brand,
        'reviews': reviews,
        'maincategory': maincategory,
    }

    return render(request, 'product/search.html', context)


def place_order(request):
    maincategory = MainCategory.objects.all().order_by('-id')
    coupon = Coupon_Code.objects.all()
    coupon.discount = 0
    valid_coupon = None
    invalid_coupon = None
    if request.method == "GET":
        coupon_code = request.GET.get('coupon_code')
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
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount
    addresses = Address.objects.filter(user=user)

    context = {
        'cart_products': cart_products,
        'amount': amount,
        'tax': tax,
        'shipping_amount': shipping_amount,
        'total_amount': int(
            float(round((amount + shipping_amount + tax) - amount * Decimal(coupon.discount / 100), 1))),
        'coupon': coupon,
        'valid_coupon': valid_coupon,
        'invalid_coupon': invalid_coupon,
        'addresses': addresses,
        'maincategory': maincategory,

    }
    return render(request, 'checkout/checkout.html', context)


@login_required
def profile(request):
    maincategory = MainCategory.objects.all().order_by('-id')
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(request, 'profile/profile_detail.html',
                  {'addresses': addresses, 'orders': orders, 'maincategory': maincategory})


@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        maincategory = MainCategory.objects.all().order_by('-id')

        return render(request, 'profile/add_address.html', {'form': form, 'maincategory': maincategory})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user = request.user
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            reg = Address(user=user, locality=locality, city=city, state=state)
            reg.save()
            messages.success(request, "New Address Added Successfully.")
        return redirect('profile_detail')


@login_required
def orders(request):
    all_orders = Order.objects.filter(user=request.user).order_by('-ordered_date')
    maincategory = MainCategory.objects.all().order_by('-id')

    return render(request, 'checkout/orders.html', {'orders': all_orders, 'maincategory': maincategory})


def blog(request):
    maincategory = MainCategory.objects.all().order_by('-id')
    blogcategories = BlogCategory.objects.all()
    category_count = get_category_count()
    print(category_count)
    blogsidelist = Post.objects.all().order_by('-timestamp')[:4]
    bloglist = Post.objects.filter(featured=True)
    paginator = Paginator(bloglist, 2)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    if request.method == "POST":
        email = request.POST.get('email')
        signup_object = Signup()
        signup_object.email = email
        signup_object.save()

    context = {
        'bloglist': paginated_queryset,
        'blogcategories': blogcategories,
        'maincategory': maincategory,
        'page_request_var': page_request_var,
        'blogsidelist': blogsidelist,
        'category_count': category_count,
    }

    return render(request, 'blog/blog.html', context)


def blog_details(request, id):
    maincategory = MainCategory.objects.all().order_by('-id')
    blogsidelist = Post.objects.all().order_by('-timestamp')[:4]
    post = get_object_or_404(Post, id=id)
    category_count = get_category_count()
    form = CommentForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.instance.user = request.user
            form.instance.post = post
            form.save()
            return redirect(reverse("blog_detail", kwargs={
                'id': post.pk
            }))

    context = {
        'post': post,
        'maincategory': maincategory,
        'blogsidelist': blogsidelist,
        'category_count': category_count,
        'form': form,

    }

    return render(request, 'blog/blog_details.html', context)


@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Address removed.")
    return redirect('profile_detail')


def faq(request):
    maincategory = MainCategory.objects.all().order_by('-id')
    return render(request, 'Main/faq.html', {'maincategory': maincategory})


@method_decorator(login_required, name='dispatch')
class RequestRefundView(View):
    def get(self, request):
        maincategory = MainCategory.objects.all().order_by('-id')

        form = RefundForm()
        context = {
            'form': form,
            'maincategory': maincategory
        }
        return render(request, "refund/request_refund.html", context)

    def post(self, request):
        form = RefundForm(request.POST, request.FILES)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            image = form.cleaned_data.get('image')

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

                messages.success(request, "Your request was received. You will shortly receive an email if refund is successfully granted.")
                return redirect("request-refund")

            except ObjectDoesNotExist:
                messages.error(request, "This order does not exist.")
                return redirect("request-refund")

        else:
            return HttpResponse("Form Failed, Go back")


@login_required
def refunds(request):
    refunds = Order.objects.filter(Q(user=request.user), (Q(refund_requested=True) & Q(refund_granted=False)) | (
            Q(refund_requested=False) & Q(refund_granted=True)))

    refunds_sent = Order.objects.filter(user=request.user, refund_requested=False, refund_granted=True,
                                        email_sent=False)
    if refunds_sent:
        sum = 0

        for refund in refunds_sent:
            refund.email_sent = True
            refund.save()
            sum = refund.product.price + sum

        template = render_to_string('refund/refund_email.html',
                                    {'name': request.user.username, 'sum': sum, 'refunds': refunds_sent})
        email = EmailMessage(
            'Your order has been refunded !',
            template,
            settings.EMAIL_HOST_USER,
            [request.user.email]

        )

        email.fail_silently = False
        email.send()

    maincategory = MainCategory.objects.all().order_by('-id')

    context = {
        'orders': refunds,
        'maincategory': maincategory,
    }

    return render(request, 'refund/refunds.html', context)


def categorization(request, category_id):
    maincategory = MainCategory.objects.all().order_by('-id')

    items_of_maincategory = Product.objects.filter(Categories__main_category__id=category_id)
    context = {
        'items': items_of_maincategory,
        'maincategory': maincategory,
    }

    return render(request, 'product/categorization.html', context)


def search_blog(request):
    queryset = Post.objects.all()
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(Q(title__icontains=query) | Q(overview__icontains=query)).distinct()

    context = {
        'queryset': queryset,
    }
    return render(request, 'blog/search_results.html', context)
