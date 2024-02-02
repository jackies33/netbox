



from django import forms
from ipam.formfields import IPNetworkFormField
#from django.core.validators import RegexValidator
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import DynamicModelChoiceField
from dcim.models.sites import Location,Site
from dcim.models.racks import Rack
from dcim.models.devices import Platform,DeviceType,DeviceRole,Manufacturer
from tenancy.models.tenants import Tenant
#from ipam.forms import IPAddressForm

class Device_Offline_PluginForm(NetBoxModelForm):

        #choices_management = [(1, 'Active'), (2, 'Offline')]
        choices_scheme = [(1, 'SSH'), (2, 'Telnet')]
        #ip_address = forms.GenericIPAddressField(protocol='IPv4')
        ip_address = IPNetworkFormField(required=True,label='ip "0.0.0.0/0"')#help_text='prefix form "0.0.0.0/0"',)
        device_name = forms.CharField(required=True, label='host name')
        platform = DynamicModelChoiceField(required=True,label='platform',queryset = Platform.objects.all())
        manufacturer = DynamicModelChoiceField(required=True, label='manufacturer', queryset=Manufacturer.objects.all())
        device_type = DynamicModelChoiceField(required=True,label='device type',queryset=DeviceType.objects.all())
        device_role = DynamicModelChoiceField(required=True,label='device role',queryset=DeviceRole.objects.all())
        tenants = DynamicModelChoiceField(required=True,label='tenants',queryset=Tenant.objects.all())
        site = DynamicModelChoiceField(required=True,label='site',queryset=Site.objects.all())
        location = DynamicModelChoiceField(required=False,label='location',queryset = Location.objects.all())
        racks = DynamicModelChoiceField(required=False,label='rack',queryset = Rack.objects.all())
        conn_scheme = forms.ChoiceField(required=True,label='connection scheme',choices=choices_scheme)
        interface_name = forms.CharField(required=True, label='mgmt interface name')

        class Meta:
            model = Location
            fields = ['ip_address','platform','device_type','device_role','tenants','site',
                      'location','racks','conn_scheme','interface_name','device_name','manufacturer']

class Device_Active_PluginForm(NetBoxModelForm):

                    #choices_management = [(1, 'Active'), (2, 'Offline')]
                    choices_scheme = [(1, 'SSH'), (2, 'Telnet')]
                    # ip_address = forms.GenericIPAddressField(protocol='IPv4')
                    ip_address = IPNetworkFormField(required=True,label='ip "0.0.0.0/0"')  # help_text='prefix form "0.0.0.0/0"',)
                    platform = DynamicModelChoiceField(required=True, label='platform', queryset=Platform.objects.all())
                    device_role = DynamicModelChoiceField(required=True, label='device role',queryset=DeviceRole.objects.all())
                    tenants = DynamicModelChoiceField(required=True, label='tenants', queryset=Tenant.objects.all())
                    site = DynamicModelChoiceField(required=True, label='site', queryset=Site.objects.all())
                    location = DynamicModelChoiceField(required=False, label='location',queryset=Location.objects.all())
                    racks = DynamicModelChoiceField(required=False, label='rack', queryset=Rack.objects.all())
                    stack = forms.BooleanField(label='is it stack?', required=False)

                    class Meta:
                            model = Location
                            fields = ['ip_address', 'platform', 'device_role', 'tenants', 'site','location','racks', 'stack']

"""
class RackForm(forms.ModelForm):
    location = forms.ModelChoiceField(queryset=Location.objects.all(), label='location')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['racks'].queryset = Rack.objects.filter(location=self.instance.location)
        else:
            self.fields['racks'].queryset = Rack.objects.none()

    class Meta:
        model = Rack
        fields = ['location', 'racks']
"""

