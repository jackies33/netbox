






from paramiko import SSHException
from ..add_device import ADD_NB
from ..classifier import classifier_device_type
from ..my_pass import mylogin , mypass
import re
import time
import paramiko


class HPProCurve9xxx():
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



            def conn_ProCurve9xxx(self ,*args):
                print("<<< start hpe.py >>>")
                primary_ip = (f'{self.ip_conn}/{self.mask}')
                cmnd1 = '\nshow system information \n\n      '  # Commands
                cmnd2 = f'\nshow ip source-interface \n\n           '  # Commands
                cmnd3 = '\ndisplay device   \n\n        '  # Commands
                cmnd4 = '         \n\n'
                try:
                        ssh = paramiko.SSHClient()
                        ssh.load_system_host_keys()
                        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        ssh.connect(self.ip_conn,
                                    username=mylogin,
                                    password=mypass,
                                    look_for_keys=False,
                                    )

                        ssh1 = ssh.invoke_shell()
                except SSHException as e:
                    print (e)
                output = ''
                #while not output.endswith('Press any key to continue '):
                #    try:
                #       print("trying")
                #       output += ssh1.recv(1024).decode()
                #       print(output)
                #    except Exception as e:
                #        print(e)
                #        break
                list_serial_devices = []
                try:
                    time.sleep(25)
                    ssh1.send(cmnd4)
                    time.sleep(4)
                    ssh1.send(cmnd1)
                    time.sleep(4)
                    ssh1.send(cmnd2)
                    time.sleep(4)
                    ssh1.send(cmnd4)
                    time.sleep(4)
                    output1 = (ssh1.recv(9999999).decode("utf-8"))
                    manufacturer = 'Hewlett Packard Enterprise'

                    device_name = \
                    re.findall(r'System Name\s+:\s+\S+', output1, re.MULTILINE)[0].replace(" ", "").split("SystemName:")[1]
                    member_sn = \
                    re.findall(r'Serial Number\s+:\s+\S+', output1, re.MULTILINE)[0].replace(" ", "").split(
                        "SerialNumber:")[1]
                    interface_name = re.findall(f'Telnet   \| Configured IP Interface\s+\S+\s+{self.ip_conn}',
                                                output1, re.MULTILINE)[0].split("Interface")[1].split(self.ip_conn)[0].strip()
                    device_type= classifier_device_type(manufacturer,re.findall(r'HP.+Switch', output1 ,
                                                                                re.MULTILINE)[0].split("HP")[1].split("Switch")[0].strip())
                    print("<<< start hpe.py >>>")
                    list_serial_devices.append({'member_id': 0, 'sn_number': member_sn, 'master': False})
                    adding = ADD_NB(device_name, self.site_name, self.location, self.tenants,
                                    self.device_role,
                                    manufacturer, self.platform, device_type[0], primary_ip, interface_name,
                                    self.conn_scheme, self.management, self.racks, list_serial_devices,
                                    self.stack_enable)
                    result = adding.add_device()
                    return result
                except Exception as e:
                   print(f"Error {e}")
                   return [False, e]



