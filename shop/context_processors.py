from .models import Category,Product,Order
from django.db.models import Sum
from accounts.models import User


from .models import Category, Product

def common_data(request):
    categories = Category.objects.all()
    brands = Product.objects.values_list('brand', flat=True).distinct().exclude(brand__isnull=True).exclude(brand__exact='')
    return {
        'all_categories': categories,
        'all_brands': brands,
    }


def Menu_Links(request):
    links = Category.objects.all()
    return {'links': links}
def Product_Links(request):
    products = Product.objects.all()
    return {'products': products}

def orders_processor(request):
    if request.user.is_authenticated:
        # Admin: return all orders and aggregates
        if hasattr(request.user, 'is_admin') and request.user.is_admin():
            all_orders = Order.objects.all()
            total_orders = all_orders.count()
            total_revenue = all_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
            total_subtotal = all_orders.aggregate(Sum('subtotal'))['subtotal__sum'] or 0

            return {
                'vendor_orders': all_orders,
                'vendor_total_orders': total_orders,
                'vendor_total_revenue': total_revenue,
                'vendor_total_subtotal': total_subtotal,
            }

        # Vendor: return only vendor's orders
        elif hasattr(request.user, 'is_vendor') and request.user.is_vendor():
            vendor_products = Product.objects.filter(user=request.user)
            vendor_orders = Order.objects.filter(product__in=vendor_products).distinct()
            total_orders = vendor_orders.count()
            total_revenue = vendor_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
            total_subtotal = vendor_orders.aggregate(Sum('subtotal'))['subtotal__sum'] or 0

            return {
                'vendor_orders': vendor_orders,
                'vendor_total_orders': total_orders,
                'vendor_total_revenue': total_revenue,
                'vendor_total_subtotal': total_subtotal,
            }

    # Default return for unauthenticated or other roles
    return {
        'vendor_orders': [],
        'vendor_total_orders': 0,
        'vendor_total_revenue': 0,
        'vendor_total_subtotal': 0,
    }
    
    
def chat_user_list(request):
    if request.user.is_authenticated:
        role = getattr(request.user, 'role', None)
        if role == 'user':
            return {'chat_user_list': User.objects.filter(role='vendor')}
        elif role == 'vendor':
            return {'chat_user_list': User.objects.filter(role__in=['user', 'admin'])}
        elif role == 'admin':
            return {'chat_user_list': User.objects.filter(role='vendor')}
    return {'chat_user_list': []}

def order_status_counts(request):
    return {
        'pending_order_count': Order.objects.filter(status='pending').count(),
        'received_order_count': Order.objects.filter(status='received').count(),
        'processing_order_count': Order.objects.filter(status='processing').count(),
        'transit_order_count': Order.objects.filter(status='transit').count(),
        'delivered_order_count': Order.objects.filter(status='delivered').count(),
    }
    
