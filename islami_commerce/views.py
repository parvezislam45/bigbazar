from django.shortcuts import render,get_object_or_404
from shop.models import Product,SubCategory,Category
from shop.utils import paginate_queryset
from django.db.models import Q

def home(request):
    return render(request,'index.html')

def Shop(request):
    keyword = request.GET.get('keyword')
    category_slug = request.GET.get('category')
    subcategory_slug = request.GET.get('subcategory')
    max_price = request.GET.get('price')
    brands = request.GET.getlist('brand')
    ratings = request.GET.getlist('rating')

    # ✅ Base QuerySet
    products = Product.objects.all()
    selected_category = None
    selected_subcategory = None
    subcategories = None

    # ✅ If category selected → filter products + fetch related subcategories
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)
        subcategories = SubCategory.objects.filter(category=selected_category)
    else:
        subcategories = SubCategory.objects.all()

    # ✅ If subcategory selected → filter products further
    if subcategory_slug:
        selected_subcategory = get_object_or_404(SubCategory, slug=subcategory_slug)
        products = products.filter(subcategory=selected_subcategory)

    # ✅ Keyword filter
    if keyword:
        products = products.filter(
            Q(product_name__icontains=keyword) |
            Q(description__icontains=keyword) |
            Q(price__icontains=keyword)
        )

    # ✅ Price filter
    if max_price:
        try:
            max_price = float(max_price)
            products = products.filter(price__lte=max_price)
        except (ValueError, TypeError):
            pass

    # ✅ Brand filter
    if brands:
        products = products.filter(brand__in=brands)

    # ✅ Ratings filter
    if ratings:
        try:
            ratings = [float(r) for r in ratings]
            q = Q()
            for r in ratings:
                q |= Q(rating__gte=r)
            products = products.filter(q)
        except ValueError:
            pass

    # ✅ Get all unique brands for filter
    all_brands = Product.objects.values_list('brand', flat=True).distinct().exclude(brand__isnull=True).exclude(brand__exact='')

    # ✅ Pagination
    paginated_products = paginate_queryset(request, products.order_by('-created_date'), per_page=20, page_param='product_page')

    context = {
        'products': paginated_products,
        'p_count': products.count(),
        'brands': all_brands,
        'ratings_list': [5, 4, 3, 2, 1],
        'subcategories': subcategories,
        'selected_category': selected_category,
        'selected_subcategory': selected_subcategory,
    }
    return render(request, 'shop.html', context)