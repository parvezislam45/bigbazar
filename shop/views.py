from django.shortcuts import render,redirect,get_object_or_404
from rest_framework.views import APIView
from rest_framework import generics,permissions
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from .models import Product,Order,Review,Wishlist,Cart,SubCategory,Category
from .serializers import ProductSerializer,OrderSerializer,CartSerializer,WishlistSerializer,CategorySerializer,SubCategorySerializer
from django.db.models import Q
import json
from .utils import paginate_queryset
from django.http import JsonResponse
from django.views.generic.detail import DetailView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
import uuid
from django.views.decorators.http import require_POST
from rest_framework.permissions import AllowAny

def add_product_page(request):
    return render(request, 'add_product.html')
def Add_Category(request):
    return render(request, 'add_category.html')

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class SubCategoryListCreateView(generics.ListCreateAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer

class SubCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    
class SubcategoriesByCategoryView(APIView):
    def get(self, request, category_id):
        subcategories = SubCategory.objects.filter(category_id=category_id)
        serializer = SubCategorySerializer(subcategories, many=True)
        return Response(serializer.data)

class ProductCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        if not (request.user.is_vendor() or request.user.is_admin()):
            return Response(
                {'error': 'Only vendors or admins can create products'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProductSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Product created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductUpdateView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk, format=None):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        if product.user != request.user and not request.user.is_admin():
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()

        # Handle percentage-based discount
        discount = data.get('discount')
        if discount:
            try:
                if isinstance(discount, str) and '%' in discount:
                    percent = float(discount.replace('%', ''))
                    discount_amount = round(product.price * (percent / 100))
                    data['discount'] = discount_amount
                else:
                    data['discount'] = int(discount)
            except Exception:
                return Response({'error': 'Invalid discount format'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductSerializer(product, data=data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Product updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class ProductDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, format=None):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        if product.user != request.user and not request.user.is_admin():
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        product.delete()
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_200_OK)


class VendorProductListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Verify user is a vendor
        if not request.user.is_vendor():
            return Response(
                {'error': 'Only vendors can view products'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Filter products by current vendor
        products = Product.objects.filter(user=request.user)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
  
class AllProductsView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'all_products.html'  # your template file

    def get(self, request, format=None):
        user = request.user
        if user.role == 'vendor':
            products = Product.objects.filter(user=user)
        else:
            products = Product.objects.all()
        
        serializer = ProductSerializer(products, many=True)

        if request.accepted_renderer.format == 'html':
            return Response({'products': products})
        return Response(serializer.data)

def Store(request):
    keyword = request.GET.get('keyword')
    category_slug = request.GET.get('category')
    max_price = request.GET.get('price')
    products = Product.objects.all()
    brands = request.GET.getlist('brand')
    ratings = request.GET.getlist('rating')

    if keyword:
        products = products.filter(
            Q(product_name__icontains=keyword) |
            Q(description__icontains=keyword) |
            Q(price__icontains=keyword)
        )

    if category_slug:
        products = products.filter(category__slug=category_slug)
        
    if max_price is not None and max_price != "":
        try:
            max_price = float(max_price)
            if max_price > 0:
                products = products.filter(price__lte=max_price)
        except (TypeError, ValueError):
            pass
        
    if brands:
        products = products.filter(brand__in=brands)
    all_brands = Product.objects.values_list('brand', flat=True).distinct().exclude(brand__isnull=True).exclude(brand__exact='')
    
    if ratings:
        try:
            ratings = [float(r) for r in ratings]
            q = Q()
            for r in ratings:
                q |= Q(rating__gte=r)
            products = products.filter(q)
        except ValueError:
            pass
        
    ratings_list = [5, 4, 3, 2, 1]

    # Apply pagination here
    paginated_products = paginate_queryset(request, products.order_by('-created_date'), per_page=20, page_param='product_page')
    

    context = {
        'products': paginated_products,
        'p_count': products.count(),
        'brands': all_brands,
        'ratings_list': ratings_list,
    }
    return render(request, 'store.html', context)


def Ajax_Search_Products(request):
    keyword = request.GET.get('term', '') 
    products = Product.objects.filter(
        Q(product_name__icontains=keyword)
    )[:5] 
    results = []
    for product in products:
        results.append({
            'label': product.product_name,
            'value': product.product_name,
            'id': product.id,
        })

    return JsonResponse(results, safe=False)

class ProductDetailTemplateView(DetailView):
    model = Product
    template_name = 'details.html'
    context_object_name = 'product'
    
# ------------------- CART -------------------
class CartListCreateView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        existing_item = Cart.objects.filter(user=self.request.user, product=product).first()
        if existing_item:
            existing_item.quantity += serializer.validated_data.get("quantity", 1)
            existing_item.save()
        else:
            serializer.save(user=self.request.user)


class CartUpdateView(generics.UpdateAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Cart.objects.all()

    def patch(self, request, *args, **kwargs):
        cart_item = self.get_object()
        action = request.data.get("action")  # "increase" or "decrease"

        if action == "increase":
            cart_item.quantity += 1
        elif action == "decrease":
            cart_item.quantity -= 1

        if cart_item.quantity <= 0:
            cart_item.delete()
            return Response({"message": "Product removed"}, status=status.HTTP_204_NO_CONTENT)

        cart_item.save()
        return Response(CartSerializer(cart_item).data, status=status.HTTP_200_OK)


class CartDeleteView(generics.DestroyAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

# ------------------- WISHLIST -------------------
class WishlistListCreateView(generics.ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        exists = Wishlist.objects.filter(user=self.request.user, product=product).exists()

        if exists:
            return Response({"message": "Product already in wishlist"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=self.request.user)

class WishlistDeleteView(generics.DestroyAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
    
@login_required
def order_from_cart(request):
    """
    Handles placing an order for multiple products from the user's cart.
    """

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            items = data.get("items", [])

            if not items:
                return JsonResponse({"error": "Cart is empty!"}, status=400)

            # Calculate totals
            subtotal = 0
            shipping_charge = 0
            total_quantity = 0

            for item in items:
                product = get_object_or_404(Product, product_name=item["product_name"])
                quantity = item["quantity"]
                price = product.price * quantity

                subtotal += price
                total_quantity += quantity

                # Shipping logic per product
                category_name = str(product.category.category_name).lower()
                if category_name == "electronics":
                    shipping_charge += 1000 * quantity
                elif category_name == "mobile":
                    shipping_charge += 100 * quantity

            total_price = subtotal + shipping_charge

            # Save all items in session to use on order page
            request.session["cart_order_items"] = items
            request.session["cart_order_totals"] = {
                "subtotal": subtotal,
                "shipping_charge": shipping_charge,
                "total_price": total_price,
                "total_quantity": total_quantity,
            }

            return JsonResponse({"success": True})

        except Exception as e:
            print(e)
            return JsonResponse({"error": "Something went wrong"}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


def order_form(request):
    """
    Handles both single product orders and multiple cart product orders.
    """

    # If we are ordering from cart
    if "cart_order_items" in request.session:
        cart_items = request.session["cart_order_items"]
        totals = request.session["cart_order_totals"]

        if request.method == "POST":
            # Extract common form fields
            name = request.POST.get("name")
            phone = request.POST.get("phone")
            address = request.POST.get("address")
            city = request.POST.get("city")
            street = request.POST.get("street")
            country = request.POST.get("country")
            payment_method = request.POST.get("payment_method")
            transaction_id = request.POST.get("transaction_id", "")
            emi_bank = request.POST.get("emi_bank", "")
            emi_duration = request.POST.get("emi_duration", "")

            # Validate EMI
            if payment_method == "emi":
                if not request.user.is_authenticated:
                    messages.error(request, "You must be logged in to use EMI")
                    return redirect("login")
                if not emi_bank or not emi_duration:
                    messages.error(request, "EMI details are required")
                    return render(
                        request,
                        "orders.html",
                        {
                            "cart_items": cart_items,
                            "totals": totals,
                            "form_data": request.POST,
                        },
                    )

            # Create a single order for all items
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=name,
                phone=phone,
                address=address,
                city=city,
                street=street,
                country=country,
                total_quantity=totals["total_quantity"],
                subtotal=totals["subtotal"],
                shipping_charge=totals["shipping_charge"],
                total_price=totals["total_price"],
                payment_method=payment_method,
                transaction_id=transaction_id or None,
                emi_bank=emi_bank or None,
                emi_duration=emi_duration or None,
                is_paid=(payment_method != "online"),
            )

            # Link products & reduce stock
            for item in cart_items:
                product = get_object_or_404(Product, product_name=item["product_name"])
                quantity = item["quantity"]

                order.products.add(product)
                product.stock -= quantity
                product.save()

            # Clear cart after order success
            Cart.objects.filter(user=request.user).delete()
            del request.session["cart_order_items"]
            del request.session["cart_order_totals"]

            # Redirect for payment if online
            if payment_method == "online":
                return redirect(reverse("sslcommerz-payment", args=[order.id]))
            return redirect("order-success")

        return render(
            request,
            "orders.html",
            {
                "cart_items": cart_items,
                "totals": totals,
            },
        )

    # ----------------- SINGLE PRODUCT ORDER -----------------
    if request.method == "POST":
        # Extract form data
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        street = request.POST.get('street')
        country = request.POST.get('country')
        total_quantity = int(request.POST.get('total_quantity', 1))
        product_name = request.POST.get('product_name')
        payment_method = request.POST.get('payment_method')
        transaction_id = request.POST.get('transaction_id', '')
        emi_bank = request.POST.get('emi_bank', '')
        emi_duration = request.POST.get('emi_duration', '')

        # Get product
        product = get_object_or_404(Product, product_name=product_name)
        category_name = str(product.category.category_name).lower()

        # Calculate prices
        subtotal = product.price * total_quantity
        if category_name == 'electronics':
            shipping_charge = 1000 * total_quantity
        elif category_name == 'mobile':
            shipping_charge = 100 * total_quantity
        else:
            shipping_charge = 0
        total_price = subtotal + shipping_charge

        # Stock check
        if product.stock < total_quantity:
            messages.error(request, "Not enough stock available")
            return render(
                request,
                "orders.html",
                {
                    "product": product,
                    "quantity": total_quantity,
                    "subtotal": subtotal,
                    "shipping_charge": shipping_charge,
                    "total_price": total_price,
                },
            )

        # Create single product order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            name=name,
            phone=phone,
            address=address,
            city=city,
            street=street,
            country=country,
            product=product,
            category=category_name,
            product_image=product.images.first().image.url if product.images.exists() else '',
            total_quantity=total_quantity,
            subtotal=subtotal,
            shipping_charge=shipping_charge,
            total_price=total_price,
            payment_method=payment_method,
            transaction_id=transaction_id or None,
            emi_bank=emi_bank or None,
            emi_duration=emi_duration or None,
            is_paid=(payment_method != 'online')
        )

        # Reduce stock
        product.stock -= total_quantity
        product.save()

        # Handle payment redirection
        if payment_method == 'online':
            return redirect(reverse('sslcommerz-payment', args=[order.id]))
        return redirect('order-success')

    # ----------------- GET REQUEST -----------------
    product_name = request.GET.get("product_name", "")
    quantity = int(request.GET.get("quantity", 1))

    if not product_name:
        return redirect("home")

    product = get_object_or_404(Product, product_name=product_name)
    category_name = str(product.category.category_name).lower()
    image_url = product.images.first().image.url if product.images.exists() else ""

    subtotal = product.price * quantity
    if category_name == "electronics":
        shipping_charge = 1000 * quantity
    elif category_name == "mobile":
        shipping_charge = 100 * quantity
    else:
        shipping_charge = 0
    total_price = subtotal + shipping_charge

    return render(
        request,
        "orders.html",
        {
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
            "shipping_charge": shipping_charge,
            "total_price": total_price,
            "image_url": image_url,
        },
    )

        
class OrderUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]  # or use custom permission
    lookup_field = 'pk'

def sslcommerz_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # For real implementation, use SSLCommerz SDK here
    # This is a simulation for demo purposes
    context = {
        'order': order,
        'payment_url': reverse('sslcommerz-callback') + f'?order_id={order_id}'
    }
    return render(request, 'payment_page.html', context)

@csrf_exempt
def sslcommerz_callback(request):
    order_id = request.GET.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    
    # In real implementation, verify payment with SSLCommerz
    order.is_paid = True
    order.status = 'received'
    order.transaction_id = uuid.uuid4().hex[:20]  # Generate fake transaction ID
    order.save()
    
    return redirect('payment-success')

def payment_success(request):
    return render(request, 'payment_success.html')

def order_success(request):
    return render(request, 'order_success.html')

@login_required
def complete_emi(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        order.emi_bank = request.POST.get('emi_bank')
        order.emi_duration = request.POST.get('emi_duration')
        order.payment_method = 'emi'
        order.save()
        return redirect('order-success')
    
    return render(request, 'complete_emi.html', {'order': order})
  
def admin_order_list_view(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin.html', {'orders': orders})

def pending_status_view(request):
    pending_orders = Order.objects.filter(status='pending').order_by('-created_at')
    pending_order_count = pending_orders.count()
    return render(request, 'pending.html',{'orders': pending_orders,'pending_order_count': pending_order_count,})

def received_status_view(request):
    received_orders = Order.objects.filter(status='received').order_by('-created_at')
    received_orders_count = received_orders.count()
    return render(request, 'received.html', {'orders': received_orders,'received_orders_count':received_orders_count})

def processing_status_view(request):
    processing_orders = Order.objects.filter(status='processing').order_by('-created_at')
    processing_orders_count = processing_orders.count()
    return render(request, 'processing.html', {'orders': processing_orders,'processing_orders_count':processing_orders_count})

def transit_status_view(request):
    transit_orders = Order.objects.filter(status='transit').order_by('-created_at')
    transit_orders_count = transit_orders.count()
    return render(request, 'transit.html', {'orders': transit_orders,'transit_orders_count':transit_orders_count})

def delivered_status_view(request):
    delivered_orders = Order.objects.filter(status='delivered').order_by('-created_at')
    delivered_orders_count = delivered_orders.count()
    return render(request, 'delivered.html', {'orders': delivered_orders,'delivered_orders_count':delivered_orders_count})

@login_required
def vendor_order_list_view(request):
    if not request.user.is_vendor():
        return render(request, 'not_authorized.html')

    # Get all orders for products added by the current vendor
    products = Product.objects.filter(user=request.user)
    orders = Order.objects.filter(product__in=products).order_by('-created_at')

    return render(request, 'vendor.html', {'orders': orders})

def order_details_api(request, order_id):
    try:
        order = Order.objects.get(id=order_id)

        # Allow access if user is:
        # - The product vendor
        # - OR admin/staff
        is_vendor = request.user == order.product.user
        is_admin = request.user.is_staff or request.user.is_superuser

        if not (is_vendor or is_admin):
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        data = {
            'id': order.id,
            'name': order.name,
            'phone': order.phone,
            'address': order.address,
            'city': order.city,
            'street': order.street,
            'country': order.country,
            'product_name': order.product.product_name,
            'total_quantity': order.total_quantity,
            'subtotal': str(order.subtotal),
            'shipping_charge': str(order.shipping_charge),
            'total_price': str(order.total_price),
            'status': order.status,
            'payment_method': order.payment_method,
            'transaction_id': order.transaction_id,
            'emi_bank': order.emi_bank,
            'emi_duration': order.emi_duration,
        }
        return JsonResponse(data)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    
    
@login_required
@require_POST
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    rating = request.POST.get('rating')
    comment = request.POST.get('comment', '').strip()

    if not rating and not comment:
        # Prevent empty reviews
        return redirect(product.get_url())

    Review.objects.update_or_create(
        product=product,
        user=request.user,
        defaults={
            'rating': float(rating) if rating else None,
            'comment': comment,
        }
    )

    product.update_rating()
    return redirect(product.get_url())



    

