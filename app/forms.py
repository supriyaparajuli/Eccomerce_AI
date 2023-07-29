from django import forms
from .models import (
    ReviewRating,
    Address,
    Comment,
    Post,
    C2CUploadProductModel,
    ChatMessage,
    Order,
    DeliveryReport,
)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ["subject", "review", "rating"]


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ["locality", "city", "state"]

        widgets = {
            "locality": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "pattern": "[A-Za-z ]+",
                    "placeholder": "Popular Place like Restaurant, Religious Site, must be alphanumeric etc.",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "pattern": "[A-Za-z ]+",
                    "placeholder": "City, must be alphanumeric etc.",
                }
            ),
            "state": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "pattern": "[0-9]{1,5}",
                    "placeholder": "State or Province, must be alphanumeric etc.",
                }
            ),
        }


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}))
    email = forms.EmailField()
    image = forms.ImageField()


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Type your comment",
                "id": "usercomment",
            }
        )
    )

    class Meta:
        model = Comment
        fields = ("content",)


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={"required": False, "cols": 30, "rows": 10})
    )

    class Meta:
        model = Post
        fields = (
            "title",
            "overview",
            "content",
            "thumbnail",
            "categories",
            "featured",
        )


# making a form field for the  C2C
class C2CUploadProductForm(forms.ModelForm):
    class Meta:
        model = C2CUploadProductModel
        fields = ('productName', 'productDescription', 'status', 'price_choice', 'delivery_choice', 'phone_number', 'image', 'approved')
        labels = {
            'productName': 'Product Name',
            'productDescription': 'Description',
            'status': 'Status',
            'price_choice': 'Price',
            'delivery_choice': 'Delivery',
            'phone_number': 'Phone Number',
            'image': 'Product Image',
            'approved': 'Approved',
        }
        
        widgets = {
            'productDescription': forms.Textarea(attrs={'class': 'form-control', 'cols': 40, 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'price_choice': forms.Select(attrs={'class': 'form-control'}),
            'delivery_choice': forms.Select(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values for the dropdown fields
        self.fields['status'].initial = 'not_used'
        self.fields['price_choice'].initial = 'negotiable'
        self.fields['delivery_choice'].initial = 'delivery_available'

class ChatMessageForm(forms.ModelForm):
    body = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "forms", "rows": 3, "placeholder": "Enter  message here"}
        )
    )

    class Meta:
        model = ChatMessage
        fields = [
            "body",
        ]


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "status",
        ]


class DeliveryReportForm(forms.ModelForm):
    class Meta:
        model = DeliveryReport
        fields = ["reference_code", "username", "report"]
        widgets = {
            "reference_code": forms.TextInput(
                attrs={"class": "form-control", "id": "refid","required":"required"}
            ),
            "username": forms.TextInput(
                attrs={"class": "form-control", "id": "reporteduserid","required":"required"}
            ),
            "report": forms.Textarea(
                attrs={"class": "form-control", "id": "reportid","required":"required"}
            ),
        }
        


