from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',views.index,name="index"),
    path('login',auth_views.LoginView.as_view(),name="login"),
    path('logout',auth_views.LogoutView.as_view(),name="logout"),
    path('register',views.register,name="register"),
    path('dashboard',views.dashboard,name="dashboard"),
    path('profile',views.profile,name="profile"),
    path('profileupdate',views.Profileupdate,name="profileupdate"),
    path('generateid',views.generateid,name="generateid"),
    # path('process_order/',views.process_order,name="process_order"),
    # path('payment_status', views.payment_status, name = 'payment_status'),
    path('handlerequest', views.handlerequest, name = 'handlerequest'),
    path('handleresponse', views.handleresponse, name = 'handleresponse'),
]