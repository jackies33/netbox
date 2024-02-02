





from ..add_device import ADD_NB
from ..classifier import classifier_device_type
from netmiko import ConnectHandler , NetMikoAuthenticationException, NetMikoTimeoutException
import re
from ..preparing import CONNECT_PREPARE





class HUAWEI_CONN():

            """
            Class for connection to different device
            """

            def __init__(self, ip_conn=None, mask=None, platform=None, site_name=None,
                         location=None, device_role=None, tenants=None, conn_scheme=None,
                         racks=None, stack_enable=None):
                self.ip_conn = ip_conn
                self.mask = mask
                self.platform = platform
                self.site_name = site_name
                self.location = location
                self.device_role = device_role
                self.tenants = tenants
                self.conn_scheme = conn_scheme
                self.racks = racks
                self.management = 1
                self.stack_enable = stack_enable


            def conn_Huawei(self ,*args):
                print("<<< Start huawei.py >>>")
                type_device_for_conn = 'huawei'
                template = CONNECT_PREPARE(self.ip_conn ,type_device_for_conn ,self.conn_scheme)
                host1 = template.template_conn()
                print("<<< Start huawei.py >>>")
                try:

                    with ConnectHandler(**host1) as net_connect:
                        primary_ip = (f'{self.ip_conn}/{self.mask}')
                        output_name_result = net_connect.send_command('display current-configuration | include sysname',
                                                                      delay_factor=.5)  # command result
                        device_name = re.findall(r"sysname \S+", output_name_result)[0].split('sysname ')[1]
                        output_version = net_connect.send_command('display version',
                                                                  delay_factor=.5)
                        command_ip = (f'display ip interface brief  | include {self.ip_conn}')
                        output_ip = net_connect.send_command(command_ip, delay_factor=.5)
                        escaped_ip_address = re.escape(self.ip_conn)
                        re_ip = (f"(\S+)\s+{escaped_ip_address}")
                        interface_name = re.findall(re_ip, output_ip)[0]
                        manufacturer = 'Huawei Technologies Co.'
                        #device_type = classifier_device_type(manufacturer ,re.findall(r'NE20E-S2F|AR6120|NetEngine 8000 F1A-8H20Q'
                        #                                                            r'|S5700-28C-EI-24S|S5735-S48S4X|CE8851-32CQ8DQ-P|CE6881-48S6CQ', output_version)[0])
                        show_device = net_connect.send_command('display device',delay_factor=.5)
                        device_type = classifier_device_type(
                            manufacturer,re.findall(f".+\s+Device status:",
                                                    show_device, re.MULTILINE)[0].split("Device status:")[0].split("'s")[0].strip())
                        print("<<< Start huawei.py >>>")
                        list_serial_devices = []
                        if self.stack_enable == True:
                            output_stack = net_connect.send_command('display stack', delay_factor=.5)
                            slave_output = re.findall(r"\d\s+Slave", output_stack)
                            standby_output = re.findall(r"\d\s+Standby", output_stack)
                            master_output = re.findall(r"\d\s+Master", output_stack)
                            for slave in slave_output:
                                member_id = slave.replace(" ", "").split('Slave')[0]
                                list_serial_devices.append(
                                    {'member_id': member_id, 'sn_number': '', 'master': False})
                            for standby in standby_output:
                                member_id = standby.replace(" ", "").split('Standby')[0]
                                list_serial_devices.append(
                                    {'member_id': member_id, 'sn_number': '', 'master': False})
                            for master in master_output:
                                member_id = master.replace(" ", "").split('Master')[0]
                                list_serial_devices.append(
                                    {'member_id': member_id, 'sn_number': '', 'master': True})
                            output_manufacturer = net_connect.send_command('display device manufacture-info', delay_factor=.5)
                            member_output = re.findall(f'^\d\s+-\s+\S+', output_manufacturer, re.MULTILINE)
                            for member in member_output:
                                member_id = re.findall(r'\d\s+-\s+', member)[0].replace(" ", "")[0]
                                member_sn = re.findall(r'-\s+\S+', member)[0].replace(" ", "").split("-")[1]
                                for l in list_serial_devices:
                                    if l['member_id'] == member_id:
                                        l['sn_number'] = member_sn

                        elif self.stack_enable == False:
                            output_sn_main = net_connect.send_command('display elabel', delay_factor=.5)
                            member_sn = re.findall(f"BarCode=\S+", output_sn_main, re.MULTILINE)[0].split("BarCode=")[1].strip()
                            list_serial_devices.append({'member_id': 0, 'sn_number': member_sn, 'master': False})

                        net_connect.disconnect()
                        adding = ADD_NB(device_name, self.site_name, self.location, self.tenants,
                                        self.device_role,
                                        manufacturer, self.platform, device_type[0], primary_ip, interface_name,
                                        self.conn_scheme, self.management, self.racks, list_serial_devices,
                                        self.stack_enable)
                        result = adding.add_device()
                        return result


                except (NetMikoAuthenticationException, NetMikoTimeoutException) as err:  # exceptions
                    print('\n\n not connect to ' + self.ip_conn + '\n\n')
                    print("<<< Start huawei.py >>>")
                    type_device_for_conn = 'huawei_telnet'
                    template = CONNECT_PREPARE(self.ip_conn, type_device_for_conn, self.conn_scheme)
                    host1 = template.template_conn()
                    print("<<< Start huawei.py >>>")

                    try:

                        with ConnectHandler(**host1) as net_connect:
                            primary_ip = (f'{self.ip_conn}/{self.mask}')
                            output_name_result = net_connect.send_command(
                                'display current-configuration | include sysname',
                                delay_factor=.5)  # command result
                            device_name = re.findall(r"sysname \S+", output_name_result)[0].split('sysname ')[1]
                            output_version = net_connect.send_command('display version',
                                                                      delay_factor=.5)
                            command_ip = (f'display ip interface brief  | include {self.ip_conn}')
                            output_ip = net_connect.send_command(command_ip, delay_factor=.5)
                            escaped_ip_address = re.escape(self.ip_conn)
                            re_ip = (f"(\S+)\s+{escaped_ip_address}")
                            interface_name = re.findall(re_ip, output_ip)[0]
                            manufacturer = 'Huawei Technologies Co.'
                            device_type = classifier_device_type(
                                manufacturer, re.findall(f".+\s+Device status:",
                                                         show_device, re.MULTILINE)[0].split("Device status:")
                                [0].split("'s")[0].strip())
                            print("<<< Start huawei.py >>>")
                            list_serial_devices = []
                            if self.stack_enable == True:
                                output_stack = net_connect.send_command('display stack', delay_factor=.5)
                                slave_output = re.findall(r"\d\s+Slave", output_stack)
                                standby_output = re.findall(r"\d\s+Standby", output_stack)
                                master_output = re.findall(r"\d\s+Master", output_stack)
                                for slave in slave_output:
                                    member_id = slave.replace(" ", "").split('Slave')[0]
                                    list_serial_devices.append(
                                        {'member_id': member_id, 'sn_number': '', 'master': False})
                                for standby in standby_output:
                                    member_id = standby.replace(" ", "").split('Standby')[0]
                                    list_serial_devices.append(
                                        {'member_id': member_id, 'sn_number': '', 'master': False})
                                for master in master_output:
                                    member_id = master.replace(" ", "").split('Master')[0]
                                    list_serial_devices.append(
                                        {'member_id': member_id, 'sn_number': '', 'master': True})
                                output_manufacturer = net_connect.send_command('display device manufacture-info',
                                                                               delay_factor=.5)
                                member_output = re.findall(f'^\d\s+-\s+\S+', output_manufacturer, re.MULTILINE)
                                for member in member_output:
                                    member_id = re.findall(r'\d\s+-\s+', member)[0].replace(" ", "")[0]
                                    member_sn = re.findall(r'-\s+\S+', member)[0].replace(" ", "").split("-")[1]
                                    for l in list_serial_devices:
                                        if l['member_id'] == member_id:
                                            l['sn_number'] = member_sn

                            elif self.stack_enable == False:
                                output_sn_main = net_connect.send_command('display elabel', delay_factor=.5)
                                member_sn = \
                                re.findall(f"BarCode=\S+", output_sn_main, re.MULTILINE)[0].split("BarCode=")[1].strip()
                                list_serial_devices.append({'member_id': 0, 'sn_number': member_sn, 'master': False})

                            net_connect.disconnect()
                            adding = ADD_NB(device_name, self.site_name, self.location, self.tenants,
                                            self.device_role,
                                            manufacturer, self.platform, device_type[0], primary_ip, interface_name,
                                            self.conn_scheme, self.management, self.racks, list_serial_devices,
                                            self.stack_enable)
                            result = adding.add_device()

                            return result
                    except (NetMikoAuthenticationException, NetMikoTimeoutException) as err:  # exceptions
                        print('\n\n not connect to ' + self.ip_conn + '\n\n')
                        return [False, err]
                except Exception as err:
                    print(f"Error {err}")
                    return [False, err]


