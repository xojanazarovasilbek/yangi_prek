from rest_framework import serializers
from test.utils import chech_email_or_phone_number
from rest_framework.exceptions import ValidationError
from .models import CustomUser, CodeVerified, VIA_EMAIL, VIA_PHONE

class SingUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    auth_type = serializers.CharField(required=False, read_only=True)
    auth_status = serializers.CharField(required=False, read_only=True)
    # email_phone_number = serializers.CharField(required=False, write_only=True)

    def __init__(self,*args, **kwargs):
        super(SingUpSerializer, self).__init__(*args,**kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ['id','auth_type','auth_status']

    def create(self, validated_data):
        user = super(SingUpSerializer, self).create(validated_data)
        if user.auth_type == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
        elif user.auth_type == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)

        user.save()
        return user




    def validate(self, data):
        super(SingUpSerializer,self).validate(data)
        data = self.auth_validate(data)
        return data
    
    def validate_email_phone_number(self, data):
        if data and CustomUser.objects.filter(email=data).exists():
            raise ValidationError('bu email mavjud')
        elif data and CustomUser.objects.filter(phone_number=data).exists():
            raise ValidationError('bu telefon raqam mavjud')
        return data

    @staticmethod
    def auth_validate(data):
        user_input = str(data.get('email_phone_number')).lower()
        auth_type = chech_email_or_phone_number(user_input)
        print(user_input)

        if auth_type == 'email':
            data = {
                'auth_type':VIA_EMAIL,
                'email':user_input
            }
        elif auth_type == 'phone':
            data = {
                'auth_type':VIA_PHONE,
                'phone':user_input
            }
        else:
            data = {
                'success':False,
                'msg': "siz telefon raqam yoki email kiritishingiz kerak"
            }
            raise ValidationError(data)

        return data

    def to_representation(self, instance):
        data =  super(SingUpSerializer, self).to_representation(instance)
        data.update(instance.token())
        return data