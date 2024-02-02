





from ..add_device import ADD_NB
from ..classifier import classifier_device_type
from ..my_pass import mylogin , mypass ,rescue_login, rescue_pass
import re
import time
import paramiko
from paramiko import SSHException



class IBM():

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





            def conn_IBM_lenovo_sw(self ,*args):
                print("<<< Start ibm.py >>>")
                primary_ip = (f'{self.ip_conn}/{self.mask}')
                ssh = paramiko.SSHClient()
                ssh.load_system_host_keys()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                cmnd1 = 'en\n'
                cmnd2 = '\nshow system\n\n\n\n'
                ssh.connect(self.ip_conn,
                            username=mylogin,
                            password=mypass,
                            look_for_keys=False,
                            allow_agent=False)
                try:
                    ssh1 = ssh.invoke_shell()
                    time.sleep(4)
                    ssh1.send(cmnd1)
                    time.sleep(1)
                    ssh1.send(cmnd2)
                    time.sleep(1)
                    output_name_result = (ssh1.recv(65535).decode("utf-8"))
                    time.sleep(3)
                    ssh1.close()
                    preresult1 = re.findall(r'sysName:     \S+', output_name_result)[0].split('sysName:     ')[1]
                    device_name = preresult1.split('"')[1]
                    manufacturer = 'LENOVO'
                    device_type = classifier_device_type(manufacturer
                                                         ,re.findall(r'Flex System Fabric EN4093R 10Gb Scalable Switch', output_name_result))
                    print("<<< Start ibm.py >>>")
                    interface_name = 'EXTM'
                    list_serial_devices = []
                    member_sn = re.findall(r'Serial Number\s+:\s+\S+', output_name_result)[0].split(":")[1].split(".")[0]
                    list_serial_devices.append({'member_id': 0, 'sn_number': member_sn, 'master': False})
                    adding = ADD_NB(device_name, self.site_name, self.location, self.tenants, self.device_role,
                                    manufacturer, self.platform, device_type[0], primary_ip, interface_name,
                                    self.conn_scheme, self.management, self.racks, list_serial_devices,
                                    self.stack_enable)
                    result = adding.add_device()
                    return result
                except IndexError as err:
                    print(f"\n\n\n{err}\n\n\n")
                    return [False, err]
                except SSHException as err:
                    print(f"\n\n\n{err}\n\n\n")
                    return [False, err]
                except Exception as err:
                    print(f"Error {err}")
                    return [False, err]