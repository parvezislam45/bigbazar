# serializers.py
from rest_framework import serializers
from .models import Product, ProductImage, ProductSize,Order,Cart,Wishlist,Category,SubCategory
from django.utils.text import slugify


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'category_name', 'cat_image', 'slug']
        read_only_fields = ['slug']

    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['category_name'])
        return super().create(validated_data)


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'category','subcategory_name', 'subcat_image', 'slug']
        read_only_fields = ['slug']

    def create(self, validated_data):
        validated_data['slug'] = slugify(validated_data['subcategory_name'])
        return super().create(validated_data)

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']

class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ['size']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            "slug": {"required": False},
            "discounted_price": {"read_only": True},
            "user": {"read_only": True},
        }

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user

        # ✅ Generate slug if missing
        if not validated_data.get('slug') and validated_data.get('product_name'):
            validated_data['slug'] = slugify(validated_data['product_name'])

        # ✅ Create product first
        product = Product.objects.create(**validated_data)

        # ✅ Handle images
        images = request.FILES.getlist('images')
        for img in images:
            ProductImage.objects.create(product=product, image=img)

        # ✅ Handle sizes
        sizes = request.data.getlist('sizes')
        for size in sizes:
            ProductSize.objects.create(product=product, size=size)

        return product
    
class OrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    buyer_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'product_name', 'buyer_name', 'total_quantity', 'subtotal',
            'shipping_charge', 'total_price', 'status', 'created_at',
            'payment_method', 'transaction_id', 'is_paid'
        ]
                
class CartSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    price = serializers.DecimalField(source="product.price", max_digits=10, decimal_places=2, read_only=True)
    discounted_price = serializers.DecimalField(source="product.discounted_price", max_digits=10, decimal_places=2, read_only=True)
    product_image = serializers.ImageField(source="product.image", read_only=True, default=None)

    class Meta:
        model = Cart
        fields = [
            "id",
            "product",
            "product_name",
            "product_image",
            "price",
            "discounted_price",
            "quantity",
            "added_at",
        ]
        read_only_fields = ["id", "added_at"]

class WishlistSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    price = serializers.DecimalField(source="product.price", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "product", "product_name", "price", "added_at"]
        read_only_fields = ["id", "added_at"]

