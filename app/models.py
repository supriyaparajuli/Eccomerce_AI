from django.contrib.auth.models import User
from django.db import models
from ckeditor.fields import RichTextField
from django.db.models import Avg, Count
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.contrib.auth import get_user_model

user_1 = get_user_model()

# Create your models here.
DISCOUNT_DEAL = (
    ('HOT DEALS', 'HOT DEALS'),
    ('New Arrivals', 'New Arrivals'),
)


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
    user = models.OneToOneField(user_1, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='media/blog')

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

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse('blog_detail', kwargs={
            'id' : self.id,
        })


class Signup(models.Model):
    email = models.EmailField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
