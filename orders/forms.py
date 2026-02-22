from django import forms
from users.models import Address


class CheckoutForm(forms.Form):
    address_id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    shipping_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address_line1 = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address_line2 = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    state = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    postal_code = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    country = forms.CharField(max_length=100, initial='India', widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user


class PaymentForm(forms.Form):
    PAYMENT_METHODS = [
        ('cod', '💵 Cash on Delivery'),
        ('upi', '📱 UPI'),
        ('card', '💳 Credit / Debit Card'),
        ('netbanking', '🏦 Net Banking'),
    ]
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHODS,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
