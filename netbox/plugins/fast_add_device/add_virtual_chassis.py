

import time
import pynetbox
from .tgbot import tg_bot
import datetime
from .my_pass import netbox_url,netbox_api_token


class ADD_NB_VC():
            """
            class for add data to NetBox over RestApi
            """

            def __init__(self, name_device, site, location, tenants, device_role,
                     manufacturer,platform, device_type,
                     primary_ip, interface_name,conn_scheme, management ,racks, list_serial,
                     stack_enable):

                self.status = 'active'
                self.type_of_interface = 'virtual'
                self.aobjt = 'dcim.interface'
                self.name_device = name_device
                self.site = site
                self.location = location
                self.tenants = tenants
                self.device_role = device_role
                self.manufacturer = manufacturer
                self.platform = platform
                self.device_type = device_type
                self.primary_ip = primary_ip
                self.interface_name = interface_name
                self.conn_scheme = conn_scheme
                self.management = management
                self.racks = racks
                self.list_serial = list_serial
                self.stack_enable = stack_enable

            def add_vc(self, *args):
                print("<<< Start add_virtual_chassis.py >>>")
                nb = pynetbox.api(url=netbox_url,
                                  token=netbox_api_token)
                nb.http_session.verify = False

                stack_amount = ''
                for member in self.list_serial:
                    mem_id = member['member_id']
                    sn_numb = member['sn_number']
                    master = member['master']
                    host_name = f'{self.name_device}.{mem_id}'
                    try:
                        nb.dcim.devices.create(
                            name=host_name,
                            status=str(self.management).lower(),
                            site=self.site,
                            device_role=self.device_role,
                            manufacturer=self.manufacturer.title(),
                            platform=self.platform,
                            device_type=self.device_type,
                            primary_ip=self.primary_ip,
                            tenant=self.tenants,
                            custom_fields={'Connection_Scheme': str(self.conn_scheme)},
                        )
                    except Exception as err:
                        print(f'device {self.name_device} is already done or \n {err}')
                        return [False, err]
                        pass


                    time.sleep(1)
                    id_device = nb.dcim.devices.get(name=host_name)
                    try:  # updating device
                        if master == True:

                            try:
                                nb.dcim.interfaces.create(
                                    device=id_device.id,
                                    name=self.interface_name,
                                    type=self.type_of_interface,
                                    enabled=True,
                                )
                            except Exception as err:
                                print(f'interface {self.interface_name} is already done \n\n {err} \n\n\ ')
                                return [False, err]
                            time.sleep(1)
                            interface = nb.dcim.interfaces.get(name=self.interface_name, device_id=id_device.id)
                            interface_id = interface['id']
                            try:
                                nb.ipam.ip_addresses.create(
                                    address=self.primary_ip,
                                    status=self.status,
                                    assigned_object_type=self.aobjt,
                                    assigned_object_id=interface_id,
                                )
                            except Exception as err:
                                print(f'Error for create an ip_address {err}')
                                return [False, err]
                            time.sleep(1)

                            try:
                                vc_id = nb.dcim.virtual_chassis.get(name=self.name_device)
                            except Exception:
                                nb.dcim.virtual_chassis.create(name=self.name_device)
                                time.sleep(1)
                                vc_id = nb.dcim.virtual_chassis.get(name=self.name_device)
                                pass
                            if vc_id == None:
                                nb.dcim.virtual_chassis.create(name=self.name_device)
                                vc_id = nb.dcim.virtual_chassis.get(name=self.name_device)
                            else:
                                pass
                            try:
                                id_device.update({'virtual_chassis': {'name': self.name_device}, 'vc_position': mem_id})
                            except Exception as err:
                                print(err)
                                pass
                            vc_id.update({'master': {'id': id_device.id}})
                            if self.location != None:
                                id_device.update({'location': self.location})
                            else:
                                pass
                            if self.racks != None:
                                id_device.update({'rack': self.racks})
                            else:
                                pass
                            id_device.update({'serial': sn_numb})

                            try:
                                id_device.update({'primary_ip4': {'address': self.primary_ip}})
                            except Exception as err:
                                print(f"in update device  - - - {err}")
                                return [False, err]
                            else:
                                print(f"Succesfull create and update device - {host_name} and send to telegram chat")
                                message = (
                                    f'Netbox.handler [ "Event_Add Device_Stack" ]\n Device_Stack Name - [ "{host_name}" ] '
                                    f'\n ip_address - [ "{self.primary_ip}" ] \n Time: [ "{datetime.datetime.now()}" ]')
                                sender = tg_bot(message)
                                sender.tg_sender()
                            stack_amount = stack_amount + f' "{host_name}"'

                        elif master == False:

                            try:
                                vc_id = nb.dcim.virtual_chassis.get(name=self.name_device)
                            except Exception:
                                nb.dcim.virtual_chassis.create(name=self.name_device)
                                time.sleep(1)
                                vc_id = nb.dcim.virtual_chassis.get(name=self.name_device)
                                pass
                            if vc_id == None:
                                nb.dcim.virtual_chassis.create(name=self.name_device)
                                vc_id = nb.dcim.virtual_chassis.get(name=self.name_device)
                            else:
                                pass
                            try:
                                id_device.update({'virtual_chassis': {'name': self.name_device}, 'vc_position': mem_id})
                            except Exception as err:
                                print(err)
                                pass
                            if self.location != None:
                                id_device.update({'location': self.location})
                            else:
                                pass
                            if self.racks != None:
                                id_device.update({'rack': self.racks})
                            else:
                                pass
                            try:
                                 id_device.update({'serial': sn_numb})
                            except Exception as err:
                                print(f"in update device  - - - {err}")
                                return [False, err]
                            else:
                                print(f"Succesfull create and update device - {host_name} and send to telegram chat")
                                #message = (
                                #    f'Netbox.handler [ "Event_Add Device_Stack" ]\n Device_Stack Name - [ "{host_name}" ] '
                                #    f'\n ip_address - [ "None" ] \n Time: [ "{datetime.datetime.now()}" ]')
                                #sender = tg_bot(message)
                                #sender.tg_sender()
                            stack_amount = stack_amount + f' "{host_name}"'

                    except Exception as err:
                        print(f"in update device  - - - {err}")
                        return [False, err]
                        pass



                return [True, stack_amount]

if __name__ == '__main__':
                print("__main__")




