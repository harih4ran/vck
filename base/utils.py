from PIL import Image, ImageDraw, ImageFont
import os
import textwrap
from django.shortcuts import render,redirect
from io import BytesIO
import sys
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files import File
import qrcode


def generateID(request):
    try:
        name = request.user.name
        legalname = request.user.username
        fathersname = request.user.fathersname
        address = request.user.address
        mobile = request.user.primary_phone
        dob = str(request.user.age)
        business = request.user.business
        position = "Member"
        vck_id = str(request.user.vck_id)
        photo = request.user.photo

        # common
        path = os.getcwd()

        qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=3,
        border=4,
        )
        qr.add_data('Name - '+str(request.user.name))
        qr.add_data('Gender - '+str(request.user.gender))
        qr.add_data('Age - '+str(request.user.age))
        qr.add_data("Father's Name"+str(request.user.fathersname))
        qr.add_data('Address'+str(request.user.address))
        
        qr.make(fit=True)

        qrimg = qr.make_image(fill_color="black", back_color="white")
        # img.save(path+"/base/some_file.png")
        frontside = Image.open(path+"/base/front.jpeg")
        frontside_draw = ImageDraw.Draw(frontside)
        backside= Image.open(path+"/base/back.jpeg")
        backside_draw = ImageDraw.Draw(backside)

        #avator
        avator= Image.open(photo)
        frontside.paste(avator, (40, 245))
        backside.paste(qrimg,(753,410))
        
        # common 
        font = ImageFont.truetype(path+"/base/static/font.ttf",size=20)  
        
        # front page design
        frontside_draw.text((470, 290),name,(0,0,0),font=font)
        frontside_draw.text((470, 375),position,(0,0,0),font=font)
        frontside_draw.text((755, 30),vck_id,(0,0,0),font=font)

        # frontside image save into card_front field
        card_front_tempfile_io = BytesIO()
        frontside.save(card_front_tempfile_io, format='JPEG')
        save_front_image = request.user
        save_front_image.card_front = InMemoryUploadedFile(card_front_tempfile_io,None,legalname+"_frontside"+".jpeg","image/jpeg",sys.getsizeof(card_front_tempfile_io),None)
        save_front_image.save()
        # frontside.show()
        # frontside.save(legalname+"_frontside"+".jpeg")
        
        # back page design
        backside_draw.text((225, 210),legalname,(0,0,0),font=font)
        backside_draw.text((225, 265),fathersname,(0,0,0),font=font)
        backside_draw.text((225, 320),mobile,(0,0,0),font=font)
        backside_draw.text((225, 380),address,(0,0,0),font=font)
        backside_draw.text((740, 210),dob,(0,0,0),font=font)
        backside_draw.text((740, 265),business,(0,0,0),font=font,line_length=10)       
        # backside.show()

        # getimage = backside.save(legalname+"_backside"+".jpeg")

        # backside image save into card_back field
        card_back_tempfile_io = BytesIO()
        backside.save(card_back_tempfile_io, format='JPEG')
        save_back_image = request.user
        save_back_image.card_back = InMemoryUploadedFile(card_back_tempfile_io,None,legalname+"_backside"+".jpeg","image/jpeg",sys.getsizeof(card_back_tempfile_io),None)
        save_back_image.save()

        return True
    except:
        return False