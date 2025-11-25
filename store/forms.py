# store/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Import the Order model only if it exists in store.models (we used it in the example)
from .models import Order  # safe: models do not import forms

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]

class AddToCartForm(forms.Form):
    """
    Simple form used on product detail to add a quantity to the session cart.
    Views expect AddToCartForm to exist with a 'quantity' integer field.
    """
    quantity = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={'min': 1}))

class CheckoutForm(forms.ModelForm):
    """
    Simple checkout form that only collects the delivery address.
    If you later add payment fields, extend this form.
    """
    class Meta:
        model = Order
        fields = ['address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Street, City, ZIP / Postal code'}),
        }

