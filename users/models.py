from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator,MinValueValidator, MaxValueValidator
from test.models import BaseModel
from datetime import datetime, timedelta
import uuid, random
from rest_framework_simplejwt.tokens import RefreshToken
# Create your models here.
ORDINARY_USER,MANAGER,ADMIN = ('ordinary_user','manager','admin')
VIA_EMAIL,VIA_PHONE = ('via_email', 'via_phone')
NEW,CODE_VERIFIED,DONE,PHOTO_DONE = ('new','code_verified','done','photo_done')

class CustomUser(BaseModel, AbstractUser):
    USER_ROLE = (
        (ORDINARY_USER, ORDINARY_USER),
        (MANAGER, MANAGER),
        (ADMIN,ADMIN)
    
    )

    AUTH_TYPE = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )

    AUTH_STATUS = (
        (NEW,NEW),
        (CODE_VERIFIED, CODE_VERIFIED),
        (DONE, DONE),
        (PHOTO_DONE, PHOTO_DONE)
    )

    auth_type = models.CharField(max_length=31, choices=AUTH_TYPE)
    user_role = models.CharField(max_length=31, choices=USER_ROLE, default=ORDINARY_USER)
    auth_status = models.CharField(max_length=31, choices=AUTH_STATUS, default=NEW)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=12, unique=True, blank=True, null=True)
    photo = models.ImageField(upload_to='users_photo/',blank=True,null=True, validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png','heix'])])
    
    def __str__(self):
        return self.username
    
    def create_verify_code(self, verify_type):
        code = random.randint(1000,9999)
        CodeVerified.objects.create(
            code=code,
            user=self, 
            verify_type=verify_type
        )







    def check_username(self):
        if not self.username:
            self.username = f"ins{uuid.uuid4().__str__().split('-')[-1]}"
            while CustomUser.objects.filter(username=self.username).exists():
                self.username = f"{self.username}+{str(random.randint(0,100))}"
    def check_pass(self):
        if not self.password:
            self.password = f"pas{uuid.uuid4().__str__().split('-')[-1]}"

    def check_email(self):
        if self.email:
            self.email = self.email.lower()
    
    def hashing_pass(self):
        self.set_password(self.password)
    def token(self):
        token = RefreshToken.for_user(self)
        data = {
            'refresh_token':str(token),
            'access_token':str(token.access_token)
        }
    def clean(self):
        self.check_username()
        self.check_email()
        self.check_pass()
        self.hashing_pass()
    def save(self, *args, **kwargs):
        super(CustomUser, self).save(*args, **kwargs)
        self.clean()
        super(CustomUser, self).save(update_fields=['username','email','password'])
    

EXPIRATION_PHONE = 2
EXPIRATION_EMAIL = 5
    
class CodeVerified(BaseModel):

    AUTH_TYPE = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE)
    )

    code = models.CharField(max_length=4, blank=True, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="verify_code")
    verify_type = models.CharField(max_length=31,choices=AUTH_TYPE)
    expiration_time = models.DateTimeField()
    code_status = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        if self.verify_type == VIA_EMAIL:
            self.expiration_time = datetime.now() + timedelta(minutes=EXPIRATION_EMAIL)
        else: 
            self.expiration_time = datetime.now() + timedelta(minutes=EXPIRATION_PHONE)

        super(CodeVerified, self).save(*args, **kwargs)




