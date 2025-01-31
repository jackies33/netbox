


###external pack
import time
import pynetbox
import datetime


##internal pack
from ..tgbot import tg_bot
from ..my_pass import netbox_url,netbox_api_token
from .add_virtual_chassis import ADD_NB_VC


class ADD_NB():

        """
        class for add data to NetBox over RestApi
        """

        def __init__(self, **kwargs):

            self.aobjt = 'dcim.interface'
            self.status = 'active'
            self.type_of_interface = 'virtual'
            self.status_secondary_ip = 'active'
            self.name_of_interface_secondary = 'lo'
            self.secondary_iface_label = 'secondary'
            self.nb = pynetbox.api(url=netbox_url,
                                   token=netbox_api_token)
            self.nb.http_session.verify = False
            """
            Initialize the values
            """

        def add_device(self,**kwargs):
            print("<<< Start add_device.py >>>")
            print(kwargs)
            # print('this is add_device.py!!!!')
            data = kwargs['data']['add']
            mgmt = data['management_status']
            conn_scheme = data['conn_scheme']
            find_ip = self.nb.ipam.ip_addresses.filter(address=data['primary_ip'])
            if find_ip:
                for i in find_ip:
                    id_ip = i.id
                    device = self.nb.dcim.devices.filter(primary_ip4_id=int(id_ip))
                    if device:
                        for dev in device:
                            return [False,f"Device with name '{data['device_name']}' already exists , check next device - {dev}"]
                    else:
                        pass
            else:
                pass
            # conn_scheme,str(management[1].lower))
            if mgmt == 1:
                mgmt = "Active"
            elif mgmt == 2:
                mgmt = "Offline"
            else:
                mgmt = "Active"
            if  conn_scheme == '1':
                conn_scheme = "ssh"
            elif conn_scheme == '2':
                conn_scheme = "telnet"
            else:
                conn_scheme = 'ssh'
            stack = bool(data['stack_enable'])

            if stack == False:
                try:
                    self.nb.dcim.devices.create(#add main form of device
                        name=data['device_name'],
                        status=mgmt.lower(),
                        site=data['site'],
                        role=data['device_role'],
                        manufacturer=data['manufacturer'].title(),
                        platform=data['platform'],
                        device_type=data['device_type'],
                        primary_ip=data['primary_ip'],
                        tenant=data['tenants'],
                        custom_fields={'Connection_Scheme': conn_scheme,'TG_Group':data['tg_resource_group']},
                    )
                except Exception as err:
                    print(f'device {data["device_name"]} is already done or \n {err}')
                    return [False, err]
                time.sleep(1)
                id_device = self.nb.dcim.devices.get(name=data["device_name"])
                try:
                    self.nb.dcim.interfaces.create(#add interface and belong it to device which created before
                        device=id_device.id,
                        name=data["interface_name"],
                        type=self.type_of_interface,
                        enabled=True,
                    )
                except Exception as err:
                    print(f'interface {data["interfaces_name"]} is already done \n\n {err} \n\n\ ')
                    return [False, err]
                time.sleep(1)
                interface = self.nb.dcim.interfaces.get(name=data["interface_name"], device_id=id_device.id)
                interface_id = interface['id']
                try:
                    self.nb.ipam.ip_addresses.create(#add ip_address and belong it to interface which created before
                        address=data['primary_ip'],
                        status=self.status,
                        assigned_object_type=self.aobjt,
                        assigned_object_id=interface_id,
                    )
                except Exception as err:
                    print(f'Error for create an ip_address {err}')
                    return [False, err]
                time.sleep(1)#next will try to update some fields for device
                try:
                    id_device.update({'primary_ip4': {'address': data['primary_ip']}})
                except Exception as err:
                    print(f"in update device  - - - {err}")
                    return [False, err]
                try:
                    sn = data['list_serial_device'][0]['sn_number']
                    id_device.update({'serial': sn})
                except Exception as err:
                    print(f'Error for create an ip_address {err}')
                if data['location'] != None:
                    id_device.update({'location': data['location']})
                else:
                    pass
                if data['rack'] != None:
                    id_device.update({'rack': data['rack']})
                else:
                    pass
                if data['map_resource_group'] != None:
                    id_device.update({'custom_fields':{'MAP_Group':data['map_resource_group']}})
                else:
                    pass
                if data['name_of_establishment'] != None:
                    id_device.update({'custom_fields': {'Name_of_Establishment': data['name_of_establishment']}})
                else:
                    pass

                try:
                    device_role_name = str(self.nb.dcim.device_roles.get(id=data['device_role']))
                    device_platform_name = str(self.nb.dcim.platforms.get(id=data['platform']))
                    if device_platform_name == "B4TECH" and device_role_name == "leaf" or \
                        device_platform_name == "B4TECH" and device_role_name == "stleaf":
                        try:
                            secondary_ip = data['secondary_ip']
                            self.nb.dcim.interfaces.create(
                                # add interface and belong it to device which created before
                                device=id_device.id,
                                name=self.name_of_interface_secondary,
                                type=self.type_of_interface,
                                enabled=True,
                                label=self.secondary_iface_label
                            )
                            interface = self.nb.dcim.interfaces.get(name=self.name_of_interface_secondary,
                                                                    device_id=id_device.id)
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
                except Exception as err:
                    device_role_name = None
                else:
                    print(f'Succesfull create and update device - [ "{data["device_name"]}" ] and send to telegram chat')
                    message = (f'Netbox.handler[ "Event_Add Device" ]\n Device Name - [ "{data["device_name"]}" ] '
                               f'\n ip_address - [ "{data["primary_ip"]}" ] \n Time: [ "{datetime.datetime.now()}" ]')
                    sender = tg_bot(message)#send message to TG about succesfull event
                    sender.tg_sender()
                return [True, data["device_name"]]
            elif stack == True:
                    call = ADD_NB_VC()
                    result_stack = call.add_vc(**kwargs)
                    if result_stack[0] == True:
                        print(f'Succesfull create and update device - [ "{result_stack[1]}" ] and send to telegram chat')
                        return [True, result_stack[1]]
                    elif result_stack[0] == False:
                        print(result_stack[1])
                        return [False, result_stack[1]]


if __name__ == '__main__':
    print("__main__")




