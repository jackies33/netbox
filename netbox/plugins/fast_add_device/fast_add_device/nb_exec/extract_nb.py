

import pynetbox


from ..my_pass import netbox_url, netbox_api_token



class EXTRACT_NB():

    def __init__(self, **kwargs):
                            """
                            Initialize the values
                            """

    def extract_for_edit(self, **kwargs):
        print("<<< Start extract_nb.py >>>")
        try:
            device_id = kwargs['data']['edit']['device_id']
            trans_dict = {}
            list_serial_device = []
            self.nb = pynetbox.api(url=netbox_url, token=netbox_api_token)
            self.nb.http_session.verify = False
            main_value_device = self.nb.dcim.devices.get(id=device_id)
            ip_address = None
            try:
                ip_address = main_value_device.primary_ip.address
            except Exception as err:
                pass
            if ip_address == None:
                    try:
                        vc_id = main_value_device.virtual_chassis.id
                        vc = self.nb.dcim.virtual_chassis.get(id=vc_id)
                        device_id = vc.master.id
                        main_value_device = self.nb.dcim.devices.get(id=device_id)
                    except Exception as err:
                        pass
            device_name = main_value_device.name
            interface_main = None
            for iface in self.nb.dcim.interfaces.filter(device=device_name,device_id=main_value_device.id):
                if iface.type.value == 'virtual':
                    interface_main = iface
            custom_fields = main_value_device.custom_fields
            status = str(main_value_device.status.label)
            if status == 'Active':
                status = 1
            elif status == 'Offline':
                status = 2
            location = None
            rack = None
            vc = None
            stack_enable = False
            member_role = False
            sn = None
            vc_name = None
            dev_vc = None
            try:
                conn_scheme = custom_fields['Connection_Scheme']
            except Exception as err:
                conn_scheme = None
            try:
                tg_group = custom_fields['TG_Group']['id']
            except Exception as err:
                tg_group = None
            try:
                map_group = custom_fields['MAP_Group']['id']
            except Exception as err:
                map_group = None
            try:
                location = int(main_value_device.location.id)
            except Exception as err:
                pass
            try:
                rack = int(main_value_device.rack.id)
            except Exception as err:
                pass
            try:
                vc = main_value_device.virtual_chassis.id
                vc_name = main_value_device.virtual_chassis.name
                vc = int(vc)
            except Exception as err:
                pass
            try:
                sn = str(main_value_device.serial)
            except Exception as err:
                pass
            if vc != None:
                try:
                    stack_enable = True

                    for dev in self.nb.dcim.devices.all():
                        try:
                            device_vc = dev.virtual_chassis.name
                            master_id = dev.virtual_chassis.master.id

                        except Exception as err:
                            continue
                        if str(device_vc) == str(vc_name):
                            member_id = (dev.name).split('.')[1]
                            member_id = int(member_id)
                            try:
                                sn = str(dev.serial)
                            except Exception as err:
                                pass
                            obj_id = dev.id
                            if int(obj_id) == int(master_id):
                                member_role = True
                            elif int(obj_id) != int(master_id):
                                member_role = False
                            list_serial_device.append(
                                {'member_id': member_id, 'sn_number': sn, 'master': member_role,'device_id':obj_id})
                            device_name = device_name.split('.')[0]
                except Exception as err:
                    pass
            else:
                    list_serial_device.append(
                        {'member_id': 0, 'sn_number': sn, 'master': False})

            trans_dict.update({
                           'purpose_value': 'edit',
                           'data':{'edit':
                           {
                           'device_id': main_value_device.id,
                           'device_name': device_name,
                           'site': main_value_device.site.id,
                           'location':location,
                           'rack': rack,
                           'tenants': main_value_device.tenant.id,
                           'device_role': main_value_device.device_role.id,
                           'device_type': main_value_device.device_type.id,
                           'manufacturer': str(main_value_device.device_type.manufacturer),
                           'platform': main_value_device.platform.id,
                           'primary_ip': main_value_device.primary_ip.address,
                           'interface_name': interface_main.name,
                           'virtual_chassis': vc,
                           'list_serial_device': list_serial_device,
                           'stack_enable': stack_enable,
                           'management_status':status,
                           'conn_scheme': conn_scheme,
                           'tg_resource_group': tg_group,
                           'map_resource_group': map_group
            },
                               'add':{},
                               'diff':{}
            }})
            return [True,trans_dict]
        except Exception as err:
            return [False, err]


