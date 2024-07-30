




###external pack
import time
import pynetbox


##internal pack
from ..my_pass import netbox_url,netbox_api_token
from .add_virtual_chassis import ADD_NB_VC


class ADD_NB_CSV():

        """
        class for add data to NetBox over RestApi
        """

        def __init__(self, **kwargs):

            self.aobjt = 'dcim.interface'
            self.status = 'active'
            self.type_of_interface = 'virtual'
            self.nb = pynetbox.api(url=netbox_url,
                                   token=netbox_api_token)
            self.nb.http_session.verify = False
            """
            Initialize the values
            """



        def add_device_csv(self,**kwargs):
            print("<<< Start add_device.py >>>")
            # print('this is add_device.py!!!!')
            data = kwargs['data']['add']
            mgmt = data['management_status']
            conn_scheme = data['conn_scheme']
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
                    self.nb.dcim.devices.create(
                        name=data['device_name'],
                        status=mgmt.lower(),
                        site=data['site'],
                        device_role=data['device_role'],
                        manufacturer=data['manufacturer'].title(),
                        platform=data['platform'],
                        device_type=data['device_type'],
                        primary_ip=data['primary_ip'],
                        tenant=data['tenants'],
                        custom_fields={'Connection_Scheme': conn_scheme,'TG_Group':data['tg_resource_group']},
                    )
                except Exception as err:
                    print(f'device {data["device_name"]} is already done or \n {err}')
                    return [False, data["device_name"]]
                time.sleep(1)
                id_device = self.nb.dcim.devices.filter(name=data["device_name"])
                for d in id_device:
                    id_device = d
                try:
                    self.nb.dcim.interfaces.create(
                        device=id_device.id,
                        name=data["interface_name"],
                        type=self.type_of_interface,
                        enabled=True,
                    )
                except Exception as err:
                    print(f'interface {data["interfaces_name"]} is already done \n\n {err} \n\n\ ')
                    return [False, data["device_name"]]
                time.sleep(1)
                interface = self.nb.dcim.interfaces.filter(name=data["interface_name"], device_id=id_device.id)
                for i in interface:
                    interface = i
                interface_id = interface['id']
                try:
                    self.nb.ipam.ip_addresses.create(
                        address=data['primary_ip'],
                        status=self.status,
                        assigned_object_type=self.aobjt,
                        assigned_object_id=interface_id,
                    )
                except Exception as err:
                    print(f'Error for create an ip_address {err}')
                    return [False, data["device_name"]]
                time.sleep(1)
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
                    id_device.update({'primary_ip4': {'address': data['primary_ip']}})
                except Exception as err:
                    print(f"in update device  - - - {err}")
                    return [False, data["device_name"]]
                else:
                    print(f'Succesfull create and update device - [ "{data["device_name"]}" ] ')
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

        def add_sites_csv(self, **kwargs):
                print("<<< Start add_device.py >>>")
                # print('this is add_device.py!!!!')
                data = kwargs['data']['add']
                try:
                    self.nb.dcim.sites.create(
                        name=data["name"],
                        slug=data["slug"],
                        region=data["region"],
                        physical_address=data["physical_address"]
                    )
                    return [True,data["name"]]
                except Exception as err:
                    try:
                        slug = (f'{data["slug"]}111')
                        self.nb.dcim.sites.create(
                            name=data["name"],
                            slug=slug,
                            region=data["region"],
                            physical_address=data["physical_address"]
                        )
                        return [True, data["name"]]
                    except Exception as err:
                        print(f'{err}')
                        return [False, data["name"]]

        def add_prefixes_csv(self, **kwargs):
                print("<<< Start add_device.py >>>")
                # print('this is add_device.py!!!!')
                data = kwargs['data']['add']
                try:
                    self.nb.ipam.prefixes.create(
                        prefix=data['prefix'],
                        vrf= data['vrf'],
                        tenant= data['tenant'],
                        site= data['site'],
                        vlan= data['vlan'],
                        #role= data['role'],
                    )
                    return [True,data["prefix"],None]
                except Exception as err:
                        return [False, data["prefix"],err]


if __name__ == '__main__':
    print("__main__")




