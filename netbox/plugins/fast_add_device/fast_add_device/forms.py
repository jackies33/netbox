



from django import forms
import logging


from ipam.formfields import IPNetworkFormField
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import DynamicModelChoiceField,DynamicMultipleChoiceField
from dcim.models.sites import Location,Site
from dcim.models.racks import Rack
from dcim.models.devices import Platform,DeviceType,DeviceRole,Manufacturer,Device
from tenancy.models.tenants import Tenant
from tenancy.models.contacts import ContactRole


message_logger = logging.getLogger('recieved_messages')
message_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('/opt/netbox/netbox/plugins/file.log')
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)
message_logger.addHandler(file_handler)


class Device_Offline_PluginForm(NetBoxModelForm):

        choices_scheme = [(1, 'ssh'), (2, 'telnet')]
        ip_address = IPNetworkFormField(required=True,label='ip "0.0.0.0/0" ')#help_text='prefix form "0.0.0.0/0"',)
        device_name = forms.CharField(required=True, label='host name ')
        platform = DynamicModelChoiceField(required=True,label='platform ',queryset = Platform.objects.all())
        manufacturer = DynamicModelChoiceField(required=True, label='manufacturer ', queryset=Manufacturer.objects.all())
        device_type = DynamicModelChoiceField(required=True,label='device type ',queryset=DeviceType.objects.all())
        device_role = DynamicModelChoiceField(required=True,label='device role ',queryset=DeviceRole.objects.all())
        tenants = DynamicModelChoiceField(required=True,label='tenants ',queryset=Tenant.objects.all())
        site = DynamicModelChoiceField(required=True,label='site ',queryset=Site.objects.all())
        tg_resource_group = DynamicModelChoiceField(required=True, label='TG resource group',
                                                 initial=2,queryset=ContactRole.objects.all())
        map_resource_group = DynamicModelChoiceField(required=False, label='MAP resource group',
                                                  queryset=ContactRole.objects.all())
        name_of_establishment = forms.CharField(required=False, label='name of establishment')
        location = DynamicModelChoiceField(required=False,label='location ',queryset = Location.objects.all())
        racks = DynamicModelChoiceField(required=False,label='rack ',queryset = Rack.objects.all())
        conn_scheme = forms.ChoiceField(required=True,label='connection scheme ',choices=choices_scheme)
        interface_name = forms.CharField(required=True, label='mgmt interface name ')
        serial_number = forms.CharField(required=True, label='serial number ')

        class Meta:
            model = Location
            fields = ['ip_address','platform','device_type','device_role','tenants','site',
                      'location','racks','conn_scheme','interface_name','device_name','manufacturer','serial_number',
                      'tg_resource_group', 'map_resource_group' ,'name_of_establishment'
                      ]

class Device_Active_PluginForm(NetBoxModelForm):


                    choices_scheme = [(1, 'SSH'), (2, 'Telnet')]
                    ip_address = IPNetworkFormField(required=True,label='ip "0.0.0.0/0"')  # help_text='prefix form "0.0.0.0/0"',)
                    platform = DynamicModelChoiceField(required=True, label='platform', queryset=Platform.objects.all())
                    device_role = DynamicModelChoiceField(required=True, label='device role',queryset=DeviceRole.objects.all())
                    tenants = DynamicModelChoiceField(required=True, label='tenants', queryset=Tenant.objects.all())
                    site = DynamicModelChoiceField(required=True, label='site', queryset=Site.objects.all())
                    tg_resource_group = DynamicModelChoiceField(required=True, label='TG resource group',
                                                                initial=2, queryset=ContactRole.objects.all())
                    map_resource_group = DynamicModelChoiceField(required=False, label='MAP resource group',
                                                                 queryset=ContactRole.objects.all())
                    name_of_establishment = forms.CharField(required=False, label='name of establishment')
                    location = DynamicModelChoiceField(required=False,label='location ',queryset = Location.objects.all())
                    racks = DynamicModelChoiceField(required=False, label='rack', queryset=Rack.objects.all())
                    stack = forms.ChoiceField(choices=[(True, 'Stack'), (False, 'Not Stack')],
                                            required=True,label="is it stack?",initial=False)
                    #stack = forms.BooleanField(label='is it stack?', required=False)

                    class Meta:
                            model = Location
                            fields = ['ip_address', 'platform', 'device_role', 'tenants', 'site','location','racks', 'stack',
                                      'tg_resource_group', 'map_resource_group', 'name_of_establishment'
                                      ]


class Device_Change_Active_PluginForm(NetBoxModelForm):
    devices = []
    try:

        #devices = DynamicModelChoiceField(required=True, label='devices', queryset=Device.objects.all())
        devices = DynamicMultipleChoiceField(
            required=True,
            label='devices',
            choices=[(device.id, device.name) for device in Device.objects.all()]  # Генерация списка кортежей
        )
        #message_logger.info(f"Debug log:  data is {devices.choices} ")
        secondary_ip = forms.BooleanField(label='Secondary ip(only for b4com devices)', required=False)
        hostname = forms.BooleanField(label='hostname', required=False)
    except Exception as err:
        message_logger.info(f"Debug log: {err}")


    class Meta:
        model = Location
        fields = ['devices','hostname','secondary_ip']


class Device_ADD_CSV_PluginForm(forms.Form):
        csv_file = forms.FileField(label='Choose file', widget=forms.FileInput())





