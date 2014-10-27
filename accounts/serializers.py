import re

from django.contrib.auth import authenticate, login

from rest_framework import serializers

from .models import User, make_password

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ('last_login', 'date_joined', 'is_staff', 'groups', 'user_permissions', 'password')

class UserAdminSerializer(serializers.ModelSerializer):

    def validate_password(self, attrs, source):
        password = attrs[source]
        attrs[source] = make_password(password)
        return attrs
    
    class Meta:
        model = User
        write_only_fields = ('password', )
        exclude = ('last_login', 'date_joined', 'is_staff', 'groups', 'user_permissions')


class UserChangePasswordSerializer(serializers.ModelSerializer):
    oldpassword = serializers.CharField()
    newpassword = serializers.CharField()

    def validate_oldpassword(self, attrs, source):
        oldpassword = attrs['oldpassword']
        user = self.object
        if not user.check_password(oldpassword):
            raise serializers.ValidationError('Incorrect old password.')
        attrs['oldpassword'] = '[PASSWORD_MASKED]'
        return attrs

    def validate_newpassword(self, attrs, source):
        newpassword = attrs['newpassword']
        if not re.match(r'[\x21-\x7F]{8,}', newpassword):
            raise serializers.ValidationError(
                    'Invalid new password, ' 
                    'should be at least 8 non-space ASCII characters.'
                    )
        attrs['password'] = make_password(newpassword)
        attrs['newpassword'] = '[PASSWORD_MASKED]'
        return attrs

    class Meta:
        model = User
        fields = ('oldpassword', 'newpassword')