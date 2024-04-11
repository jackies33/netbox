

from netmiko import ConnectHandler , NetMikoAuthenticationException, NetMikoTimeoutException
import re

from ..classifier import classifier_device_type
from ..preparing import CONNECT_PREPARE


class MIKROTIK_CONN():

            """
            Class for connection to different device
            """

            def __init__(self, **kwargs):
                """
                Initialize the values
                """


            def conn_RouterOS(self ,**kwargs):
                print("<<< Start mikrotik.py >>>")
                if kwargs['purpose_value'] == "add":
                    data = kwargs['data']['add']####add data for consider adding dict
                    data_for_add = kwargs['data']['add']
                elif kwargs['purpose_value'] == "edit":
                    data = kwargs['data']['edit']#### edit data for consider data from extract_nb.py
                    data_for_add = kwargs['data']['add']
                else:
                    return [False,None]
                ip_conn = data['ip_conn']
                mask = data['mask']
                stack_enable = data['stack_enable']
                conn_scheme = data['conn_scheme']
                type_device_for_conn = 'mikrotik_routeros'
                dict_for_template = {'ip_conn': ip_conn, 'type_device_for_conn': type_device_for_conn,
                                     'conn_scheme': conn_scheme}
                template = CONNECT_PREPARE()
                host1 = template.template_conn(**dict_for_template)
                print("<<< Start mikrotik.py >>>")
                try:

                    with ConnectHandler(**host1) as net_connect:
                        primary_ip = (f'{ip_conn}/{mask}')
                        device_type_output = net_connect.send_command('system resource print',delay_factor=.5)  # command result
                        device_name_output = net_connect.send_command('system export', delay_factor=.5)
                        ip_address_output = net_connect.send_command('ip address print', delay_factor=.5)
                        serial_output = net_connect.send_command('system routerboard print', delay_factor=.5)
                        device_type = re.findall(r'board-name:\s+\S+', device_type_output)[0].split("board-name:")[1].split()[0]
                        device_name = re.findall(r'set name=\S+', device_name_output)[0].split('set name=')[1]
                        interface_name = re.findall(rf"\d+\s+{ip_conn}/\d+\s+\S+\s+\S+", ip_address_output)[0].split()[-1]
                        serial_number = re.findall(r'serial-number:\s+\S+', serial_output)[0].split()[-1]
                        manufacturer = 'MikroTik'
                        device_type = classifier_device_type(manufacturer,device_type)
                        print("<<< Start mikrotik.py >>>")
                        list_serial_device = []
                        list_serial_device.append({'member_id': 0, 'sn_number': serial_number, 'master': False})
                        net_connect.disconnect()
                        data_for_add.update(
                            {
                                'site': data['site'],
                                'location': data['location'],
                                'tenants': data['tenants'],
                                'device_role': data['device_role'],
                                'platform': data['platform'],
                                'primary_ip': data['primary_ip'],
                                'device_name': device_name,
                                'manufacturer': manufacturer,
                                'device_type': device_type[0],
                                'interface_name': interface_name,
                                'list_serial_device': list_serial_device,
                                'conn_scheme': data['conn_scheme'],
                                'management_status': data['management_status'],
                                'rack': data['rack'],
                                'stack_enable': data['stack_enable'],
                                'tg_resource_group': data['tg_resource_group'],
                                'map_resource_group': data['map_resource_group']
                            }
                        )

                        return kwargs


                except (NetMikoAuthenticationException, NetMikoTimeoutException) as err:  # exceptions
                    print('\n\n not connect to ' + ip_conn + '\n\n')


                except Exception as err:
                    print(f"Error {err}")
                    return [False, err]



