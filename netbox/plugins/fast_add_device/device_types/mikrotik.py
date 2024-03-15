

from ..add_device import ADD_NB
from ..classifier import classifier_device_type
from netmiko import ConnectHandler , NetMikoAuthenticationException, NetMikoTimeoutException
import re
from ..preparing import CONNECT_PREPARE


class MIKROTIK_CONN():

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


            def conn_RouterOS(self ,*args):
                print("<<< Start mikrotik.py >>>")
                type_device_for_conn = 'mikrotik_routeros'
                template = CONNECT_PREPARE(self.ip_conn ,type_device_for_conn ,self.conn_scheme)
                host1 = template.template_conn()
                print("<<< Start mikrotik.py >>>")
                try:

                    with ConnectHandler(**host1) as net_connect:
                        primary_ip = (f'{self.ip_conn}/{self.mask}')
                        device_type_output = net_connect.send_command('system resource print',delay_factor=.5)  # command result
                        device_name_output = net_connect.send_command('system export', delay_factor=.5)
                        ip_address_output = net_connect.send_command('ip address print', delay_factor=.5)
                        serial_output = net_connect.send_command('system routerboard print', delay_factor=.5)
                        device_type = re.findall(r'board-name:\s+\S+', device_type_output)[0].split("board-name:")[1].split()[0]
                        device_name = re.findall(r'set name=\S+', device_name_output)[0].split('set name=')[1]
                        interface_name = re.findall(rf"\d+\s+{self.ip_conn}/\d+\s+\S+\s+\S+", ip_address_output)[0].split()[-1]
                        serial_number = re.findall(r'serial-number:\s+\S+', serial_output)[0].split()[-1]
                        manufacturer = 'MikroTik'
                        device_type = classifier_device_type(manufacturer,device_type)
                        print("<<< Start mikrotik.py >>>")
                        list_serial_devices = []
                        list_serial_devices.append({'member_id': 0, 'sn_number': serial_number, 'master': False})
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


                except Exception as err:
                    print(f"Error {err}")
                    return [False, err]



