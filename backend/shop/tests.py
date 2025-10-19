from django.test import TestCase
from .models import Category, Product


class ProductModelTest(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Test Cat", slug="test-cat")
        self.prod = Product.objects.create(
            title="Product 1",
            description="Desc",
            price=9.99,
            stock=10,
            category=self.cat,
        )

    def test_product_creation(self):
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(self.prod.title, "Product 1")
