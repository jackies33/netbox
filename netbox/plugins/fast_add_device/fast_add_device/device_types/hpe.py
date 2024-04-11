





import re
import time
import paramiko
from paramiko import SSHException


from ..classifier import classifier_device_type
from ..my_pass import mylogin , mypass



class HPProCurve9xxx():
            """
            Class for connection to different device
            """

            def __init__(self, **kwargs):
                """
                Initialize the values
                """



            def conn_ProCurve9xxx(self ,**kwargs):
                print("<<< start hpe.py >>>")
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
                cmnd1 = '\nshow system information \n\n      '  # Commands
                cmnd2 = f'\nshow ip source-interface \n\n           '  # Commands
                cmnd3 = '\ndisplay device   \n\n        '  # Commands
                cmnd4 = '         \n\n'
                try:
                        ssh = paramiko.SSHClient()
                        ssh.load_system_host_keys()
                        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        ssh.connect(ip_conn,
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
                list_serial_device = []
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
                    interface_name = re.findall(f'Telnet   \| Configured IP Interface\s+\S+\s+{ip_conn}',
                                                output1, re.MULTILINE)[0].split("Interface")[1].split(ip_conn)[0].strip()
                    device_type= classifier_device_type(manufacturer,re.findall(r'HP.+Switch', output1 ,
                                                                                re.MULTILINE)[0].split("HP")[1].split("Switch")[0].strip())
                    print("<<< start hpe.py >>>")
                    list_serial_device.append({'member_id': 0, 'sn_number': member_sn, 'master': False})
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
                            'map_resource_group': data['map_resource_group']
                        }
                    )

                    return kwargs
                except Exception as e:
                   print(f"Error {e}")
                   return [False, e]



