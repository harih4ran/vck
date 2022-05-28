from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from base.forms import *
from django.contrib.auth.decorators import login_required
import razorpay
from .utils import generateID
from django.contrib import messages
from .models import User,Membership
import json
import hashlib
import hmac
import base64
import random
import string
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse,HttpResponse
import os

def index(request):  
    return render(request,'index.html')

@login_required(login_url="login")
def dashboard(request):
    if request.user.is_authenticated:
        member =  Membership.objects.filter(member = request.user,complete=True,status = "success")
        context = {
            "member":member
        }
        return render(request,'dashboard.html',context)
    else:
        return redirect('login')

@login_required(login_url="login")
def profile(request):
    if request.user.is_authenticated:
        return render(request,'profile.html')
    else:
        return redirect('login')

@login_required(login_url="login")
def generateid(request):
    if request.user.is_authenticated:
        if Membership.objects.filter(member = request.user,complete=True,status = "success"):
            if generateID(request):
                messages.info(request, '*VCK ID Card Generated Successfully')
                return redirect('dashboard')
            else:
                messages.info(request, '*Please Try again')
                return redirect('dashboard')
        else:
            return redirect('payment')
        return render(request,'dashboard.html')

def register(request):
    if request.method == 'POST':
        form =RegisterForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form=RegisterForm()        

    return render(request,'registration/register.html',{'form':form}) 

@csrf_exempt
def process_order(request):
    transactionid = datetime.datetime.now().timestamp()
    data = request.POST
    if True:
        member = request.user
        membership,created = Membership.objects.get_or_create(member=member,complete=False)
        membership.transactionid = transactionid
        payment_id = data['razorpay_payment_id']
        client = razorpay.Client(
                auth=("rzp_test_MKMFi5canwMhSE","0FwZn6zOTvYVAYwo3M84T3YE"))
        status = client.payment.fetch(payment_id)
        status['id']
        amount = int(status['amount']/100)
        
        if int(amount) == int(200):
            # client = razorpay.Client(
            #     auth=("rzp_test_MKMFi5canwMhSE","0FwZn6zOTvYVAYwo3M84T3YE"))
            # payment = client.order.create({'amount':int(200), 'currency':'INR', 'payment_capture':0})
            membership.complete = True
            membership.amount = float(amount)
            if amount == 200:
                membership.plan = 'silver'
            elif amount == 300:
                membership.plan = 'gold'
            elif amount == 500:
                membership.plan = 'platinam'
        else:
            messages.info(request,"Don't try to tamper the values")
        membership.status = 'success'
        membership.save()
        return redirect('dashboard')
    else:
        print("User not logged in ..")
    return JsonResponse("process complete",safe=False)
    # data = json.loads(request.body)
    # print(data)
    # if request.user.is_authenticated:
    #     member = request.user
    #     membership,created = Membership.objects.get_or_create(member=member,complete=False)
    #     membership.transactionid = transactionid
    #     amount = data['amount']

    #     if str(amount) == str(200):
    #         client = razorpay.Client(
    #             auth=("rzp_test_MKMFi5canwMhSE","0FwZn6zOTvYVAYwo3M84T3YE"))
    #         payment = client.order.create({'amount':int(200), 'currency':'INR', 'payment_capture':0})
    #         membership.complete = True
    #         membership.amount = float(amount)
    #         if amount == 200:
    #             membership.plan = 'silver'
    #     else:
    #         messages.info(request,"Don't try to tamper the values")
    #     membership.save()
    # else:
    #     print("User not logged in ..")
    # return JsonResponse("process complete",safe=False)

@csrf_exempt
def payment_status(request):

    response = request.POST

    params_dict = {
        'razorpay_payment_id' : response['razorpay_payment_id'],
        'razorpay_order_id' : response['razorpay_order_id'],
        'razorpay_signature' : response['razorpay_signature']
    }
    client = razorpay.Client(auth=("rzp_test_MKMFi5canwMhSE","0FwZn6zOTvYVAYwo3M84T3YE"))

    # VERIFYING SIGNATURE
    try:
        status = client.utility.verify_payment_signature(params_dict)
        return render(request, 'order_summary.html', {'status': 'Payment Successful'})
    except:
        return render(request, 'order_summary.html', {'status': 'Payment Faliure!!!'})

