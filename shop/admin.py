from django.contrib import admin
from .models import Product, Category, ProductImage, ProductSize,Order,Review,Cart,Wishlist,SubCategory
from django.utils.html import format_html

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug')

admin.site.register(Category, CategoryAdmin)

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('subcategory_name', 'category')
    prepopulated_fields = {'slug': ('subcategory_name',)}
admin.site.register(SubCategory, SubCategoryAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available', 'first_image')
    prepopulated_fields = {'slug': ('product_name',)}

    def first_image(self, obj):
        first_img = obj.images.first()
        if first_img:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover"/>', first_img.image.url)
        return "No Image"
    
    first_image.short_description = "Image"

admin.site.register(Product, ProductAdmin)

# Optionally register ProductImage and ProductSize
admin.site.register(ProductImage)
admin.site.register(ProductSize)
admin.site.register(Order)
admin.site.register(Review)
admin.site.register(Cart)
admin.site.register(Wishlist)
