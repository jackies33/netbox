

from django.urls import path
from .views import Add_Device_Active_View, Add_Device_Offline_View

urlpatterns = [
    path('add_device_active/', Add_Device_Active_View.as_view(), name='add_device_active'),
    path('add_device_offline/', Add_Device_Offline_View.as_view(), name='add_device_offline'),
]
