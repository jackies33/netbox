



import re
import time
import paramiko
import datetime




from ..classifier import classifier_device_type
from ..my_pass import mylogin , mypass




class FORTINET_CONN():

            """
            Class for connection to different device
            """

            def __init__(self, **kwargs):
                """
                Initialize the values
                """


            def conn_FortiGate(self, **kwargs):
                print("<<< Start fortinet.py >>>")
                if kwargs['purpose_value'] == "add":
                    data = kwargs['data']['add']####add data for consider adding dict
                    data_for_add = kwargs['data']['add']
                elif kwargs['purpose_value'] == "edit":
                    data = kwargs['data']['edit']#### edit data for consider data from extract_nb.py
                    data_for_add = kwargs['data']['add']
                else:
                    return [False,None]
                ip_conn = data['ip_conn']
                mask = data['mask']
                stack_enable = data['stack_enable']
                conn_scheme = data['conn_scheme']
                primary_ip = (f'{ip_conn}/{mask}')
                cmnd1 = '\n config global \n\n      '  # Commands
                cmnd2 = '\n get system status  \n\n           '  # Commands
                cmnd3 = '\n get system interface physical  \n\n        '  # Commands
                cmnd4 = '         \n\n           '
                ssh = paramiko.SSHClient()
                ssh.load_system_host_keys()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ip_conn,
                            username=mylogin,
                            password=mypass,
                            look_for_keys=False)
                ssh1 = ssh.invoke_shell()
                list_serial_device = []
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
                    interface_name = re.findall(f"==.+\n.+\n\s+ip: {ip_conn}", output1)[0]
                    interface_name = re.findall(f"==\[\S+\]", interface_name)[0].split("==[")[1].rsplit(']')[0]
                    device_type = re.findall(f"Version: \S+", output1)[0].split("Version: ")[1]
                    member_sn = re.findall(r'Serial-Number: \S+', output1)[0].split("Serial-Number: ")[1]
                    list_serial_device.append({'member_id': 0, 'sn_number': member_sn, 'master': False})
                    manufacturer = 'Fortinet'
                    device_type = classifier_device_type(manufacturer ,device_type)
                    print("<<< Start fortinet.py >>>")
                    ssh1.close()
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
                            'stack_enable': data['stack_enable'],
                            'tg_resource_group': data['tg_resource_group'],
                            'map_resource_group': data['map_resource_group'],
                            'name_of_establishment': data['name_of_establishment']
                        }
                    )

                    return kwargs
                except Exception as err:
                    print(f'\n\n{datetime.datetime.now()}\n\n{err}')
                    return [False, err]

