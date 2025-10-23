from decimal import Decimal

import graphene
from django.db import transaction
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from shop.cart import Cart
from shop.models import CartItem, Category, Order, OrderItem, Product


# region GraphQL Types
class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = "__all__"


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"


# class CartItemType(DjangoObjectType):
#     class Meta:
#         model = CartItem
#         fields = "__all__"


class CartItemType(DjangoObjectType):
    class Meta:
        model = CartItem
        fields = ("id", "product", "quantity")

    total_price = graphene.Decimal(required=True)

    def resolve_total_price(self, info):
        return self.quantity * self.product.price


class GuestCartItemType(graphene.ObjectType):
    product = graphene.Field(ProductType, required=True)
    quantity = graphene.Int(required=True)
    total_price = graphene.Decimal(required=True)


class CartItemUnion(graphene.Union):
    class Meta:
        types = (CartItemType, GuestCartItemType)


class CartType(graphene.ObjectType):
    items = graphene.List(CartItemUnion)
    total_items = graphene.Int()
    total_price = graphene.Decimal()


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"


# endregion
# region GraphQL Queries


class ProductQuery(graphene.ObjectType):
    all_categories = graphene.List(CategoryType)
    category = graphene.Field(CategoryType, id=graphene.ID(required=True))

    all_products = graphene.List(ProductType)
    product = graphene.Field(ProductType, id=graphene.ID(required=True))

    # Resolvers
    def resolve_all_categories(root, info):
        return Category.objects.all()

    def resolve_category(root, info, id):
        try:
            return Category.objects.get(pk=id)
        except Category.DoesNotExist:
            raise GraphQLError("Category not found")

    def resolve_all_products(root, info):
        return Product.objects.all()

    def resolve_product(root, info, id):
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            raise GraphQLError("Product not found")


class CartQuery(graphene.ObjectType):
    cart = graphene.Field(CartType)

    def resolve_cart(self, info):
        print("inside cartquery)")

        request = info.context
        cart = Cart(request)
        user = request.user

        if user.is_authenticated:
            cart_items = CartItem.objects.filter(user=user).select_related("product")
            total_items = sum(item.quantity for item in cart_items)
            total_price = sum(item.quantity * item.product.price for item in cart_items)
            return CartType(
                items=cart_items, total_items=total_items, total_price=total_price
            )
        else:
            cart_items = []
            for item in cart:
                cart_items.append(
                    GuestCartItemType(
                        product=item["product"],
                        quantity=item["quantity"],
                        total_price=Decimal(
                            item["total_price"]
                        ),  # ✅ wrap with Decimal
                    )
                )

            total_items = sum(item.quantity for item in cart_items)
            total_price = sum(
                Decimal(item.total_price) for item in cart_items
            )  # ✅ wrap again
            return CartType(
                items=cart_items, total_items=total_items, total_price=total_price
            )


class OrderQuery(graphene.ObjectType):
    my_orders = graphene.List(OrderType)
    order = graphene.Field(OrderType, id=graphene.Int(required=True))

    def resolve_my_orders(root, info):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        return Order.objects.filter(user=user).order_by("-created_at")

    def resolve_order(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required.")
        try:
            return Order.objects.get(id=id, user=user)
        except Order.DoesNotExist:
            raise GraphQLError("Order not found.")


# endregion


# region Mutaions


class CreateCategory(graphene.Mutation):
    category = graphene.Field(CategoryType)

    class Arguments:
        name = graphene.String(required=True)
        slug = graphene.String(required=True)

    def mutate(self, info, name, slug):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        category = Category.objects.create(name=name, slug=slug)
        return CreateCategory(category=category)


class UpdateCategory(graphene.Mutation):
    category = graphene.Field(CategoryType)

    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        slug = graphene.String()

    def mutate(self, info, id, name=None, slug=None):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        try:
            category = Category.objects.get(pk=id)
        except Category.DoesNotExist:
            raise GraphQLError("Category not found")
        if name:
            category.name = name
        if slug:
            category.slug = slug
        category.save()
        return UpdateCategory(category=category)


class DeleteCategory(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        try:
            category = Category.objects.get(pk=id)
        except Category.DoesNotExist:
            raise GraphQLError("Category not found")
        category.delete()
        return DeleteCategory(message="Category deleted successfully")


class CreateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)

    class Arguments:
        category_id = graphene.ID(required=True)
        title = graphene.String(required=True)
        description = graphene.String()
        price = graphene.Float(required=True)
        stock = graphene.Int(required=True)

    def mutate(self, info, category_id, title, description="", price=0, stock=0):
        if price < 0 or stock < 0:
            raise GraphQLError("Price and stock must be non-negative")
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            raise GraphQLError("Category not found")
        product = Product.objects.create(
            category=category,
            title=title,
            description=description,
            price=price,
            stock=stock,
        )
        return CreateProduct(product=product)


class UpdateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)

    class Arguments:
        id = graphene.ID(required=True)
        category_id = graphene.ID()
        title = graphene.String()
        description = graphene.String()
        price = graphene.Float()
        stock = graphene.Int()

    def mutate(
        self,
        info,
        id,
        category_id=None,
        title=None,
        description=None,
        price=None,
        stock=None,
    ):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        try:
            product = Product.objects.get(pk=id)
        except Product.DoesNotExist:
            raise GraphQLError("Product not found")
        if category_id:
            try:
                category = Category.objects.get(pk=category_id)
                product.category = category
            except Category.DoesNotExist:
                raise GraphQLError("Category not found")
        if title:
            product.title = title
        if description is not None:
            product.description = description
        if price is not None:
            product.price = price
        if stock is not None:
            product.stock = stock
        product.save()
        return UpdateProduct(product=product)


