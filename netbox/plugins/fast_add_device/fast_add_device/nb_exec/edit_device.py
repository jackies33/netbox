


import time
import pynetbox
import datetime
import logging





from ..my_pass import netbox_url,netbox_api_token
from .add_virtual_chassis import ADD_NB_VC




message_logger = logging.getLogger('recieved_messages')
message_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('/opt/netbox/netbox/plugins/file.log')
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)
message_logger.addHandler(file_handler)




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

            self.aobjt = 'dcim.interface'
            # self.status_secondary_ip = 'reserved'
            self.status_secondary_ip = 'active'
            self.type_of_interface = 'virtual'
            self.name_of_interface = 'lo'
            self.secondary_iface_label = 'secondary'


            self.template_for_device = {
                'device_id': 'id',
                'device_name': 'name',
                'site': 'site.id',
                'location': 'location.id',
                'rack': 'rack.id',
                'tenants': 'tenant.id',
                'device_role': 'role.id',
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
            diff_data_list_target = kwargs['data']['target_list']
            device_id = int(edit_data['device_id'])
            message_logger.info(f"Debug log#1 in edit_device.py: {device_id}")
            device = self.nb.dcim.devices.get(id=device_id)
            #device = self.nb.dcim.devices.filter(id=device_id)
            #device = self.nb.dcim.devices.filter(id=7188)
            #interface = self.nb.dcim.interfaces.get(device=edit_data['device_name'])
            #message_logger.info(f"Debug log#1 in edit_device.py: {kwargs}")
            for target in diff_data_list_target:
                message_logger.info(f"Debug log#2 in edit_device.py: {device,add_data}")
                if target == "hostname":
                    device.name(add_data['device_name'])
                elif target == 'secondary_ip':

                    secondary_ip = add_data['secondary_ip']
                    message_logger.info(f"Debug log#3 in edit_device.py: {secondary_ip}")
                    if secondary_ip:
                        try:
                            message_logger.info(f"Debug log#4 in edit_device.py: {device_id}")
                            self.nb.dcim.interfaces.create(  # add interface and belong it to device which created before
                                device=device.id,
                                name=self.name_of_interface,
                                type=self.type_of_interface,
                                enabled=True,
                                label=self.secondary_iface_label
                            )
                            interface = self.nb.dcim.interfaces.get(name=self.name_of_interface, device_id=device.id)
                            if interface:
                                interface_id = interface['id']
                                self.nb.ipam.ip_addresses.create(
                                    # add ip_address and belong it to interface which created before
                                    address=secondary_ip,
                                    status=self.status_secondary_ip,
                                    assigned_object_type=self.aobjt,
                                    assigned_object_id=interface_id,
                                )
                        except Exception as err:
                            print(err)

            return [True,add_data['device_name']]



