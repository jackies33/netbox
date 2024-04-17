


import re
import time
import paramiko
from paramiko import SSHException



from ..classifier import classifier_device_type
from ..my_pass import mylogin , mypass




class IBM():

            """
            Class for connection to different device
            """

            def __init__(self, **kwargs):
                """
                Initialize the values
                """

            def conn_IBM_lenovo_sw(self ,**kwargs):
                print("<<< Start ibm.py >>>")
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
                ssh = paramiko.SSHClient()
                ssh.load_system_host_keys()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                cmnd1 = 'en\n'
                cmnd2 = '\nshow system\n\n\n\n'
                ssh.connect(ip_conn,
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
                    list_serial_device = []
                    member_sn = re.findall(r'Serial Number\s+:\s+\S+', output_name_result)[0].split(":")[1].split(".")[0]
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
                except IndexError as err:
                    print(f"\n\n\n{err}\n\n\n")
                    return [False, err]
                except SSHException as err:
                    print(f"\n\n\n{err}\n\n\n")
                    return [False, err]
                except Exception as err:
                    print(f"Error {err}")
                    return [False, err]