from rest_framework import serializers
from .models import User,Vendor
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id','first_name', 'username', 'email', 'password', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'user')
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        return user
    
class UserRoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['role']
        
class VendorApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'
        extra_kwargs = {
            'user': {'required': False},  # We'll handle this in create()
            'profile_image': {'required': True},
            'license_image': {'required': True},
            'nid_front': {'required': True},
            'nid_back': {'required': True},
        }

    def validate(self, data):
        user = self.context['request'].user
        if hasattr(user, 'vendor_profile'):
            raise serializers.ValidationError("You have already applied as a vendor.")
        return data

    def create(self, validated_data):
        # Automatically set the user from the request
        validated_data['user'] = self.context['request'].user
        return Vendor.objects.create(**validated_data)
    
    
class VendorStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['status']