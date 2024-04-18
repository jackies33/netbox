


from netmiko import ConnectHandler , NetMikoAuthenticationException, NetMikoTimeoutException
import re


from ..classifier import classifier_device_type
from ..preparing import CONNECT_PREPARE



class CISCO_CONN():

            """
            Class for connection to different device
            """

            def __init__(self, **kwargs):
                """
                Initialize the values
                """

            def conn_Cisco_IOS(self, **kwargs):
                print("<<< Start cisco.py >>>")
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
                type_device_for_conn = "cisco_ios"
                dict_for_template = {'ip_conn': ip_conn, 'type_device_for_conn': type_device_for_conn,
                                     'conn_scheme': conn_scheme}
                if conn_scheme == '2':
                    dict_for_template = {'ip_conn': ip_conn, 'type_device_for_conn': "cisco_ios_telnet",'conn_scheme': conn_scheme}
                template = CONNECT_PREPARE()
                host1 = template.template_conn(**dict_for_template)
                try:
                    with ConnectHandler(**host1) as net_connect:
                        primary_ip = (f'{ip_conn}/{mask}')
                        output_main = net_connect.send_command('show version', delay_factor=.5)
                        device_name = re.findall(f"\S+ uptime is", output_main)[0].split("uptime is")[0].strip()
                        manufacturer = 'Cisco Systems'
                        device_type = classifier_device_type(manufacturer,
                                                             re.findall(f"^cisco \S+", output_main, re.MULTILINE)[
                                                                 0].split("cisco")[1].strip())
                        print("<<< Start cisco.py >>>")
                        output_interface_name = net_connect.send_command(
                            f'show ip interface brief | include {ip_conn}', delay_factor=.5)
                        interface_name = \
                        re.findall(f"^\S+\s+{ip_conn}", output_interface_name, re.MULTILINE)[0].split(
                            ip_conn)[0].strip()
                        list_serial_device = []
                        if stack_enable == True:
                            output_switch = net_connect.send_command('show switch', delay_factor=.5)
                            member_output = re.findall(r"\d\s+Member \S+", output_switch)
                            master_output = re.findall(r"\d\s+Master \S+", output_switch)[0]
                            for member in member_output:
                                member_id = member.replace(" ", "").split('Member')[0]
                                list_serial_device.append(
                                    {'member_id': member_id, 'sn_number': '',
                                     'master': False})

                            master_id = master_output.replace(" ", "").split('Master')[0]
                            list_serial_device.append(
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
                                for l in list_serial_device:
                                    if l['member_id'] == member_id:
                                        l['sn_number'] = member_sn

                        elif stack_enable == False:
                            serial_number = \
                            re.findall(f'Processor board ID \S+', output_main)[0].split('Processor board ID ')[1]
                            list_serial_device.append(
                                {'member_id': 0, 'sn_number': serial_number, 'master': False})
                        net_connect.disconnect()
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


                except (NetMikoAuthenticationException, NetMikoTimeoutException) as err:  # exceptions
                    #### if ssh not work , script shall try via telnet
                    if conn_scheme == '1':
                        print('\n\n not connect to (with ssh)' + ip_conn + '\n\n')
                        print("<<< Start cisco.py >>>")
                        type_device_for_conn = "cisco_ios_telnet"
                        dict_for_template = {'ip_conn': ip_conn, 'type_device_for_conn': type_device_for_conn,'conn_scheme': 'telnet'}
                        template = CONNECT_PREPARE()
                        host1 = template.template_conn(**dict_for_template)
                        print("<<< Start cisco.py >>>")
                        try:
                            with ConnectHandler(**host1) as net_connect:
                                primary_ip = (f'{ip_conn}/{mask}')
                                output_main = net_connect.send_command('show version', delay_factor=.5)
                                device_name = re.findall(f"\S+ uptime is", output_main)[0].split("uptime is")[0].strip()
                                manufacturer = 'Cisco Systems'
                                device_type = classifier_device_type(manufacturer,
                                                                     re.findall(f"^cisco \S+", output_main,
                                                                                re.MULTILINE)[
                                                                         0].split("cisco")[1].strip())
                                print("<<< Start cisco.py >>>")
                                output_interface_name = net_connect.send_command(
                                    f'show ip interface brief | include {ip_conn}', delay_factor=.5)
                                interface_name = \
                                    re.findall(f"^\S+\s+{ip_conn}", output_interface_name, re.MULTILINE)[0].split(
                                        ip_conn)[0].strip()
                                list_serial_device = []
                                if stack_enable == True:
                                    output_switch = net_connect.send_command('show switch', delay_factor=.5)
                                    member_output = re.findall(r"\d\s+Member \S+", output_switch)
                                    master_output = re.findall(r"\d\s+Master \S+", output_switch)[0]
                                    for member in member_output:
                                        member_id = member.replace(" ", "").split('Member')[0]
                                        list_serial_device.append(
                                            {'member_id': member_id, 'sn_number': '',
                                             'master': False})

                                    master_id = master_output.replace(" ", "").split('Master')[0]
                                    list_serial_device.append(
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
                                        for l in list_serial_device:
                                            if l['member_id'] == member_id:
                                                l['sn_number'] = member_sn

                                elif stack_enable == False:
                                    serial_number = \
                                        re.findall(f'Processor board ID \S+', output_main)[0].split(
                                            'Processor board ID ')[1]
                                    list_serial_device.append(
                                        {'member_id': 0, 'sn_number': serial_number, 'master': False})

                                net_connect.disconnect()
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
                        except (NetMikoAuthenticationException, NetMikoTimeoutException) as err:  # exceptions
                            print('\n\n not connect to ' + ip_conn + '\n\n')
                            return [False, err]
                except Exception as err:
                    print(f"Error {err}")
                    return [False, err]

            def conn_Cisco_IOS_XR(self, **kwargs):
                print("<<< Start cisco.py >>>")
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
                type_device_for_conn = "cisco_xr"
                dict_for_template = {'ip_conn':ip_conn,'type_device_for_conn':type_device_for_conn,'conn_scheme':conn_scheme}
                template = CONNECT_PREPARE()
                host1 = template.template_conn(**dict_for_template)
                print("<<< Start cisco.py >>>")
                try:
                    with ConnectHandler(**host1) as net_connect:
                        list_serial_device =[]
                        primary_ip = (f'{ip_conn}/{mask}')
                        output_hostname = net_connect.send_command('show running-config hostname', delay_factor=.5)
                        device_name = \
                        re.findall(r'hostname \S+', output_hostname)[0].replace(" ", "").split("hostname")[1]
                        output_version = net_connect.send_command('show version', delay_factor=.5)
                        manufacturer = 'Cisco Systems'
                        device_type = re.findall(f"cisco \S+", output_version, re.MULTILINE)[0].split("cisco")[
                            1].strip()
                        if device_type == "ASR9K":
                            device_type = classifier_device_type(manufacturer,
                                                                 re.findall(f"\S+\s+Chassis", output_version,
                                                                            re.MULTILINE)[0].replace(" ", "").split(
                                                                     "Chassis")[0])
                        else:
                            device_type = classifier_device_type(manufacturer, device_type)
                        print("<<< Start cisco.py >>>")
                        output_interface_name = net_connect.send_command(
                            f'show ip interface brief | include {ip_conn}', delay_factor=.5)
                        interface_name = \
                        re.findall(f"^\S+\s+{ip_conn}", output_interface_name, re.MULTILINE)[0].split(self.ip_conn)[
                            0].strip()
                        show_inventory = net_connect.send_command(f'show inventory rack', delay_factor=.5)
                        member_sn1 = re.findall(f'{device_type[1]}\s+\S+|{device_type[1]}\S+\s+\S+', show_inventory)[
                            0].split()
                        member_sn = member_sn1[1]
                        if member_sn1[0] == device_type[1]:
                            pass
                        elif member_sn1[0] != device_type[1]:

                            device_type = device_type = classifier_device_type(manufacturer, member_sn1[0])
                            print("<<< Start cisco.py >>>")
                        list_serial_device.append({'member_id': 0, 'sn_number': member_sn, 'master': False})
                        net_connect.disconnect()
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
                except (NetMikoAuthenticationException, NetMikoTimeoutException) as err:  # exceptions
                    print('\n\n not connect to ' + self.ip_conn + '\n\n')
                    return [False, err]

            def conn_Cisco_NXOS(self,**kwargs):
                   print("<<< Start cisco.py >>>")
                   if kwargs['purpose_value'] == "add":
                       data = kwargs['data']['add']  ####add data for consider adding dict
                       data_for_add = kwargs['data']['add']
                   elif kwargs['purpose_value'] == "edit":
                       data = kwargs['data']['edit']  #### edit data for consider data from extract_nb.py
                       data_for_add = kwargs['data']['add']
                   else:
                       return [False, None]
                   ip_conn = data['ip_conn']
                   mask = data['mask']
                   stack_enable = data['stack_enable']
                   conn_scheme = data['conn_scheme']
                   type_device_for_conn = "cisco_nxos"
                   dict_for_template = {'ip_conn': ip_conn, 'type_device_for_conn': type_device_for_conn,
                                        'conn_scheme': conn_scheme}
                   template = CONNECT_PREPARE()
                   host1 = template.template_conn(**dict_for_template)
                   print("<<< Start cisco.py >>>")
                   try:
                            with ConnectHandler(**host1) as net_connect:
                                    primary_ip = (f'{ip_conn}/{mask}')
                                    output1 = net_connect.send_command('show hostname', delay_factor=.5)
                                    device_name = re.findall(r'\S+', output1)[0]
                                    output2 = net_connect.send_command('show version',delay_factor=.5)  # command result
                                    output_name_result = re.findall(r'Hardware\n.+', output2)[0]
                                    manufacturer = 'Cisco Systems'
                                    device_type = classifier_device_type(manufacturer,re.findall(r'cisco Nexus7700 C7702|cisco Nexus 6001', output_name_result)[0].split("cisco")[1].strip())
                                    print("<<< Start cisco.py >>>")
                                    interface_name = 'mgmt0'
                                    list_serial_device = []
                                    serial_number = re.findall(f'Processor board ID \S+', output2)[0].split('Processor board ID ')[1]
                                    list_serial_device.append({'member_id': 0, 'sn_number': serial_number, 'master': False})
                                    net_connect.disconnect()
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

                   except (NetMikoAuthenticationException, NetMikoTimeoutException) as err:  # exceptions
                        print('\n\n not connect to ' + ip_conn + '\n\n')
                        return [False, err]
                   except Exception as err:
                       print(f"Error {err}")
                       return [False, err]

            def conn_Cisco_ASA(self,**kwargs):
                   print("<<< Start cisco.py >>>")
                   if kwargs['purpose_value'] == "add":
                       data = kwargs['data']['add']  ####add data for consider adding dict
                       data_for_add = kwargs['data']['add']
                   elif kwargs['purpose_value'] == "edit":
                       data = kwargs['data']['edit']  #### edit data for consider data from extract_nb.py
                       data_for_add = kwargs['data']['add']
                   else:
                       return [False, None]
                   ip_conn = data['ip_conn']
                   mask = data['mask']
                   stack_enable = data['stack_enable']
                   conn_scheme = data['conn_scheme']
                   type_device_for_conn = "cisco_asa"
                   dict_for_template = {'ip_conn': ip_conn, 'type_device_for_conn': type_device_for_conn,
                                        'conn_scheme': conn_scheme}
                   template = CONNECT_PREPARE()
                   host1 = template.template_conn(**dict_for_template)
                   print("<<< Start cisco.py >>>")
                   try:
                            with ConnectHandler(**host1) as net_connect:
                                    primary_ip = (f'{ip_conn}/{mask}')
                                    output_version = net_connect.send_command('show version', delay_factor=.5)
                                    output_name = net_connect.send_command('show hostname', delay_factor=.5)
                                    output_interface = net_connect.send_command(f'show interface ip brief | include {ip_conn}', delay_factor=.5)
                                    device_name = re.findall(r'\S+', output_name)[0]
                                    manufacturer = 'Cisco Systems'
                                    device_type = re.findall(f'Hardware:\s+\S+', output_version)[0].split("Hardware:")[1].split()[0]
                                    if "," in device_type:
                                        device_type = device_type.split(",")[0]
                                    interface_name = re.findall(f"^\S+\s+{ip_conn}", output_interface, re.MULTILINE)[0].split(ip_conn)[0].strip()
                                    serial_number = re.findall(f"Serial Number:\s+\S+", output_version)[0].split("Serial Number:")[1].split()[0]
                                    device_type = classifier_device_type(manufacturer,device_type)
                                    print("<<< Start cisco.py >>>")
                                    list_serial_device = []
                                    list_serial_device.append({'member_id': 0, 'sn_number': serial_number, 'master': False})
                                    net_connect.disconnect()
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

                   except (NetMikoAuthenticationException, NetMikoTimeoutException) as err:  # exceptions
                        print('\n\n not connect to ' + ip_conn + '\n\n')
                        return [False, err]
                   except Exception as err:
                       print(f"Error {err}")
                       return [False, err]

