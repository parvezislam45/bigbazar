
from rest_framework.generics import CreateAPIView,GenericAPIView,ListAPIView,UpdateAPIView,DestroyAPIView
from rest_framework import generics, status
from django.http import JsonResponse,Http404
from .serializers import UserSerializer,LoginSerializer,UserRoleUpdateSerializer,VendorApplicationSerializer,VendorStatusSerializer
from django.contrib.auth import login,logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication
User = get_user_model()
from .models import Vendor

class RegisterView(CreateAPIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def get(self, request):
        return render(request, 'accounts/register.html')

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return redirect('user_dashboard')
        return render(request, 'accounts/register.html', {'errors': serializer.errors})


class LoginView(GenericAPIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def get(self, request):
        return render(request, 'accounts/login.html')

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return render(request, 'accounts/login.html', {'errors': serializer.errors})
        
        user = serializer.validated_data
        login(request, user)

        # Role-based redirection
        if user.is_admin() or user.is_vendor():
            return redirect('staff_dashboard')  # Combined dashboard
        else:
            return redirect('user_dashboard')
    
    
class UserListView(ListAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    
class UpdateUserRoleView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRoleUpdateSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return super().get_queryset()
    
class DeleteUserView(DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
@login_required
def staff_dashboard(request):
    if request.user.role == 'user':
        return redirect('user_dashboard')
    return render(request, 'accounts/staff.html')
@login_required
def user_dashboard(request):
    if request.user.role.lower() != 'user':
        return redirect('staff_dashboard')
    return render(request, 'accounts/client.html')
def User_All(request):
    return render(request, 'accounts/users.html')
def Vendor_All(request):
    return render(request, 'accounts/allvendor.html')
def Vendor_Request(request):
    all_vendors = Vendor.objects.all().order_by('-created_at')
    pending_vendor_count = Vendor.objects.filter(status='pending').count()

    return render(request, 'accounts/request.html', {
        'vendors': all_vendors,
        'pending_vendor_count': pending_vendor_count,
    })

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def ApplyVendors(request):
    if request.method == 'POST':
        # Combine POST data and FILES
        data = request.POST.copy()
        data.update(request.FILES)  # Merge files into data
        
        serializer = VendorApplicationSerializer(
            data=data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return redirect('dashboard')
        else:
            return render(request, 'accounts/apply.html', {'errors': serializer.errors})
    
    return render(request, 'accounts/apply.html')

def Vendor_Detail(request, vendor_id):
    try:
        vendor = Vendor.objects.get(id=vendor_id)
    except Vendor.DoesNotExist:
        raise Http404("Vendor not found")

    data = {
        'id': vendor.id,
        'business_name': vendor.business_name,
        'business_email': vendor.business_email,
        'phone_number': vendor.phone_number,
        'address': vendor.address,
        'division': vendor.division,
        'district': vendor.district,
        'sub_district': vendor.sub_district,
        'union': vendor.union,
        'registration_number': vendor.registration_number,
        'tax_id': vendor.tax_id,
        'business_description': vendor.business_description,
        'status': vendor.status,
        'profile_image': vendor.profile_image.url if vendor.profile_image else None,
        'license_image': vendor.license_image.url if vendor.license_image else None,
        'nid_front': vendor.nid_front.url if vendor.nid_front else None,
        'nid_back': vendor.nid_back.url if vendor.nid_back else None,
    }

    return JsonResponse(data)

class VendorDetailAPIView(generics.UpdateAPIView):
    queryset = Vendor.objects.all()
    permission_classes = [AllowAny]
    serializer_class = VendorStatusSerializer



