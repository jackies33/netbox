



from netmiko import ConnectHandler , NetMikoAuthenticationException, NetMikoTimeoutException
import re
import logging

from ..classifier import classifier_device_type
from ..preparing import CONNECT_PREPARE






message_logger = logging.getLogger('recieved_messages')
message_logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('/opt/netbox/netbox/plugins/file.log')
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)
message_logger.addHandler(file_handler)


class B4COM():

            """
            Class for connection to different device
            """

            def __init__(self, **kwargs):
                """
                Initialize the values
                """

                self.pattern_productname1 = r"^Product Name\s+:\s+(\S+)"
                self.pattern_serialnumber1 =r"^Serial Number\s+:\s+(\S+)"
                self.pattern_ip_secondary = rf"^\s+ip address\s+(\S+)\s+secondary"
                self.pattern_device_type_shit = rf"^B4TECH Software,\s+(\S+),\s+Version"
                self.pattern_host_name_shit = rf"^(\S+)\s+uptime\s+is\s+"
                self.pattern_sn_shit = rf"^System\s+serial\s+number\s+is\s+(\S+)"

            def conn_B4COM_sw_shit(self,**kwargs):
                try:
                    # try to find out new version of devices , another device_type
                    if kwargs['purpose_value'] == "add":
                        data = kwargs['data']['add']  ####add data for consider adding dict
                        data_for_add = kwargs['data']['add']
                    elif kwargs['purpose_value'] == "edit":
                        data = kwargs['data']['edit']  #### edit data for consider data from extract_nb.py
                        data_for_add = kwargs['data']['add']
                    else:
                        return [False, "Undefined_device", None]
                    ip_conn = data['ip_conn']
                    mask = data['mask']
                    stack_enable = data['stack_enable']
                    conn_scheme = data['conn_scheme']
                    type_device_for_conn = "b4com"
                    dict_for_template = {'ip_conn': ip_conn, 'type_device_for_conn': type_device_for_conn,
                                        'conn_scheme': conn_scheme}
                    if conn_scheme == '2':
                        dict_for_template = {'ip_conn': ip_conn, 'type_device_for_conn': "cisco_ios_telnet",
                                             'conn_scheme': conn_scheme}

                    template = CONNECT_PREPARE()
                    host1 = template.template_conn(**dict_for_template)
                    print(host1)
                    # message_logger.info(f"Debug log#1 in b4com.py: {host1}")
                    try:
                        with ConnectHandler(**host1) as net_connect:
                            primary_ip = (f'{ip_conn}/{mask}')
                            output_sys_information = net_connect.send_command('show version', delay_factor=.5)
                            device_type_1 = re.findall(self.pattern_device_type_shit, output_sys_information, re.MULTILINE)
                            if device_type_1:
                                device_type_1 = device_type_1[0]
                            else:
                                return [False, ip_conn, "device_type wasnt found in device"]
                            manufacturer = 'B4COM'
                            device_type = classifier_device_type(manufacturer, device_type_1)
                            print("<<< Start b4com.py >>>")
                            device_name = re.findall(self.pattern_host_name_shit, output_sys_information, re.MULTILINE)
                            if device_name:
                                device_name = device_name[0]
                            else:
                                return [False, ip_conn, "hostname wasnt found in device"]
                            sn = re.findall(self.pattern_sn_shit, output_sys_information, re.MULTILINE)
                            if sn:
                                sn = sn[0]
                            else:
                                return [False, ip_conn, "sn wasnt found in device"]
                            pattern_iface_name1 = rf"^(.*?)\s+{re.escape(ip_conn)}\s+.*$"
                            output_interface_name = net_connect.send_command(f'show ip interface brief', delay_factor=.5)
                            interface_name = re.findall(pattern_iface_name1, output_interface_name,
                                                        re.MULTILINE)
                            if interface_name:
                                interface_name = interface_name[0]
                            else:
                                interface_name = 'eth0'
                            list_serial_device = []
                            if stack_enable == True:
                                return [False, ip_conn, "For this type of device doesn't have yet stack handler"]
                            elif stack_enable == False:
                                sn = re.findall(self.pattern_sn_shit, output_sys_information, re.MULTILINE)
                                if sn:
                                    sn = sn[0]
                                else:
                                    return [False, ip_conn, "sn wasnt found in device"]
                                list_serial_device.append(
                                    {'member_id': 0, 'sn_number': sn, 'master': False})
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
                                    'unit_of_rack': data['unit_of_rack'],
                                    'stack_enable': data['stack_enable'],
                                    'tg_resource_group': data['tg_resource_group'],
                                    'map_resource_group': data['map_resource_group'],
                                    'name_of_establishment': data['name_of_establishment'],
                                    'secondary_ip': None
                                }
                            )
                            message_logger.info(f"Debug log#show full data after connect in b4com.py: {kwargs}")
                            return [True, kwargs]
                    except Exception as err:
                        message_logger.info(f"Debug log#2 in b4com.py: {err}")
                        return [False, ip_conn, err]

                except Exception as err:
                    message_logger.info(f"Debug log#2 in b4com.py: {err}")
                    return [False, ip_conn, err]

            def conn_B4COM_sw(self, **kwargs):

                print("<<< Start b4com.py >>>")
                try:
                    if kwargs['purpose_value'] == "add":
                        data = kwargs['data']['add']####add data for consider adding dict
                        data_for_add = kwargs['data']['add']
                    elif kwargs['purpose_value'] == "edit":
                        data = kwargs['data']['edit']#### edit data for consider data from extract_nb.py
                        data_for_add = kwargs['data']['add']
                    else:
                        return [False,"Undefined_device", None]
                    ip_conn = data['ip_conn']
                    mask = data['mask']
                    stack_enable = data['stack_enable']
                    conn_scheme = data['conn_scheme']
                    type_device_for_conn = "b4com"
                    dict_for_template = {'ip_conn': ip_conn, 'type_device_for_conn': type_device_for_conn,
                                         'conn_scheme': conn_scheme}
                    if conn_scheme == '2':
                        dict_for_template = {'ip_conn': ip_conn, 'type_device_for_conn': "cisco_ios_telnet",'conn_scheme': conn_scheme}

                    template = CONNECT_PREPARE()
                    host1 = template.template_conn(**dict_for_template)
                    print(host1)
                    #message_logger.info(f"Debug log#1 in b4com.py: {host1}")
                    try:
                        with ConnectHandler(**host1) as net_connect:
                            primary_ip = (f'{ip_conn}/{mask}')
                            output_sys_information = net_connect.send_command('show system-information all', delay_factor=.5)
                            device_type_1 = re.findall(self.pattern_productname1, output_sys_information,re.MULTILINE)
                            if device_type_1:
                                device_type_1 = device_type_1[0]
                            else:
                                #try another type of device
                                net_connect.disconnect()
                                result = self.conn_B4COM_sw_shit(**kwargs)
                                return result

                                #return [False, ip_conn, "device_type wasn't found in device"]
                            manufacturer = 'B4COM'
                            device_type = classifier_device_type(manufacturer,device_type_1)
                            print("<<< Start b4com.py >>>")
                            device_name = net_connect.send_command('show hostname',delay_factor=.5)
                            pattern_iface_name1 = rf"^(.*?)\s+{re.escape(ip_conn)}\s+.*$"
                            output_interface_name = net_connect.send_command(f'show ip interface brief', delay_factor=.5)
                            interface_name = re.findall(pattern_iface_name1, output_interface_name, re.MULTILINE)
                            if interface_name:
                                interface_name = interface_name[0]
                            else:
                                interface_name = 'eth0'
                            list_serial_device = []
                            if stack_enable == True:
                                return [False, ip_conn, "For this type of device doesn't have yet stack handler"]
                            elif stack_enable == False:
                                serial_number = re.findall(self.pattern_serialnumber1, output_sys_information,re.MULTILINE)
                                if serial_number:
                                    serial_number = serial_number[0]
                                list_serial_device.append(
                                    {'member_id': 0, 'sn_number': serial_number, 'master': False})
                            secondary_ip_output = net_connect.send_command('show running-config interface lo', delay_factor=.5)
                            sec_ip = None
                            sec_ip = re.findall(self.pattern_ip_secondary, secondary_ip_output, re.MULTILINE)
                            if sec_ip:
                                sec_ip = sec_ip[0]
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
                                    'unit_of_rack': data['unit_of_rack'],
                                    'stack_enable': data['stack_enable'],
                                    'tg_resource_group': data['tg_resource_group'],
                                    'map_resource_group': data['map_resource_group'],
                                    'name_of_establishment': data['name_of_establishment'],
                                    'secondary_ip':sec_ip
                                }
                            )
                            message_logger.info(f"Debug log#show full data after connect in b4com.py: {kwargs}")

                            return [True, kwargs]
                    except Exception as err:
                        message_logger.info(f"Debug log#2 in b4com.py: {err}")
                        return [False, ip_conn, err]
                except Exception as err:
                        message_logger.info(f"Debug log#2 in b4com.py: {err}")
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
                            message_logger.info(f"Debug log#2 in b4com.py: {err}")
                            return [False, "Undefined ip address", err]
                        return [False, ip_conn, err]


