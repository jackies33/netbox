from ..add_device import ADD_NB
from ..classifier import classifier_device_type
from netmiko import ConnectHandler , NetMikoAuthenticationException, NetMikoTimeoutException
import re
from ..preparing import CONNECT_PREPARE
import paramiko
from paramiko import SSHException


class QTECH_CONN():

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

            def conn_qtech(self, *args):
                print("<<< Start qtech.py >>>")
                type_device_for_conn = "cisco_ios"
                template = CONNECT_PREPARE(self.ip_conn, type_device_for_conn, self.conn_scheme)
                host1 = template.template_conn()
                try:
                    with ConnectHandler(**host1) as net_connect:
                        primary_ip = (f'{self.ip_conn}/{self.mask}')

                        # Get device name
                        output_main = net_connect.send_command('show running-config | include hostname', delay_factor=.5)

                        # Extract name from output
                        device_name = output_main.split()[-1]

                        print("Device name is {device_name}")
                        
                        manufacturer = 'Qtech'
                        
                        # Get device type
                        output_device_type = net_connect.send_command('show version | include Slot', delay_factor=.5)
                        device_type = classifier_device_type(manufacturer, output_device_type.split()[-1].strip())
                        print("Device name is {device_type}")

                                                
                        # Get IF name
                        output_interface_name = net_connect.send_command(
                            f'show ip interface brief | include {self.ip_conn}', delay_factor=.5)
                        
                        interface_name = \
                        re.findall(f"^\S+\s+{self.ip_conn}", output_interface_name, re.MULTILINE)[0].split(
                            self.ip_conn)[0].strip()
                        
                        print("Interface name is {interface_name}")

                        list_serial_devices = []

                        # IF STACK
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

                        
                        # IF NOT STACK
                        elif self.stack_enable == False:
                            serial_number = \
                            re.findall(f'Serial number', output_main)[0].split(' Serial number       : ')[1]

                            print("SN is {serial_number}")


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

                
                except Exception as err:
                    print(f"Error {err}")
                    return [False, err]