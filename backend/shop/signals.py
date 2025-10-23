from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from shop.models import Product, CartItem
from .cart import Cart


@receiver(user_logged_in)
def merge_cart_on_login(sender, user, request, **kwargs):

    cart = Cart(request)
    for item in cart:
        product = item["product"]
        quantity = item["quantity"]

        cart_item, created = CartItem.objects.get_or_create(
            user=user,
            product=product,
            defaults={"quantity": quantity},
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

    cart.clear()
