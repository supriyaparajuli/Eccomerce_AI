from django import forms
from .models import ReviewRating, Address, Comment, Post


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['locality', 'city', 'state']

        widgets = {'locality': forms.TextInput(
            attrs={'class': 'form-control', 'pattern': '[A-Za-z ]+',
                   'placeholder': 'Popular Place like Restaurant, Religious Site, must be alphanumeric etc.'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'pattern': '[A-Za-z ]+',
                                           'placeholder': 'City, must be alphanumeric etc.'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'pattern': '[0-9]{1,5}',
                                            'placeholder': 'State or Province, must be alphanumeric etc.'})}


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()
    image = forms.ImageField()


class CommentForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Type your comment',
        'id': 'usercomment',
    }))

    class Meta:
        model = Comment
        fields = ('content',)


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={'required': False, 'cols': 30, 'rows': 10}
        )
    )

    class Meta:
        model = Post
        fields = ('title', 'overview', 'content', 'thumbnail',
                  'categories', 'featured',)
