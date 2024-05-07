



from netmiko import ConnectHandler , NetMikoAuthenticationException, NetMikoTimeoutException, ReadException
import re


from ..classifier import classifier_device_type
from ..preparing import CONNECT_PREPARE





class HUAWEI_CONN():

            """
            Class for connection to different device
            """

            def __init__(self, **kwargs):
                """
                Initialize the values
                """


            def conn_Huawei(self ,**kwargs):
                print("<<< Start huawei.py >>>")
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
                type_device_for_conn = 'huawei'
                dict_for_template = {'ip_conn': ip_conn, 'type_device_for_conn': type_device_for_conn,
                                     'conn_scheme': conn_scheme}
                if conn_scheme == '2':
                    dict_for_template = {'ip_conn': ip_conn, 'type_device_for_conn': "huawei_telnet",
                                         'conn_scheme': conn_scheme}
                template = CONNECT_PREPARE()
                host1 = template.template_conn(**dict_for_template)
                print("<<< Start huawei.py >>>")
                try:

                    with ConnectHandler(**host1) as net_connect:
                        primary_ip = (f'{ip_conn}/{mask}')
                        output_name_result = net_connect.send_command('display current-configuration | include sysname',
                                                                      delay_factor=.5)  # command result
                        device_name = re.findall(r"sysname \S+", output_name_result)[0].split('sysname ')[1]
                        output_version = net_connect.send_command('display version',
                                                                  delay_factor=.5)
                        command_ip = (f'display ip interface brief  | include {ip_conn}')
                        output_ip = net_connect.send_command(command_ip, delay_factor=.5)
                        escaped_ip_address = re.escape(ip_conn)
                        re_ip = (f"(\S+)\s+{escaped_ip_address}")
                        interface_name = re.findall(re_ip, output_ip)[0]
                        manufacturer = 'Huawei Technologies Co.'
                        #device_type = classifier_device_type(manufacturer ,re.findall(r'NE20E-S2F|AR6120|NetEngine 8000 F1A-8H20Q'
                        #                                                            r'|S5700-28C-EI-24S|S5735-S48S4X|CE8851-32CQ8DQ-P|CE6881-48S6CQ', output_version)[0])
                        show_device = net_connect.send_command('display device',delay_factor=.5)
                        device_type = classifier_device_type(
                            manufacturer,re.findall(f".+\s+Device status:",
                                                    show_device, re.MULTILINE)[0].split("Device status:")[0].split("'s")[0].strip())
                        print("<<< Start huawei.py >>>")
                        list_serial_device = []
                        if stack_enable == True:
                            output_stack = net_connect.send_command('display stack', delay_factor=.5)
                            slave_output = re.findall(r"\d\s+Slave", output_stack)
                            standby_output = re.findall(r"\d\s+Standby", output_stack)
                            master_output = re.findall(r"\d\s+Master", output_stack)
                            for slave in slave_output:
                                member_id = slave.replace(" ", "").split('Slave')[0]
                                list_serial_device.append(
                                    {'member_id': member_id, 'sn_number': '', 'master': False})
                            for standby in standby_output:
                                member_id = standby.replace(" ", "").split('Standby')[0]
                                list_serial_device.append(
                                    {'member_id': member_id, 'sn_number': '', 'master': False})
                            for master in master_output:
                                member_id = master.replace(" ", "").split('Master')[0]
                                list_serial_device.append(
                                    {'member_id': member_id, 'sn_number': '', 'master': True})
                            output_manufacturer = net_connect.send_command('display device manufacture-info', delay_factor=.5)
                            member_output = re.findall(f'^\d\s+-\s+\S+', output_manufacturer, re.MULTILINE)
                            for member in member_output:
                                member_id = re.findall(r'\d\s+-\s+', member)[0].replace(" ", "")[0]
                                member_sn = re.findall(r'-\s+\S+', member)[0].replace(" ", "").split("-")[1]
                                for l in list_serial_device:
                                    if l['member_id'] == member_id:
                                        l['sn_number'] = member_sn

                        elif stack_enable == False:
                            output_sn_main = net_connect.send_command('display elabel', delay_factor=.5)
                            member_sn = re.findall(f"BarCode=\S+", output_sn_main, re.MULTILINE)[0].split("BarCode=")[1].strip()
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
                    print('\n\n not connect to ' + ip_conn + '\n\n')
                    print("<<< Start huawei.py >>>")
                    #### if ssh not work , script shall try via telnet
                    if conn_scheme == '1':
                        type_device_for_conn = 'huawei_telnet'
                        dict_for_template = {'ip_conn': ip_conn, 'type_device_for_conn': type_device_for_conn,
                                             'conn_scheme': 'telnet'}
                        template = CONNECT_PREPARE()
                        host1 = template.template_conn(**dict_for_template)
                        print("<<< Start huawei.py >>>")

                        try:

                            with ConnectHandler(**host1) as net_connect:
                                primary_ip = (f'{ip_conn}/{mask}')
                                output_name_result = net_connect.send_command(
                                    'display current-configuration | include sysname',
                                    delay_factor=.5)  # command result
                                device_name = re.findall(r"sysname \S+", output_name_result)[0].split('sysname ')[1]
                                #output_version = net_connect.send_command('display version',
                                #                                         delay_factor=.5)
                                command_ip = (f'display ip interface brief  | include {ip_conn}')
                                output_ip = net_connect.send_command(command_ip, delay_factor=.5)
                                escaped_ip_address = re.escape(ip_conn)
                                re_ip = (f"(\S+)\s+{escaped_ip_address}")
                                interface_name = re.findall(re_ip, output_ip)[0]
                                manufacturer = 'Huawei Technologies Co.'
                                device_type = classifier_device_type(
                                    manufacturer, re.findall(f".+\s+Device status:",
                                                             show_device, re.MULTILINE)[0].split("Device status:")
                                    [0].split("'s")[0].strip())
                                print("<<< Start huawei.py >>>")
                                list_serial_device = []
                                if stack_enable == True:
                                    output_stack = net_connect.send_command('display stack', delay_factor=.5)
                                    slave_output = re.findall(r"\d\s+Slave", output_stack)
                                    standby_output = re.findall(r"\d\s+Standby", output_stack)
                                    master_output = re.findall(r"\d\s+Master", output_stack)
                                    for slave in slave_output:
                                        member_id = slave.replace(" ", "").split('Slave')[0]
                                        list_serial_device.append(
                                            {'member_id': member_id, 'sn_number': '', 'master': False})
                                    for standby in standby_output:
                                        member_id = standby.replace(" ", "").split('Standby')[0]
                                        list_serial_device.append(
                                            {'member_id': member_id, 'sn_number': '', 'master': False})
                                    for master in master_output:
                                        member_id = master.replace(" ", "").split('Master')[0]
                                        list_serial_device.append(
                                            {'member_id': member_id, 'sn_number': '', 'master': True})
                                    output_manufacturer = net_connect.send_command('display device manufacture-info',
                                                                                   delay_factor=.5)
                                    member_output = re.findall(f'^\d\s+-\s+\S+', output_manufacturer, re.MULTILINE)
                                    for member in member_output:
                                        member_id = re.findall(r'\d\s+-\s+', member)[0].replace(" ", "")[0]
                                        member_sn = re.findall(r'-\s+\S+', member)[0].replace(" ", "").split("-")[1]
                                        for l in list_serial_device:
                                            if l['member_id'] == member_id:
                                                l['sn_number'] = member_sn

                                elif stack_enable == False:
                                    output_sn_main = net_connect.send_command('display elabel', delay_factor=.5)
                                    member_sn = \
                                    re.findall(f"BarCode=\S+", output_sn_main, re.MULTILINE)[0].split("BarCode=")[1].strip()
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
                            print('\n\n not connect to ' + ip_conn + '\n\n')
                            return [False, err]
                except ReadException as err:
                    print("<<< Start huawei.py >>>")
                    type_device_for_conn = 'huawei'
                    dict_for_template = {'ip_conn': ip_conn, 'type_device_for_conn': type_device_for_conn,
                                         'conn_scheme': conn_scheme}
                    template = CONNECT_PREPARE()
                    host1 = template.template_conn(**dict_for_template)
                    print("<<< Start huawei.py >>>")
                    try:

                        with ConnectHandler(**host1) as net_connect:
                            primary_ip = (f'{ip_conn}/{mask}')
                            pattern_output = r'<.*>'
                            output_name_result = net_connect.send_command(
                                'display current-configuration | include sysname',expect_string=pattern_output,
                                delay_factor=.5)  # command result
                            device_name = re.findall(r"sysname \S+", output_name_result)[0].split('sysname ')[1]
                            output_version = net_connect.send_command('display version',expect_string=pattern_output,
                                                                      delay_factor=.5)
                            command_ip = (f'display ip interface brief  | include {ip_conn}')
                            output_ip = net_connect.send_command(command_ip, expect_string=pattern_output, delay_factor=.5)
                            escaped_ip_address = re.escape(ip_conn)
                            re_ip = (f"(\S+)\s+{escaped_ip_address}")
                            interface_name = re.findall(re_ip, output_ip)[0]
                            manufacturer = 'Huawei Technologies Co.'
                            # device_type = classifier_device_type(manufacturer ,re.findall(r'NE20E-S2F|AR6120|NetEngine 8000 F1A-8H20Q'
                            #                                                            r'|S5700-28C-EI-24S|S5735-S48S4X|CE8851-32CQ8DQ-P|CE6881-48S6CQ', output_version)[0])
                            show_device = net_connect.send_command('display device', expect_string=pattern_output, delay_factor=.5)
                            device_type = classifier_device_type(
                                manufacturer, re.findall(f".+\s+Device status:",
                                                         show_device, re.MULTILINE)[0].split("Device status:")[0].split(
                                    "'s")[0].strip())
                            print("<<< Start huawei.py >>>")
                            list_serial_device = []
                            if stack_enable == True:
                                output_stack = net_connect.send_command('display stack', expect_string=pattern_output, delay_factor=.5)
                                slave_output = re.findall(r"\d\s+Slave", output_stack)
                                standby_output = re.findall(r"\d\s+Standby", output_stack)
                                master_output = re.findall(r"\d\s+Master", output_stack)
                                for slave in slave_output:
                                    member_id = slave.replace(" ", "").split('Slave')[0]
                                    list_serial_device.append(
                                        {'member_id': member_id, 'sn_number': '', 'master': False})
                                for standby in standby_output:
                                    member_id = standby.replace(" ", "").split('Standby')[0]
                                    list_serial_device.append(
                                        {'member_id': member_id, 'sn_number': '', 'master': False})
                                for master in master_output:
                                    member_id = master.replace(" ", "").split('Master')[0]
                                    list_serial_device.append(
                                        {'member_id': member_id, 'sn_number': '', 'master': True})
                                output_manufacturer = net_connect.send_command('display device manufacture-info', expect_string=pattern_output,
                                                                               delay_factor=.5)
                                member_output = re.findall(f'^\d\s+-\s+\S+', output_manufacturer, re.MULTILINE)
                                for member in member_output:
                                    member_id = re.findall(r'\d\s+-\s+', member)[0].replace(" ", "")[0]
                                    member_sn = re.findall(r'-\s+\S+', member)[0].replace(" ", "").split("-")[1]
                                    for l in list_serial_device:
                                        if l['member_id'] == member_id:
                                            l['sn_number'] = member_sn

                            elif stack_enable == False:
                                try:
                                    output_sn_main = net_connect.send_command_timing('display elabel', delay_factor=.5)
                                    if "[Y/N]:" in output_sn_main:
                                        output_sn_main += net_connect.send_command_timing('y')
                                    member_sn = \
                                    re.findall(f"BarCode=\S+", output_sn_main, re.MULTILINE)[0].split("BarCode=")[1].strip()
                                    list_serial_device.append({'member_id': 0, 'sn_number': member_sn, 'master': False})
                                except Exception as err:
                                   pass



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

                    except Exception as err:
                        pass

                except Exception as err:
                        return [False, err]



