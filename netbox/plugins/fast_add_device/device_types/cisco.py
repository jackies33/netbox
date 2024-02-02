




from ..add_device import ADD_NB
from ..classifier import classifier_device_type
from netmiko import ConnectHandler , NetMikoAuthenticationException, NetMikoTimeoutException
import re
from ..preparing import CONNECT_PREPARE



class CISCO_CONN():

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

            def conn_Cisco_IOS(self, *args):
                print("<<< Start cisco.py >>>")
                type_device_for_conn = "cisco_ios"
                template = CONNECT_PREPARE(self.ip_conn, type_device_for_conn, self.conn_scheme)
                host1 = template.template_conn()
                try:
                    with ConnectHandler(**host1) as net_connect:
                        primary_ip = (f'{self.ip_conn}/{self.mask}')
                        output_main = net_connect.send_command('show version', delay_factor=.5)
                        device_name = re.findall(f"\S+ uptime is", output_main)[0].split("uptime is")[0].strip()
                        manufacturer = 'Cisco Systems'
                        device_type = classifier_device_type(manufacturer,
                                                             re.findall(f"^cisco \S+", output_main, re.MULTILINE)[
                                                                 0].split("cisco")[1].strip())
                        print("<<< Start cisco.py >>>")
                        output_interface_name = net_connect.send_command(
                            f'show ip interface brief | include {self.ip_conn}', delay_factor=.5)
                        interface_name = \
                        re.findall(f"^\S+\s+{self.ip_conn}", output_interface_name, re.MULTILINE)[0].split(
                            self.ip_conn)[0].strip()
                        list_serial_devices = []
                        if self.stack_enable == True:
                            output_switch = net_connect.send_command('show switch', delay_factor=.5)
                            member_output = re.findall(r"\d\s+Member \S+", output_switch)
                            master_output = re.findall(r"\d\s+Master \S+", output_switch)[0]
                            for member in member_output:
                                member_id = member.replace(" ", "").split('Member')[0]
                                list_serial_devices.append(
                                    {'member_id': member_id, 'sn_number': '',
                                     'master': False})

                            master_id = master_output.replace(" ", "").split('Master')[0]
                            list_serial_devices.append(
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
                                for l in list_serial_devices:
                                    if l['member_id'] == member_id:
                                        l['sn_number'] = member_sn

                        elif self.stack_enable == False:
                            serial_number = \
                            re.findall(f'Processor board ID \S+', output_main)[0].split('Processor board ID ')[1]
                            list_serial_devices.append(
                                {'member_id': 0, 'sn_number': serial_number, 'master': False})

                        adding = ADD_NB(device_name, self.site_name, self.location, self.tenants,
                                        self.device_role,
                                        manufacturer, self.platform, device_type[0], primary_ip, interface_name,
                                        self.conn_scheme, self.management, self.racks, list_serial_devices,
                                        self.stack_enable)
                        result = adding.add_device()
                        net_connect.disconnect()
                        return result

                except (NetMikoAuthenticationException, NetMikoTimeoutException) as err:  # exceptions
                    print('\n\n not connect to (with ssh)' + self.ip_conn + '\n\n')
                    print("<<< Start cisco.py >>>")
                    type_device_for_conn = "cisco_ios_telnet"
                    template = CONNECT_PREPARE(self.ip_conn, type_device_for_conn, 'telnet')
                    host1 = template.template_conn()
                    print("<<< Start cisco.py >>>")
                    try:
                        with ConnectHandler(**host1) as net_connect:
                            primary_ip = (f'{self.ip_conn}/{self.mask}')
                            output_main = net_connect.send_command('show version', delay_factor=.5)
                            device_name = re.findall(f"\S+ uptime is", output_main)[0].split("uptime is")[0].strip()
                            manufacturer = 'Cisco Systems'
                            device_type = classifier_device_type(manufacturer,
                                                                 re.findall(f"^cisco \S+", output_main,
                                                                            re.MULTILINE)[
                                                                     0].split("cisco")[1].strip())
                            print("<<< Start cisco.py >>>")
                            output_interface_name = net_connect.send_command(
                                f'show ip interface brief | include {self.ip_conn}', delay_factor=.5)
                            interface_name = \
                                re.findall(f"^\S+\s+{self.ip_conn}", output_interface_name, re.MULTILINE)[0].split(
                                    self.ip_conn)[0].strip()
                            list_serial_devices = []
                            if self.stack_enable == True:
                                output_switch = net_connect.send_command('show switch', delay_factor=.5)
                                member_output = re.findall(r"\d\s+Member \S+", output_switch)
                                master_output = re.findall(r"\d\s+Master \S+", output_switch)[0]
                                for member in member_output:
                                    member_id = member.replace(" ", "").split('Member')[0]
                                    list_serial_devices.append(
                                        {'member_id': member_id, 'sn_number': '',
                                         'master': False})

                                master_id = master_output.replace(" ", "").split('Master')[0]
                                list_serial_devices.append(
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
                                    for l in list_serial_devices:
                                        if l['member_id'] == member_id:
                                            l['sn_number'] = member_sn

                            elif self.stack_enable == False:
                                serial_number = \
                                    re.findall(f'Processor board ID \S+', output_main)[0].split(
                                        'Processor board ID ')[1]
                                list_serial_devices.append(
                                    {'member_id': 0, 'sn_number': serial_number, 'master': False})

                            adding = ADD_NB(device_name, self.site_name, self.location, self.tenants,
                                            self.device_role,
                                            manufacturer, self.platform, device_type[0], primary_ip, interface_name,
                                            self.conn_scheme, self.management, self.racks, list_serial_devices,
                                            self.stack_enable)
                            result = adding.add_device()
                            net_connect.disconnect()
                            return result
                    except (NetMikoAuthenticationException, NetMikoTimeoutException) as err:  # exceptions
                        print('\n\n not connect to ' + self.ip_conn + '\n\n')
                        return [False, err]
                except Exception as err:
                    print(f"Error {err}")
                    return [False, err]

            def conn_Cisco_IOS_XR(self, *args):
                print("<<< Start cisco.py >>>")
                type_device_for_conn = "cisco_xr"
                template = CONNECT_PREPARE(self.ip_conn, type_device_for_conn, self.conn_scheme)
                host1 = template.template_conn()
                print("<<< Start cisco.py >>>")
                try:
                    with ConnectHandler(**host1) as net_connect:
                        list_serial_devices =[]
                        primary_ip = (f'{self.ip_conn}/{self.mask}')
                        output_hostname = net_connect.send_command('show running-config hostname', delay_factor=.5)
                        device_name = \
                        re.findall(r'hostname \S+', output_hostname)[0].replace(" ", "").split("hostname")[1]
                        output_version = net_connect.send_command('show version', delay_factor=.5)
                        manufacturer = 'Cisco Systems'
                        device_type = re.findall(f"cisco \S+", output_version, re.MULTILINE)[0].split("cisco")[
                            1].strip()
                        if device_type == "ASR9K":
                            device_type = classifier_device_type(manufacturer,
                                                                 re.findall(f"\S+\s+Chassis", output_version,
                                                                            re.MULTILINE)[0].replace(" ", "").split(
                                                                     "Chassis")[0])
                        else:
                            device_type = classifier_device_type(manufacturer, device_type)
                        print("<<< Start cisco.py >>>")
                        output_interface_name = net_connect.send_command(
                            f'show ip interface brief | include {self.ip_conn}', delay_factor=.5)
                        interface_name = \
                        re.findall(f"^\S+\s+{self.ip_conn}", output_interface_name, re.MULTILINE)[0].split(self.ip_conn)[
                            0].strip()
                        show_inventory = net_connect.send_command(f'show inventory rack', delay_factor=.5)
                        member_sn1 = re.findall(f'{device_type[1]}\s+\S+|{device_type[1]}\S+\s+\S+', show_inventory)[
                            0].split()
                        member_sn = member_sn1[1]
                        if member_sn1[0] == device_type[1]:
                            pass
                        elif member_sn1[0] != device_type[1]:

                            device_type = device_type = classifier_device_type(manufacturer, member_sn1[0])
                            print("<<< Start cisco.py >>>")
                        list_serial_devices.append({'member_id': 0, 'sn_number': member_sn, 'master': False})
                        adding = ADD_NB(device_name, self.site_name, self.location, self.tenants,
                                        self.device_role,
                                        manufacturer, self.platform, device_type[0], primary_ip, interface_name,
                                        self.conn_scheme, self.management, self.racks, list_serial_devices,
                                        self.stack_enable)
                        result = adding.add_device()
                        net_connect.disconnect()
                        return result
                except (NetMikoAuthenticationException, NetMikoTimeoutException) as err:  # exceptions
                    print('\n\n not connect to ' + self.ip_conn + '\n\n')
                    return [False, err]

            def conn_Cisco_NXOS(self,*args):
                   print("<<< Start cisco.py >>>")
                   type_device_for_conn = "cisco_nxos"
                   template = CONNECT_PREPARE(self.ip_conn, type_device_for_conn, self.conn_scheme)
                   host1 = template.template_conn()
                   print("<<< Start cisco.py >>>")
                   try:
                            with ConnectHandler(**host1) as net_connect:
                                    primary_ip = (f'{self.ip_conn}/{self.mask}')
                                    output1 = net_connect.send_command('show hostname', delay_factor=.5)
                                    device_name = re.findall(r'\S+', output1)[0]
                                    output2 = net_connect.send_command('show version',delay_factor=.5)  # command result
                                    output_name_result = re.findall(r'Hardware\n.+', output2)[0]
                                    manufacturer = 'Cisco Systems'
                                    device_type = classifier_device_type(manufacturer,re.findall(r'cisco Nexus7700 C7702|cisco Nexus 6001', output_name_result)[0].split("cisco")[1].strip())
                                    print("<<< Start cisco.py >>>")
                                    interface_name = 'mgmt0'
                                    list_serial_devices = []
                                    serial_number = re.findall(f'Processor board ID \S+', output2)[0].split('Processor board ID ')[1]
                                    list_serial_devices.append({'member_id': 0, 'sn_number': serial_number, 'master': False})
                                    adding = ADD_NB(device_name, self.site_name, self.location, self.tenants,
                                                    self.device_role,
                                                    manufacturer, self.platform, device_type[0], primary_ip, interface_name,
                                                    self.conn_scheme, self.management, self.racks, list_serial_devices,
                                                    self.stack_enable)
                                    result = adding.add_device()
                                    net_connect.disconnect()
                                    return result

                   except (NetMikoAuthenticationException, NetMikoTimeoutException) as err:  # exceptions
                        print('\n\n not connect to ' + self.ip_conn + '\n\n')
                        return [False, err]
                   except Exception as err:
                       print(f"Error {err}")
                       return [False, err]
