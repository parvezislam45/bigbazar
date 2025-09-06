from django.urls import path
from .views import (
    RegisterView, LoginView,logout_view,user_dashboard,UserListView,User_All,UpdateUserRoleView,DeleteUserView,ApplyVendors,Vendor_Request,Vendor_Detail,VendorDetailAPIView,staff_dashboard,Vendor_All
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('user/', User_All, name='all_users'),
    path('allvendor/', Vendor_All, name='all_vendor'),
    path('users/<int:pk>/update-role/', UpdateUserRoleView.as_view(), name='update_user_role'),
    path('users/<int:pk>/delete/', DeleteUserView.as_view(), name='delete_user'),
    path('dashboard/staff/', staff_dashboard, name='staff_dashboard'),
    path('dashboard/user/', user_dashboard, name='user_dashboard'),
    path('apply/', ApplyVendors, name='vendor-apply'),
    path('request/', Vendor_Request, name='vendor_request'),
    path('request/<int:vendor_id>/', Vendor_Detail, name='vendor_detail'),
    path('vendors/<int:pk>/', VendorDetailAPIView.as_view(), name='vendor-detail'),
    
]