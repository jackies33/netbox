

from netmiko import ConnectHandler
import re


from ..classifier import classifier_device_type
from ..preparing import CONNECT_PREPARE



class QTECH_CONN():

            """
            Class for connection to different device
            """

            def __init__(self, **kwargs):
                """
                Initialize the values
                """

            def conn_qtech(self, **kwargs):
                print("<<< Start qtech.py >>>")
                try:
                    if kwargs['purpose_value'] == "add":
                        data = kwargs['data']['add']####add data for consider adding dict
                        data_for_add = kwargs['data']['add']
                    elif kwargs['purpose_value'] == "edit":
                        data = kwargs['data']['edit']#### edit data for consider data from extract_nb.py
                        data_for_add = kwargs['data']['add']
                    else:
                        return [False, "Undefined_device", None]
                    ip_conn = data['ip_conn']
                    mask = data['mask']
                    stack_enable = data['stack_enable']
                    conn_scheme = data['conn_scheme']
                    type_device_for_conn = "cisco_ios"
                    dict_for_template = {'ip_conn': ip_conn, 'type_device_for_conn': type_device_for_conn,
                                         'conn_scheme': conn_scheme}
                    template = CONNECT_PREPARE()
                    host1 = template.template_conn(**dict_for_template)
                    try:
                        with ConnectHandler(**host1) as net_connect:
                            primary_ip = (f'{ip_conn}/{mask}')
                            # Get device name
                            output_main = net_connect.send_command('show running-config | include hostname', delay_factor=.5)
                            # Extract name from output
                            # device_name = output_main.split()[-1]
                            # device_name = re.findall(r"hostname \S+", output_main)[0].split('hostname ')[1]
                            device_name = re.findall(r"hostname \S+", output_main)[0].split("hostname")[1].split()[0]
                            manufacturer = 'Qtech'
                            # Get device type
                            output_device_type = net_connect.send_command('show version | include Slot', delay_factor=.5)
                            # device_type = classifier_device_type(manufacturer, output_device_type.split()[-1].strip())
                            device_type = re.findall(r" Slot 0 : \S+", output_device_type)[0].split(" Slot 0 :")[1].split()[0]
                            device_type = classifier_device_type(manufacturer,device_type)
                            # Get IF name
                            output_interface_name = net_connect.send_command(
                                f'show ip interface brief | include {ip_conn}', delay_factor=.5)

                            interface_name = \
                            re.findall(f"^\S+\s+\d+\s+{ip_conn}", output_interface_name, re.MULTILINE)[0].split(
                                ip_conn)[0].strip()
                            list_serial_device = []
                            # IF STACK
                            if stack_enable == True:
                                output_switch = net_connect.send_command('show switch', delay_factor=.5)
                                member_output = re.findall(r"\d\s+Member \S+", output_switch)
                                master_output = re.findall(r"\d\s+Master \S+", output_switch)[0]
                                for member in member_output:
                                    member_id = member.replace(" ", "").split('Member')[0]
                                    list_serial_device.append(
                                        {'member_id': member_id, 'sn_number': '',
                                         'master': False})

                                master_id = master_output.replace(" ", "").split('Master')[0]
                                list_serial_device.append(
                                    {'member_id': master_id, 'sn_number': '',
                                     'master': True})

                                output_inventory = net_connect.send_command('show inventory', delay_factor=.5)
                                member_output = re.findall(f'^NAME:.+\nPID: {device_type[1]}.+SN: \S+',
                                                           output_inventory,
                                                           re.MULTILINE)
                                for member in member_output:
                                    member_id = re.findall(r'NAME: "\d"', member)[0].split('NAME: "')[1].split('"')[
                                        0]
                                    member_sn = re.findall(r'SN: \S+', member)[0].split('SN: ')[1]
                                    for l in list_serial_device:
                                        if l['member_id'] == member_id:
                                            l['sn_number'] = member_sn

                            # IF NOT STACK
                            elif stack_enable == False:
                                output_sn = net_connect.send_command('show version | include serial', delay_factor=.5)

                                serial_number = \
                                re.findall(r"System serial number    : \S+", output_sn)[0].split("System serial number    :")[1].split()[0]

                                print("SN is ", serial_number)

                                list_serial_device.append(
                                    {'member_id': 0, 'sn_number': serial_number, 'master': False})
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
                                    'map_resource_group': data['map_resource_group'],
                                    'name_of_establishment': data['name_of_establishment']
                                }
                            )

                            return [True,kwargs]


                    except Exception as err:
                        print(f"Error {err}")
                        return [False,ip_conn, err]
                except Exception as err:
                        try:
                            if kwargs['purpose_value'] == "add":
                                data = kwargs['data']['add']  ####add data for consider adding dict
                                data_for_add = kwargs['data']['add']
                            elif kwargs['purpose_value'] == "edit":
                                data = kwargs['data']['edit']  #### edit data for consider data from extract_nb.py
                                data_for_add = kwargs['data']['add']
                            else:
                                return [False, "Undefined device", None]
                            ip_conn = data['ip_conn']
                        except Exception as err:
                            return [False, "Undefined ip address", err]
                        return [False, ip_conn, err]