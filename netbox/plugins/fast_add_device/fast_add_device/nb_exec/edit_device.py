


import time
import pynetbox
import datetime

from ..my_pass import netbox_url,netbox_api_token
from .add_virtual_chassis import ADD_NB_VC




class EDIT_NB():

        """
        class for add data to NetBox over RestApi
        """

        def __init__(self, **kwargs):
            """
            Initialize the values

            """
            self.nb = pynetbox.api(url=netbox_url,
                              token=netbox_api_token)
            self.nb.http_session.verify = False

            self.template_for_interface = {
                'interface_name': 'name',
            }
            self.template_for_device = {
                'device_id': 'id',
                'device_name': 'name',
                'site': 'site.id',
                'location': 'location.id',
                'rack': 'rack.id',
                'tenants': 'tenant.id',
                'device_role': 'device_role.id',
                'device_type': 'device_type.id',
                'manufacturer': 'device_type.manufacturer',
                'platform': 'platform.id',
                'list_serial_device': 'serial',
                'primary_ip': 'primary_ip.address',
                'management_status': 'status.label',
            }

        def edit_device(self,**kwargs):
            print("<<< Start edit_device.py >>>")
            edit_data = kwargs['data']['edit']
            add_data = kwargs['data']['add']
            diff_data = kwargs['data']['diff']
            device_id = edit_data['device_id']
            device = self.nb.dcim.devices.get(device_id)
            interface = self.nb.dcim.interfaces.get(device=edit_data['device_name'])
            for key, value in diff_data.items():
                if key in self.template_for_device:
                    templ_value = self.template_for_device[key]
                    if templ_value == 'serial':
                        value = str(value[0]['sn_number'])
                        edit_value = f"device.{templ_value} = '{value}'"
                        exec(edit_value)
                    elif templ_value == 'device_name':
                        edit_value = f"device.{templ_value} = '{value}'"
                        exec(edit_value)
                    elif 'manufacrturer' or 'primary_ip':
                        edit_value = f"device.{templ_value} = '{value}'"
                        exec(edit_value)
                    else:
                        edit_value = f"device.{templ_value} = {value}"
                        exec(edit_value)
                elif key in self.template_for_interface:
                    templ_value = self.template_for_interface[key]
                    edit_value = f"interface.{templ_value} = '{value}'"
                    exec(edit_value)
            device.save()
            interface.save()
            return [True, add_data["device_name"]]

        def edit_vc(self,**kwargs):
            print("<<< Start edit_device.py >>>")
            edit_data = kwargs['data']['edit']
            add_data = kwargs['data']['add']
            diff_data = kwargs['data']['diff']
            device_id = edit_data['device_id']

            try:
                device = self.nb.dcim.devices.get(device_id)
                interface = self.nb.dcim.interfaces.get(device=edit_data['device_name'])
            except Exception as err:
                pass
            try:
                if diff_data['list_serial_device']:
                    try:
                            vc = self.nb.dcim.virtual_chassis.get(id=edit_data['virtual_chassis'])
                    except Exception as err:
                        pass
                    try:
                        vc = self.nb.dcim.virtual_chassis.get(id=edit_data['virtual_chassis'])
                        vc.delete()
                    except Exception as err:
                        print(err)
                        pass
                    for member in edit_data['list_serial_device']:
                        mem_id = member['member_id']
                        device_name = edit_data['device_name']
                        host_name = f'{device_name}.{mem_id}'
                        try:
                            device = self.nb.dcim.devices.get(name=host_name)
                        except Exception as err:
                            pass
                        try:
                            device.delete()
                        except Exception as err:
                            print(err)
                            pass
                    time.sleep(2)
                    kwargs.update({'purpose_value': 'add'})
                    call = ADD_NB_VC()
                    call.add_vc(**kwargs)

            except KeyError as err:
                print({err},'without vc edit')


            return [True,add_data['device_name']]



