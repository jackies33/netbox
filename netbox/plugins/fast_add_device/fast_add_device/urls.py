


from django.urls import path

from .views import Add_Device_Active_View,Add_Device_Offline_View,\
    Change_Device_Active_View ,get_location,get_racks,\
    Add_Device_CSV_Online_View,Add_Sites_CSV_View,Add_Prefixes_CSV_View

urlpatterns = [
    path('add_device_active/', Add_Device_Active_View.as_view(), name='add_device_active'),
    path('add_device_offline/', Add_Device_Offline_View.as_view(), name='add_device_offline'),
    path('add_device_csv/',Add_Device_CSV_Online_View.as_view(),name='add_device_csv'),
    path('add_sites_csv/',Add_Sites_CSV_View.as_view(),name='add_sites_csv'),
    path('add_prefix_csv/',Add_Prefixes_CSV_View.as_view(),name='add_prefix_csv'),
    path('edit_device_active/',Change_Device_Active_View.as_view(),name='edit_device_active'),
    path('get_location/', get_location, name='get_location'),
    path('get_racks/', get_racks, name='get_racks'),
]


