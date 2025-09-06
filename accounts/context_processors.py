from .models import User,Vendor

def All_Users(request):
    if request.user.is_authenticated:
        users = User.objects.all()
    else:
        users = []
    return {
        'all_users': users
    }
    

    
def pending_vendor_count(request):
    count = Vendor.objects.filter(status='pending').count()
    return {'pending_vendor_count': count}
def all(request):
    vendors = User.objects.filter(role='vendor')
    users = User.objects.filter(role='user')

    return {
        'vendors': vendors,
        'users': users,
        'total_vendor_count': vendors.count(),
        'total_user_count': users.count(),
    }


    
