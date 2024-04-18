


from netmiko import ConnectHandler
import re

from ..classifier import classifier_device_type
from ..preparing import CONNECT_PREPARE




class LINUX():
            """
            Class for connection to different device
            """

            def __init__(self, **kwargs):
                """
                Initialize the values
                """

            def conn_OS_Linux(self ,**kwargs):
                print("<<< Start linux.py >>>")
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
                type_device_for_conn = "linux"
                dict_for_template = {'ip_conn': ip_conn, 'type_device_for_conn': type_device_for_conn,
                                     'conn_scheme': conn_scheme}
                template = CONNECT_PREPARE()
                host1 = template.template_conn(**dict_for_template)
                print("<<< Start linux.py >>>")
                try:
                    with ConnectHandler(**host1) as net_connect:
                        primary_ip = (f'{ip_conn}/{mask}')
                        sudo = net_connect.send_command('sudo -s', delay_factor=.5, expect_string="#")
                        output_hostname = net_connect.send_command('cat /etc/hostname', delay_factor=.5, expect_string="#")
                        device_name = re.findall(r'\S+', output_hostname)[0]
                        output_interface = net_connect.send_command('ip a', delay_factor=.5, expect_string="#")
                        interface_name = re.findall(f'^\d+: .+\n.+\n.+inet {ip_conn}', output_interface, re.MULTILINE)[0]
                        interface_name = re.findall(r'\d+: \S+:', interface_name)[0].split(":")[1].strip()
                        output_device_type = net_connect.send_command('cat /etc/issue', delay_factor=.5, expect_string="#")
                        manufacturer = 'Meinberg Funkuhren GmbH & Co. KG'
                        device_type = classifier_device_type(manufacturer, re.findall(r'Meinberg LANTIME OS7|Ubuntu', output_device_type)[0])
                        print("<<< Start linux.py >>>")
                        list_serial_device = []
                        list_serial_device.append({'member_id': 0, 'sn_number': "NNNNNNN000000", 'master': False})
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
                                'map_resource_group': data['map_resource_group'],
                                'name_of_establishment': data['name_of_establishment']
                            }
                        )

                        return kwargs


                except Exception as err:
                    print(f"Error {err}")
                    return [False, err]