class DeleteProduct(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")
        try:
            product = Product.objects.get(pk=id)
        except Product.DoesNotExist:
            raise GraphQLError("Product not found")
        product.delete()
        return DeleteProduct(message="Product deleted successfully")


class AddToCart(graphene.Mutation):
    message = graphene.String()
    total_items = graphene.Int()
    cart_item = graphene.Field(CartItemType)

    class Arguments:
        product_id = graphene.ID(required=True)
        quantity = graphene.Int(required=True)

    def mutate(self, info, product_id, quantity):
        print("inside add to cart")
        request = info.context
        user = request.user
        cart = Cart(request)

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise GraphQLError("Product not found")

        if user.is_authenticated:
            cart_item, created = CartItem.objects.get_or_create(
                user=user,
                product=product,
                defaults={"quantity": quantity},
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            total_items = CartItem.objects.filter(user=user).count()
        else:
            cart.add(product, quantity=quantity)
            total_items = len(cart)

        return AddToCart(
            message="Product added to cart",
            total_items=total_items,
            cart_item=cart_item if user.is_authenticated else None,
        )


class UpdateCartItemQuantity(graphene.Mutation):
    cart_item = graphene.Field(CartItemType)

    class Arguments:
        cart_item_id = graphene.ID(required=True)
        quantity = graphene.Int(required=True)

    def mutate(self, info, cart_item_id, quantity):
        user = info.context.user
        session_key = info.context.session.session_key
        try:
            cart_item = CartItem.objects.get(
                pk=cart_item_id,
                user=user if user.is_authenticated else None,
                session_key=session_key if not user.is_authenticated else None,
            )
        except CartItem.DoesNotExist:
            raise GraphQLError("Cart item not found")

        cart_item.quantity = quantity
        cart_item.save()
        return UpdateCartItemQuantity(cart_item=cart_item)


class RemoveFromCart(graphene.Mutation):
    message = graphene.String()
    total_items = graphene.Int()

    class Arguments:
        product_id = graphene.ID(required=True)

    def mutate(self, info, product_id):
        request = info.context
        cart = Cart(request)
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise GraphQLError("Product not found")

        cart.remove(product)
        total_items = len(cart)
        return RemoveFromCart(message="Product removed", total_items=total_items)


class UpdateOrderStatus(graphene.Mutation):
    order = graphene.Field(OrderType)

    class Arguments:
        order_id = graphene.ID(required=True)
        status = graphene.String(required=True)

    def mutate(self, info, order_id, status):
        user = info.context.user
        if not user.is_authenticated or not user.is_staff:
            raise GraphQLError("Admin privileges required")
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            raise GraphQLError("Order not found")
        if status not in dict(Order.STATUS_CHOICES).keys():
            raise GraphQLError("Invalid status")
        order.status = status
        order.save()
        return UpdateOrderStatus(order=order)


class Checkout(graphene.Mutation):
    order_id = graphene.Int()
    message = graphene.String()

    class Arguments:
        session_key = graphene.String(required=False)

    def mutate(self, info, session_key=None):
        request = info.context
        user = request.user if request.user.is_authenticated else None

        if user:
            cart_items = CartItem.objects.filter(user=user)
        elif session_key:
            cart_items = CartItem.objects.filter(session_key=session_key)
        else:
            raise GraphQLError("No user or session_key provided")

        if not cart_items.exists():
            raise GraphQLError("Cart is empty")

        with transaction.atomic():
            total = 0
            order = Order.objects.create(user=user, total=0, status="pending")

            for item in cart_items:
                product = item.product
                if product.stock < item.quantity:
                    raise GraphQLError(f"Not enough stock for {product.title}")

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price=product.price,
                )

                product.stock -= item.quantity
                product.save()

                total += product.price * item.quantity

            order.total = total
            order.status = "paid"
            order.save()

            cart_items.delete()

        return Checkout(order_id=order.id, message="Order created successfully")


# endregion


class ShopMutation(graphene.ObjectType):
    create_category = CreateCategory.Field()
    update_category = UpdateCategory.Field()
    delete_category = DeleteCategory.Field()

    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()

    # CartItem Mutations
    add_to_cart = AddToCart.Field()
    update_cart_item_quantity = UpdateCartItemQuantity.Field()
    remove_from_cart = RemoveFromCart.Field()

    # Checkout
    checkout = Checkout.Field()

    # Order Mutations
    update_order_status = UpdateOrderStatus.Field()


class ShopQuery(OrderQuery, ProductQuery, CartQuery, graphene.ObjectType):
    pass
