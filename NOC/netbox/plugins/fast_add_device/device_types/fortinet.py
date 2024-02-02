



from ..add_device import ADD_NB
from ..classifier import classifier_device_type
from ..my_pass import mylogin , mypass ,rescue_login, rescue_pass
import re
import time
import paramiko
import datetime




class FORTINET_CONN():

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



            def conn_FortiGate(self, *args):
                print("<<< Start fortinet.py >>>")
                primary_ip = (f'{self.ip_conn}/{self.mask}')
                cmnd1 = '\n config global \n\n      '  # Commands
                cmnd2 = '\n get system status  \n\n           '  # Commands
                cmnd3 = '\n get system interface physical  \n\n        '  # Commands
                cmnd4 = '         \n\n           '
                ssh = paramiko.SSHClient()
                ssh.load_system_host_keys()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(self.ip_conn,
                            username=mylogin,
                            password=mypass,
                            look_for_keys=False)
                ssh1 = ssh.invoke_shell()
                list_serial_devices = []
                try:
                    time.sleep(1)
                    ssh1.send(cmnd1)
                    time.sleep(1)
                    ssh1.send(cmnd2)
                    time.sleep(1)
                    ssh1.send(cmnd3)
                    time.sleep(1)
                    ssh1.send(cmnd4)
                    time.sleep(1)
                    output1 = (ssh1.recv(9999999).decode("utf-8"))
                    time.sleep(1)
                    device_name = re.findall(f"Hostname: \S+", output1)[0].split("Hostname: ")[1]
                    interface_name = re.findall(f"==.+\n.+\n\s+ip: {self.ip_conn}", output1)[0]
                    interface_name = re.findall(f"==\[\S+\]", interface_name)[0].split("==[")[1].rsplit(']')[0]
                    device_type = re.findall(f"Version: \S+", output1)[0].split("Version: ")[1]
                    member_sn = re.findall(r'Serial-Number: \S+', output1)[0].split("Serial-Number: ")[1]
                    list_serial_devices.append({'member_id': 0, 'sn_number': member_sn, 'master': False})
                    manufacturer = 'Fortinet'
                    device_type = classifier_device_type(manufacturer ,device_type)
                    print("<<< Start fortinet.py >>>")
                    ssh1.close()
                    adding = ADD_NB(device_name, self.site_name, self.location, self.tenants, self.device_role,
                                    manufacturer, self.platform, device_type[0], primary_ip, interface_name,
                                    self.conn_scheme, self.management, self.racks, list_serial_devices, self.stack_enable)
                    result = adding.add_device()
                    return result
                except Exception as err:
                    print(f'\n\n{datetime.datetime.now()}\n\n{err}')
                    return [False, err]

