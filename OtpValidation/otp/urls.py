
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('login/',views.CustomLogin,name='login'),
    path('register/',views.register,name='register'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('registration_success/', views.registration_success, name='registration_success'),

]
