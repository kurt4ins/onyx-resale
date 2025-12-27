from django import forms
from .models import PaymentMethod


class CheckoutForm(forms.Form):
    payment_method = forms.ChoiceField(
        label='Способ оплаты',
        choices=PaymentMethod.choices,
        widget=forms.RadioSelect(attrs={'class': 'payment-method-radio'}),
        initial=PaymentMethod.CASH
    )
    
    def __init__(self, *args, **kwargs):
        self.customer = kwargs.pop('customer', None)
        super().__init__(*args, **kwargs)

