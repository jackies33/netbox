



from ..add_device import ADD_NB
from ..classifier import classifier_device_type
from ..preparing import CONNECT_PREPARE
from netmiko import ConnectHandler
import re



class LINUX():
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




            def conn_OS_Linux(self ,*args):
                print("<<< Start linux.py >>>")
                type_device_for_conn = "linux"
                template = CONNECT_PREPARE(self.ip_conn, type_device_for_conn, self.conn_scheme)
                host1 = template.template_conn()
                print("<<< Start linux.py >>>")
                try:
                    with ConnectHandler(**host1) as net_connect:
                        primary_ip = (f'{self.ip_conn}/{self.mask}')
                        sudo = net_connect.send_command('sudo -s', delay_factor=.5, expect_string="#")
                        output_hostname = net_connect.send_command('cat /etc/hostname', delay_factor=.5, expect_string="#")
                        device_name = re.findall(r'\S+', output_hostname)[0]
                        output_interface = net_connect.send_command('ip a', delay_factor=.5, expect_string="#")
                        interface_name = re.findall(f'^\d+: .+\n.+\n.+inet {self.ip_conn}', output_interface, re.MULTILINE)[0]
                        interface_name = re.findall(r'\d+: \S+:', interface_name)[0].split(":")[1].strip()
                        output_device_type = net_connect.send_command('cat /etc/issue', delay_factor=.5, expect_string="#")
                        manufacturer = 'Meinberg Funkuhren GmbH & Co. KG'
                        device_type = classifier_device_type(manufacturer, re.findall(r'Meinberg LANTIME OS7|Ubuntu', output_device_type)[0])
                        print("<<< Start linux.py >>>")
                        list_serial_devices = []
                        list_serial_devices.append({'member_id': 0, 'sn_number': "NNNNNNN000000", 'master': False})
                        adding = ADD_NB(device_name, self.site_name, self.location, self.tenants, self.device_role,
                                        manufacturer, self.platform, device_type[0], primary_ip, interface_name,
                                        self.conn_scheme, self.management, self.racks, list_serial_devices,
                                        self.stack_enable)
                        result = adding.add_device()
                        return result


                except Exception as err:
                    print(f"Error {err}")
                    return [False, err]