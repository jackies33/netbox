

import time
import pynetbox
import datetime


from ..tgbot import tg_bot
from ..my_pass import netbox_url,netbox_api_token


class ADD_NB_VC():
            """
            class for add data to NetBox over RestApi
            """

            def __init__(self, **kwargs):
                """
                :param kwargs:
                """
                self.aobjt = 'dcim.interface'
                self.status = 'active'
                self.type_of_interface = 'virtual'
                self.nb=pynetbox.api(url=netbox_url,
                                  token=netbox_api_token)
                self.nb.http_session.verify = False

            def add_vc(self, **kwargs):
                print("<<< Start add_virtual_chassis.py >>>")
                data = kwargs['data']['add']
                mgmt = data['management_status']
                conn_scheme = data['conn_scheme']
                # conn_scheme,str(management[1].lower))
                if mgmt == 1:
                    mgmt = "Active"
                elif mgmt == 2:
                    smgmt = "Offline"
                else:
                    mgmt = "Active"
                if conn_scheme == '1':
                    conn_scheme = "ssh"
                elif conn_scheme == '2':
                    conn_scheme = "telnet"
                else:
                    conn_scheme = 'ssh'
                edit_data = kwargs['data']['edit']
                add_data = kwargs['data']['add']

                if kwargs['purpose_value'] == 'edit':
                      pass
                elif kwargs['purpose_value'] == 'add':
                    stack_amount = ''
                    print(data)
                    for member in add_data['list_serial_device']:
                        mem_id = member['member_id']
                        sn_numb = member['sn_number']
                        master = member['master']
                        host_name = f'{add_data["device_name"]}.{mem_id}'
                        try:
                            self.nb.dcim.devices.create(
                                name=host_name,
                                status=mgmt.lower(),
                                site=add_data['site'],
                                device_role=add_data['device_role'],
                                manufacturer=add_data['manufacturer'].title(),
                                platform=add_data['platform'],
                                device_type=add_data['device_type'],
                                primary_ip=add_data['primary_ip'],
                                tenant=add_data['tenants'],
                                custom_fields={'Connection_Scheme': str(conn_scheme),'TG_Group':add_data['tg_resource_group']},
                            )
                        except Exception as err:
                            print(f'device {add_data["device_name"]} is already done or \n {err}')
                            return [False, err]
                            pass
                        time.sleep(1)
                        id_device = self.nb.dcim.devices.get(name=host_name)
                        try:  # updating device
                            if master == True:
                                try:
                                    self.nb.dcim.interfaces.create(
                                        device=id_device.id,
                                        name=add_data['interface_name'],
                                        type=self.type_of_interface,
                                        enabled=True,
                                    )
                                except Exception as err:
                                    print(f'interface {add_data["interface_name"]} is already done \n\n {err} \n\n\ ')
                                    return [False, err]
                                time.sleep(1)
                                interface = self.nb.dcim.interfaces.get(name=add_data['interface_name'], device_id=id_device.id)
                                interface_id = interface['id']
                                try:
                                    self.nb.ipam.ip_addresses.create(
                                        address=add_data['primary_ip'],
                                        status=self.status,
                                        assigned_object_type=self.aobjt,
                                        assigned_object_id=interface_id,
                                    )
                                except Exception as err:
                                    print(f'Error for create an ip_address {err}')
                                    return [False, err]
                                time.sleep(1)

                                try:
                                    vc_id = self.nb.dcim.virtual_chassis.get(name=add_data['device_name'])
                                except Exception:
                                    self.nb.dcim.virtual_chassis.create(name=add_data['device_name'])
                                    time.sleep(1)
                                    vc_id = self.nb.dcim.virtual_chassis.get(name=add_data['device_name'])
                                    pass
                                if vc_id == None:
                                    self.nb.dcim.virtual_chassis.create(name=add_data['device_name'])
                                    vc_id = self.nb.dcim.virtual_chassis.get(name=add_data['device_name'])
                                else:
                                    pass
                                try:
                                    id_device.update({'virtual_chassis': {'name': add_data['device_name']}, 'vc_position': mem_id})
                                except Exception as err:
                                    print(err)
                                    pass
                                vc_id.update({'master': {'id': id_device.id}})
                                if add_data['location'] != None:
                                    id_device.update({'location': add_data['location']})
                                else:
                                    pass
                                if add_data['rack'] != None:
                                    id_device.update({'rack': add_data['rack']})
                                else:
                                    pass
                                if data['map_resource_group'] != None:
                                    id_device.update({'custom_fields': {'MAP_Group': data['map_resource_group']}})
                                else:
                                    pass
                                if data['name_of_establishment'] != None:
                                    id_device.update({'custom_fields': {'Name_of_Establishment': data['name_of_establishment']}})
                                else:
                                    pass
                                try:
                                    id_device.update({'serial': sn_numb})
                                except Exception as err:
                                    pass

                                try:
                                    id_device.update({'primary_ip4': {'address': add_data['primary_ip']}})
                                except Exception as err:
                                    print(f"in update device  - - - {err}")
                                    return [False, err]
                                else:
                                    print(f"Succesfull create and update device - {host_name} and send to telegram chat")
                                    message = (
                                        f'Netbox.handler [ "Event_Add Device_Stack" ]\n Device_Stack Name - [ "{host_name}" ] '
                                        f'\n ip_address - [ "{add_data["primary_ip"]}" ] \n Time: [ "{datetime.datetime.now()}" ]')
                                    sender = tg_bot(message)
                                    sender.tg_sender()
                                stack_amount = stack_amount + f' "{host_name}"'

                            elif master == False:

                                try:
                                    vc_id = self.nb.dcim.virtual_chassis.get(name=add_data['device_name'])
                                except Exception:
                                    self.nb.dcim.virtual_chassis.create(name=add_data['device_name'])
                                    time.sleep(1)
                                    vc_id = self.nb.dcim.virtual_chassis.get(name=add_data['device_name'])
                                    pass
                                if vc_id == None:
                                    self.nb.dcim.virtual_chassis.create(name=add_data['device_name'])
                                    vc_id = self.nb.dcim.virtual_chassis.get(name=add_data['device_name'])
                                else:
                                    pass
                                try:
                                    id_device.update({'virtual_chassis': {'name': add_data['device_name']}, 'vc_position': mem_id})
                                except Exception as err:
                                    pass
                                if add_data['location'] != None:
                                    id_device.update({'location': add_data['location']})
                                else:
                                    pass
                                if add_data['rack'] != None:
                                    id_device.update({'rack': add_data['rack']})
                                else:
                                    pass
                                if data['map_resource_group'] != None:
                                    id_device.update({'custom_fields': {'MAP_Group': data['map_resource_group']}})
                                else:
                                    pass
                                try:
                                     id_device.update({'serial': sn_numb})
                                except Exception as err:
                                    print(f"in update device  - - - {err}")
                                    return [False, err]
                                else:
                                    print(f"Succesfull create and update device - {host_name} and send to telegram chat")
                                stack_amount = stack_amount + f' "{host_name}"'

                        except Exception as err:
                            print(f"in update device  - - - {err}")
                            return [False, err]
                            pass



                    return [True, stack_amount]