secretKey = "6c3ce67a838871e23c083fd2df5a27d6b2577196"
def handlerequest(request):
    mode = "TEST" 
    strings = "".join(random.choices(string.digits, k = 12))
    postData = {
        "appId" : '16528874af4d9cea70ac4d6560882561', 
        "orderId" : strings, 
        "orderAmount" : "200", 
        "orderCurrency" : "INR", 
        "orderNote" : "Membership Payment", 
        "customerName" : request.user.username, 
        "customerPhone" : request.user.primary_phone, 
        "customerEmail" : "enquiry@vck.enigmatn.in", 
        "returnUrl" : request.headers['Origin']+'/handleresponse?id='+str(request.user.id), 
        "notifyUrl" : request.headers['Origin']+'/handleresponse'
    }
    sortedKeys = sorted(postData)
    signatureData = ""
    for key in sortedKeys:
        signatureData += key+postData[key]
    message = signatureData.encode('utf-8')
    secret = secretKey.encode('utf-8')
    signature = base64.b64encode(hmac.new(secret,message,digestmod=hashlib.sha256).digest()).decode("utf-8")
    if mode == 'PROD': 
        url = "https://www.cashfree.com/checkout/post/submit"
    else: 
        url = "https://test.cashfree.com/billpay/checkout/post/submit"
    return render(request,'request.html', {"postData" :postData,"signature" :signature,"url": url})
    
@csrf_exempt
def handleresponse(request):
    postData = {
        "orderId" : request.POST.get('orderId'), 
        "orderAmount" : request.POST.get('orderAmount'), 
        "referenceId" : request.POST.get('referenceId'), 
        "txStatus" : request.POST.get('txStatus'), 
        "paymentMode" : request.POST.get('paymentMode'), 
        "txMsg" : request.POST.get('txMsg'), 
        "signature" : request.POST.get('signature'), 
        "txTime" : request.POST.get('txTime')
    }

    signatureData = ""
    signatureData = postData['orderId'] + postData['orderAmount'] + postData['referenceId'] + postData['txStatus'] + postData['paymentMode'] + postData['txMsg'] + postData['txTime']

    message = signatureData.encode('utf-8')
    # get secret key from your config
    secret = secretKey.encode('utf-8')
    computedsignature = base64.b64encode(hmac.new(secret,message,digestmod=hashlib.sha256).digest()).decode('utf-8')   
    transactionid = datetime.datetime.now().timestamp()
    userid = request.GET.get('id')
    amount = 200
    try:
        member = User.objects.get(id = userid)
    except:
        return redirect('dashboard')
    membership,created = Membership.objects.get_or_create(member=member,complete=False)
    membership.transactionid = transactionid
    membership.complete = True
    membership.amount = float(amount)
    if amount == 200:
        membership.plan = 'silver'
    elif amount == 300:
        membership.plan = 'gold'
    elif amount == 500:
        membership.plan = 'platinam'

    membership.status = 'success'
    membership.save()
    return render(request,'response.html', {"postData" :postData,"computedsignature" : computedsignature})

def Profileupdate(request): 
    instance = User.objects.get(id=request.user.id)
    if request.method == 'POST':
        data = request.POST
        name = data.get('name')
        fathersname = data.get('fathersname')
        age = data.get('age')
        gender = data.get('gender')
        address = data.get('address')
        business = data.get('business')
        primary_phone = data.get('primary_phone')
        second_phone = data.get('second_phone')
        instance.name = name
        instance.username = name
        instance.fathersname = fathersname
        instance.age = age
        instance.address = address
        instance.gender = gender
        instance.business = business
        instance.primary_phone = primary_phone
        instance.second_phone = second_phone
        instance.save()
        return redirect('dashboard')
    else:
        return redirect('dashboard')       

def FrontDownload(request):
    if request.user.is_authenticated:
        image = request.user
        image_buffer = open(request.user.card_front.path, "rb").read()
        response = HttpResponse(image_buffer, content_type='application/jpeg');
        response['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(request.user.card_front.path)
        return response
    else:
        return redirect('dashboard')
    
def BackDownload(request):
    if request.user.is_authenticated:
        image = request.user
        image_buffer = open(request.user.card_back.path, "rb").read()
        response = HttpResponse(image_buffer, content_type='application/jpeg');
        response['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(request.user.card_back.path)
        return response
    else:
        return redirect('dashboard')
