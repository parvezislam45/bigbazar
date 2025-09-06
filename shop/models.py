# models.py
from django.db import models
from django.urls import reverse
from accounts.models import User
from django.utils.text import slugify

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_url(self):
        return reverse('products_by_category', args=[self.slug])

    def __str__(self):
        return self.category_name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    subcategory_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=True)
    subcat_image = models.ImageField(upload_to='photos/subcategories', blank=True)

    class Meta:
        verbose_name = 'subcategory'
        verbose_name_plural = 'subcategories'
        unique_together = ('category', 'subcategory_name')  # No duplicate subcategory names per category

    def get_url(self):
        return reverse('products_by_subcategory', args=[self.category.slug, self.slug])

    def __str__(self):
        return f"{self.subcategory_name} ({self.category.category_name})"


class Product(models.Model):
    product_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    description = models.CharField(max_length=2000)
    price = models.IntegerField(blank=True)
    discount = models.IntegerField(blank=True, null=True)
    discounted_price = models.IntegerField(null=True, blank=True)
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    brand = models.CharField(max_length=200, null=True, blank=True)
    rating = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    numReviews = models.IntegerField(null=True, default=0)

    def save(self, *args, **kwargs):
        if not self.slug and self.product_name:
            self.slug = slugify(self.product_name)
        if self.discount:
            self.discounted_price = self.price - self.discount
        else:
            self.discounted_price = None
        super().save(*args, **kwargs)
        
    def update_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            total = sum([r.rating for r in reviews])
            self.rating = total / reviews.count()
            self.numReviews = reviews.count()
        else:
            self.rating = None
            self.numReviews = 0
            self.save()

    def get_url(self):
        return reverse('product-detail-page', args=[self.pk])

    def __str__(self):
        return self.product_name if self.product_name else "Unnamed Product"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='photos/products')


class ProductSize(models.Model):
    product = models.ForeignKey(Product, related_name='sizes', on_delete=models.CASCADE)
    size = models.CharField(max_length=20)
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('processing', 'Processing'),
        ('transit', 'In Transit'),
        ('delivered', 'Delivered'),
    ]
    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('online', 'Online Payment'),
        ('emi', 'EMI'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.CharField(max_length=100, null=True)
    product_image = models.URLField(blank=True, null=True)
    total_quantity = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='online')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    emi_bank = models.CharField(max_length=100, blank=True, null=True)
    emi_duration = models.CharField(max_length=50, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Order #{self.id} - {self.product.product_name}"
    
    
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name} ({self.rating})"
    
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name} ({self.quantity})"
    
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist_items")
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name}"
