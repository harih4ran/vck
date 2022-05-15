from django.db import models
from django.contrib.auth.models import AbstractUser
import random
import string
from io import BytesIO
import sys
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import math
import datetime

GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('T', 'TransGender'),
    )

class User(AbstractUser):
    name = models.CharField(max_length=500,blank=False,null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES,blank=False,null=True)
    age = models.CharField(max_length=500,null=True,blank=False)
    fathersname = models.CharField(max_length=500,null=True,blank=False)
    primary_phone = models.CharField(max_length=500,blank=False,null=True)
    second_phone = models.CharField(max_length=500,blank=True,null=True)
    address = models.TextField(blank=False,null=True)
    business = models.CharField(max_length=500,blank=False,null=True) 
    document = models.FileField(upload_to ='uploads/')
    photo = models.ImageField(upload_to="photo/",blank=True)
    vck_id = models.IntegerField(blank = True,unique=True)

    card_front = models.ImageField(upload_to="members/card_front",blank=True,null = True)
    card_back = models.ImageField(upload_to="members/card_back",blank=True,null = True)


    USERNAME_FIELD = 'username'
    REQUIRED_FILEDS = ['username']

    def save(self,*args,**kwargs):
        if User.objects.filter(vck_id=self.vck_id).exists():
            strings = "".join(random.choices(string.digits, k = 12))
            self.vck_id = strings
            super(User,self).save(*args, **kwargs)
            
        else:
            strings = "".join(random.choices(string.digits, k = 12))
            self.vck_id = strings
            super(User,self).save(*args, **kwargs)

        #image compression and 257 x 302
        try:
            # Opening the uploaded image
            im = Image.open(self.photo)

            output = BytesIO()

            x, y = im.size
            x2, y2 = math.floor(x - 50), math.floor(y - 20)
            im = im.resize((x2, y2), Image.ANTIALIAS)

            im = im.convert('RGB')

            # Resize/modify the image
            im = im.resize((257, 302), Image.ANTIALIAS)

            # after modifications, save it to the output
            im.save(output, format="JPEG", quality=30)
            output.seek(0)

            # change the imagefield value to be the newley modifed image value
            self.photo = InMemoryUploadedFile(
                output,
                "ImageField",
                "%s.jpg" % self.photo.name.split(".")[0],
                "image/jpeg",
                sys.getsizeof(output),
                None,
            )

            super(User, self).save(*args, **kwargs)
        except Exception as e:
            return
            super(User, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.vck_id)

PAYMENT_CHOICES = (
        ('P', 'pending'),
        ('F', 'failure'),
        ('S', 'success'),
    )

PLAN_TYPE_CHOICES = (
        ('S', 'silver'),
        ('G', 'gold'),
        ('P', 'platinam'),
    )

class Membership(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    status = models.CharField(max_length=100, choices=PAYMENT_CHOICES,blank=False,null=True)
    plan = models.CharField(max_length=100, choices=PLAN_TYPE_CHOICES,blank=False,null=True)
    date_ordered = models.DateTimeField(auto_now_add = True)
    complete = models.BooleanField(default=False,null=True,blank=False)
    transactionid = models.CharField(max_length=200,null=True,blank=True,unique=True)
    amount = models.IntegerField(default = 0,blank=True,null=True)

    def __str__(self):
        return str(self.id)