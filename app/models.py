from django.db import models
from ckeditor.fields import RichTextField
from django.db.models import Avg, Count
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
User = settings.AUTH_USER_MODEL
# Create your models here.
DISCOUNT_DEAL = (
    ('HOT DEALS', 'HOT DEALS'),
    ('New Arrivals', 'New Arrivals'),
)

class CustomUser(AbstractUser):
    is_delivery = models.BooleanField('Is Delivery', default=False)
    phone_number = PhoneNumberField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)



class Slider(models.Model):
    Image = models.ImageField(upload_to='media/slider_imgs')
    Discount_Deal = models.CharField(choices=DISCOUNT_DEAL, max_length=100)
    SALE = models.IntegerField()
    Brand_Name = models.CharField(max_length=200)
    Discount = models.IntegerField()
    Link = models.CharField(max_length=200, null=True, blank="True")

    def __str__(self):
        return self.Brand_Name


class Banner(models.Model):
    image = models.ImageField(upload_to='media/banner_img')
    Discount_Deal = models.CharField(max_length=100)
    Quote = models.CharField(max_length=100)
    Discount = models.IntegerField()
    link = models.CharField(max_length=400, null=True)

    def __str__(self):
        return self.Quote


class MainCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Category(models.Model):
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name + "-->" + self.main_category.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.category.main_category.name + "---" + self.category.name + "---" + self.name


class Section(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Color(models.Model):
    code = models.CharField(max_length=100)

    def __str__(self):
        return self.code


class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    total_quantity = models.IntegerField()
    Availability = models.IntegerField()
    featured_image = models.CharField(max_length=100)
    product_name = models.CharField(max_length=100)
    price = models.IntegerField()
    Discount = models.IntegerField()
    model_Name = models.CharField(max_length=100)
    Categories = models.ForeignKey(Category, on_delete=models.CASCADE)
    Tags = models.CharField(max_length=200)
    Product_information = RichTextField()
    Description = RichTextField()
    section = models.ForeignKey(Section, on_delete=models.DO_NOTHING)
    slug = models.SlugField(default='', max_length=500, null=True, blank=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True)
    Brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.product_name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("product_detail", kwargs={'slug': self.slug})

    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count

    class Meta:
        db_table = "app_Product"


def create_slug(instance, new_slug=None):
    slug = slugify(instance.product_name)
    if new_slug is not None:
        slug = new_slug
    qs = Product.objects.filter(slug=slug).order_by('-id')
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug


def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)


pre_save.connect(pre_save_post_receiver, Product)


class Coupon_Code(models.Model):
    code = models.CharField(max_length=10)
    discount = models.IntegerField()

    def __str__(self):
        return self.code


class Product_Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image_url = models.CharField(max_length=200)


class Additional_Information(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    specification = models.CharField(max_length=100)
    detail = models.CharField(max_length=100)


class Cart(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated Date")

    def __str__(self):
        return str(self.user)

    # Creating Model Property to calculate Quantity x Price
    @property
    def unit_total_price(self):
        return self.quantity * self.product.price


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject


class Address(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    locality = models.CharField(max_length=150, verbose_name="Nearest Location")
    city = models.CharField(max_length=150, verbose_name="City")
    state = models.CharField(max_length=150, verbose_name="State")

    def __str__(self):
        return self.locality


STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('On The Way', 'On The Way'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled')
)


class Order(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE, null=True)
    ref_code = models.CharField(max_length=10, blank=True, null=True)
    address = models.ForeignKey(Address, verbose_name="Shipping Address", on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, verbose_name="Product", on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(verbose_name="Quantity", null=True)
    ordered_date = models.DateTimeField(auto_now_add=True, verbose_name="Ordered Date", null=True)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    price = models.IntegerField()
    email_sent = models.BooleanField(default=False)
    unit_total_price = models.IntegerField()
    status = models.CharField(
        choices=STATUS_CHOICES,
        max_length=50,
        default="Pending"
    )

    def __str__(self):
        return f"{self.pk}"


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()
    Image = models.ImageField(upload_to='media/refund', null=True, blank=True)

    def __str__(self):
        return f"{self.pk}"


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='media/blog', default='media/blog/profile.png')

    def __str__(self):
        return self.user.username


class PostView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username



class BlogCategory(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return self.title


class Post(models.Model):
    title = models.CharField(max_length=100)
    overview = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    comment_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    thumbnail = models.ImageField(upload_to='media/blog')
    categories = models.ManyToManyField(BlogCategory)
    featured = models.BooleanField()
    content = RichTextField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse('blog_detail', kwargs={
            'id': self.pk,
        })

    def get_update_url(self):
        from django.urls import reverse

        return reverse('post-update', kwargs={
            'pk': self.pk
        })

    def get_delete_url(self):
        from django.urls import reverse

        return reverse('post-delete', kwargs={
            'pk': self.pk
        })

    @property
    def get_comments(self):
        return self.comments.all().order_by('-timestamp')


    @property
    def view_count(self):
        return PostView.objects.filter(post=self).count()

class Signup(models.Model):
    
    email = models.EmailField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


# here we add a model class for the Product recommendation
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=None)
    ratings = models.CharField(max_length=70)
    rated_date = models.DateTimeField(auto_now_add=True)


# here we making a models for the c2c 
# user can upload the product

# here we making a models for the c2c 
# user can upload the product

class C2CUploadProductModel(models.Model):
    crcProductUploadId = models.IntegerField(max_length=100,null=True)
    productId = models.AutoField(primary_key=True)  
    productName = models.CharField(max_length=200)
    productDescription = models.CharField(max_length=300)
    STATUS_CHOICES = [
        ('used', 'Used'),
        ('not_used', 'Not Used'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES,null=True)

    STATUS_PRICE = [
        ('negotiable', 'Negotiable'),
        ('not_negotiable', 'Not Negotiable'),
    ]
    price_choice = models.CharField(max_length=50, choices=STATUS_PRICE,null=True)


    STATUS_DELIVERY = [
        ('delivery_available', 'Delivery_Available'),
        ('not_available', 'Not Available'),
    ]
    delivery_choice = models.CharField(max_length=50, choices=STATUS_DELIVERY,null=True)
  

    phone_number = models.CharField(max_length=20,null=True)

    image = models.ImageField(upload_to="c2cproductimage")   #upload_to -> where image is store 
    date = models.DateTimeField(auto_now_add=True)  #auto_now_add means when user can post the product then default it can add bydefault time
    approved = models.BooleanField(default=False)  # New field to track approval status


    def save(self, *args, **kwargs):
        if not self.date:
            self.date = timezone.now()
        super().save(*args, **kwargs)
# make drop down for used item or not



class FriendModel(models.Model):
    profile = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.profile.username
    


class ChatMessage(models.Model):
    body = models.TextField()
    msg_sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="msg_sender")
    msg_receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="msg_receiver")
    seen = models.BooleanField(default=False)
    
    def __str__(self):
        return self.body
    

#For chat 
class FriendRequest(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_requests')
    status = models.CharField(max_length=10, choices=(
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ))


class ChatRoom(models.Model):
    participant1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_as_participant1')
    participant2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_as_participant2')

    def __str__(self):
        return f"Chat Room {self.id}"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE,null=True)



class DeliveryReport(models.Model):
    reference_code = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=50, null=True,blank=True)
    report = models.TextField(max_length=100, null=True, blank=True) 

    def __str__(self):
        return self.username
