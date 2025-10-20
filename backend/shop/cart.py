from decimal import Decimal
from django.conf import settings
from shop.models import Product

from decimal import Decimal
from django.conf import settings
from shop.models import Product  # adjust import according to your app structure


class Cart:
    """
    A session-based shopping cart class.

    This class manages cart data using Django's session framework.
    It allows adding, updating, removing, and iterating over cart items.
    Each user's cart is stored in their session under a key defined by
    `settings.CART_SESSION_ID`.

    Attributes:
        session (SessionBase): The current user's session.
        cart (dict): The dictionary that holds cart data, where keys are
            product IDs (as strings) and values are dictionaries containing
            quantity and price information.

    Example:
        >>> cart = Cart(request)
        >>> cart.add(product, quantity=2)
        >>> total = cart.get_total_price()
    """

    def __init__(self, request):
        """
        Initialize the cart.

        Args:
            request (HttpRequest): The current HTTP request object containing
                the session where cart data will be stored.

        Behavior:
            - Retrieves the cart from the session if it exists.
            - If not, creates an empty cart dictionary in the session.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Create a new empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.

        Args:
            product (Product): The product instance to add to the cart.
            quantity (int): Number of items to add (default is 1).
            override_quantity (bool): If True, set the quantity directly.
                If False, increment the existing quantity.

        Behavior:
            - Converts product ID to string (since session data must be serializable).
            - If the product is not in the cart, initializes it with price and quantity.
            - Updates the quantity accordingly.
            - Calls `save()` to mark the session as modified.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            # Store initial cart item with quantity 0 and product price as string
            self.cart[product_id] = {"quantity": 0, "price": str(product.price)}
        if override_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity
        self.save()

    def save(self):
        """
        Mark the session as modified.

        Behavior:
            Ensures that Django knows the session data has changed,
            so it will be saved at the end of the request.
        """
        self.session.modified = True

    def remove(self, product):
        """
        Remove a product from the cart.

        Args:
            product (Product): The product instance to remove.

        Behavior:
            - Deletes the product from the session-based cart if it exists.
            - Calls `save()` to update the session.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Iterate over the items in the cart and fetch products from the database.

        Yields:
            dict: Each cart item containing:
                - "product": Product instance.
                - "quantity": Quantity of that product.
                - "price": Decimal price.
                - "total_price": price * quantity

        Behavior:
            - Fetches all product objects corresponding to IDs stored in the cart.
            - Enriches cart items with full product objects and computed total prices.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            item = self.cart[str(product.id)]
            item["product"] = product
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            yield item

    def __len__(self):
        """
        Return the total number of items in the cart.

        Returns:
            int: Sum of all product quantities in the cart.
        """
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self):
        """
        Calculate the total cost of all items in the cart.

        Returns:
            Decimal: The sum of (price * quantity) for all items.
        """
        return sum(
            Decimal(item["price"]) * item["quantity"] for item in self.cart.values()
        )

    def clear(self):
        """
        Remove the cart from the session completely.

        Behavior:
            - Deletes the cart entry from the session.
            - Calls `save()` to ensure the session updates are applied.
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()
