


from ..add_device import ADD_NB
from ..classifier import classifier_device_type
from ..my_pass import mylogin , mypass ,rescue_login, rescue_pass
import re
from airwaveapiclient import AirWaveAPIClient





class ARUBA_OS():
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


            def conn_AWMP(self ,*args):
                print("<<< Start aruba.py >>>")
                airwave = AirWaveAPIClient(username=mylogin, password=mypass, url=f'https://{self.ip_conn}')
                try:
                    airwave.login()
                    output = airwave.amp_stats().text
                    manufacturer = "Hewlett Packard Enterprise"
                    device_type = classifier_device_type(manufacturer
                                                         ,re.findall("<name>.*</name>", output)[0].split('<name>')[1].split
                                                             ('</name>'))
                    print("<<< Start aruba.py >>>")
                    primary_ip = (f'{self.ip_conn}/{self.mask}')
                    interface_name = "VirtInt"
                    device_name = f'AWMP_{self.ip_conn}'
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