


import re
from jnpr.junos.exception import ConnectAuthError,ConnectClosedError,ConnectError,ConnectTimeoutError
from jnpr.junos import Device
from lxml import etree
import time
import paramiko
from paramiko import SSHException



from ..classifier import classifier_device_type
from ..my_pass import mylogin , mypass



class JUNIPER_CONN():


            """
            Class for connection to different device
            """

            def __init__(self, **kwargs):
                    """
                    Initialize the values
                    """


            def conn_Juniper_rpc(self, **kwargs):
                # print('this is connect_to_device_juniper!!!!')
                # host1 = self.template_conn(ip_conn,manufacturer)
                print("<<< Start juniper.py >>>")
                ###consider data for collect and return
                try:
                    if kwargs['purpose_value'] == "add":
                        data = kwargs['data']['add']####add data for consider adding dict
                        data_for_add = kwargs['data']['add']
                    elif kwargs['purpose_value'] == "edit":
                        data = kwargs['data']['edit']#### edit data for consider data from extract_nb.py
                        data_for_add = kwargs['data']['add']
                    else:
                        return [False, "Undefined_device",None]
                    ip_conn = data['ip_conn']
                    mask = data['mask']
                    stack_enable = data['stack_enable']
                    try:

                        dev = Device(host=ip_conn, user=mylogin, password=mypass)
                        dev.open()
                        device_name = dev.facts['hostname']
                        device_type = dev.facts['model']
                        config = dev.rpc.get_config(filter_xml=etree.XML(f'''
                                                     <configuration>
                                                         <interfaces>
                                                             <interface>
                                                                <unit>
                                                                   <family>
                                                                      <inet>
                                                                         <address>
                                                                            <name>{ip_conn}/{mask}</name>
                                                                         </address>
                                                                      </inet>
                                                                   </family>
                                                                </unit>
                                                             </interface>
                                                         </interfaces>
                                                     </configuration>'''),
                                                    options={'database': 'committed', 'inherit': 'inherit'})

                        interface_name = ''
                        # interface_name = interfaces.xpath(f"//logical-interface[contains(address-family/address/name,'inet') and contains(address-family/address/ip-prefix,'{self.ip_conn}/{self.mask}')]/name")
                        for interface in config.xpath('//interface'):
                            interface_name = interface.find('name').text
                            for unit in interface.xpath('.//unit'):
                                unit = unit.find('name').text
                                if interface_name == 'fxp0':
                                    break
                                elif interface_name == 'vlan':
                                    interface_name = interface_name + unit
                                elif interface_name == 'irb':
                                    interface_name = (f'{interface_name}.{unit}')
                                elif "em" in interface_name:
                                    interface_name = interface_name
                        if interface_name == '':
                            config = dev.rpc.get_config(filter_xml=etree.XML(f'''
                                                                     <configuration>
                                                                         <interfaces>
                                                                             <interface>
                                                                                <unit>
                                                                                   <family>
                                                                                      <inet>
                                                                                         <address>
                                                                                            <name>{ip_conn}/32</name>
                                                                                         </address>
                                                                                      </inet>
                                                                                   </family>
                                                                                </unit>
                                                                             </interface>
                                                                         </interfaces>
                                                                     </configuration>'''),
                                                        options={'database': 'committed', 'inherit': 'inherit'})
                            for interface in config.xpath('//interface'):
                                interface_name = interface.find('name').text
                                for unit in interface.xpath('.//unit'):
                                    unit = unit.find('name').text
                                    if interface_name == 'fxp0':
                                        break
                                    elif interface_name == 'vlan':
                                        interface_name = interface_name + unit
                                    elif interface_name == 'irb':
                                        interface_name = (f'{interface_name}.{unit}')
                                    elif interface_name == "lo0":
                                        interface_name = f"lo{unit}"
                                    elif "em" in interface_name:
                                        interface_name = interface_name

                        else:
                            pass
                        list_serial_device = []
                        if stack_enable == True:
                            memb_count = 0
                            vc_info = dev.rpc.get_virtual_chassis_information()
                            # print(etree.tounicode(vc_info))
                            # vc_mode = vc_info.find('.//virtual-chassis-mode').text
                            members = vc_info.findall('.//member')
                            # if vc_mode == 'Enabled':
                            for member in members:
                                member_id = int(member.find('member-id').text)
                                member_status = member.find('member-status').text
                                if member_status == "Prsnt":
                                    member_serial_number = member.find('member-serial-number').text
                                    role = member.find('member-role').text
                                    if role == "Master*":
                                        member_role = True
                                    else:
                                        member_role = False
                                    # print(f"Member ID: {member_id}, Serial Status: {member_serial_status}")
                                    memb_count = memb_count + 1
                                    list_serial_device.append(
                                        {'member_id': member_id, 'sn_number': member_serial_number, 'master': member_role})
                                elif member_status == "NotPrsnt":
                                    pass
                            if memb_count == 1:
                                stack_enable = False
                                for l in list_serial_device:
                                    if l['master'] == True:
                                        l['master'] = False
                                    else:
                                        pass
                            elif memb_count > 1:
                                stack_enable = True
                        elif stack_enable == False:
                            inventory = dev.rpc.get_chassis_inventory()
                            serial_number = str(inventory.findtext('.//serial-number'))
                            list_serial_device.append(
                                {'member_id': 0, 'sn_number': serial_number, 'master': False})
                        dev.close()
                        # print('this is connect_to_device_juniper_out!!!!')
                        manufacturer = 'Juniper Networks'
                        device_type = classifier_device_type(manufacturer, device_type)
                        print("<<< Start juniper.py >>>")
                        ###update data dict for adding
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

                        return [True,kwargs]
                    except (ConnectAuthError, ConnectClosedError, ConnectError, ConnectTimeoutError) as err:  # exceptions
                                #######if rpc bad result - try to connect directly throuh ssh(paramiko)

                                print('\n\n not connect to ' + ip_conn + f'\n\n {err}')
                                print("<<< Start juniper.py >>>")
                                primary_ip = (f'{ip_conn}/{mask}')
                                cmnd1 = '\n show version \n\n      '  # Commands
                                cmnd2 = f'\n show configuration | display set| match {ip_conn}  \n\n           '  # Commands
                                cmnd3 = '\n show chassis hardware  \n\n        '  # Commands
                                cmnd4 = '         \n\n           '
                                cmnd5 = '\n show virtual-chassis \n '
                                ssh = paramiko.SSHClient()
                                ssh.load_system_host_keys()
                                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                                ssh.connect(ip_conn,
                                            username=mylogin,
                                            password=mypass,
                                            look_for_keys=False)
                                ssh1 = ssh.invoke_shell()
                                output = ''
                                while not output.endswith('> '):
                                    output += ssh1.recv(1024).decode()
                                list_serial_devices = []
                                try:
                                    time.sleep(1)
                                    ssh1.send(cmnd1)
                                    time.sleep(2)
                                    ssh1.send(cmnd4)
                                    time.sleep(2)
                                    ssh1.send(cmnd2)
                                    time.sleep(2)
                                    if stack_enable == True:
                                        ssh1.send(cmnd5)
                                    elif stack_enable == False:
                                        ssh1.send(cmnd3)
                                    time.sleep(2)
                                    ssh1.send(cmnd4)
                                    time.sleep(2)
                                    output1 = (ssh1.recv(9999999).decode("utf-8"))
                                    ssh1.close()
                                    device_name = re.findall(r"Hostname: \S+", output1)[0].split('Hostname: ')[1]
                                    manufacturer = 'juniper-networks'
                                    device_type = classifier_device_type(manufacturer,
                                                                         re.findall(r'Model: \S+', output1)[0].split('Model: ')[1].upper())
                                    print("<<< Start juniper.py >>>")
                                    interface_first = \
                                        re.findall(r'set interfaces \S+', output1, re.MULTILINE)[0].split('set interfaces ')[1]
                                    inetrface_count = \
                                        re.findall(r'unit \d+ family inet', output1)[0].split('unit ')[1].split(" family inet")[0]
                                    if interface_first == "vlan":
                                        interface_name = interface_first + inetrface_count
                                    elif interface_first == 'lo0':
                                        interface_name = f"lo{inetrface_count}"
                                    elif interface_first == 'irb':
                                        interface_name = (f'{interface_first}.{inetrface_count}')
                                    else:
                                        interface_name = interface_first
                                    list_serial_device = []
                                    if stack_enable == True:

                                        chassis_start = re.findall(r'\d \(FPC \d\)\s+ Prsnt\s+\S+\s+\S+\s+\d+\s+\S+', output1,
                                                                   re.MULTILINE)
                                        for chassis in chassis_start:
                                            member_id = \
                                                re.findall(r"\d+ \(FPC \d\)", chassis)[0].replace(" ", "").split("(FPC")[0]
                                            member_serial_number = \
                                                re.findall(r'Prsnt\s+\S+', chassis)[0].replace(" ", "").split("Prsnt")[1]
                                            member_role = re.findall(r'Linecard|Master|Backup', chassis)[0]
                                            if member_role == 'Master':
                                                member_role = True
                                            else:
                                                member_role = False
                                            list_serial_device.append(
                                                {'member_id': member_id, 'sn_number': member_serial_number,
                                                 'master': member_role})
                                    elif stack_enable == False:
                                        member_serial_number = \
                                            re.findall(r'Chassis\s+\S+', output1, re.MULTILINE)[0].replace(" ", "").split(
                                                "Chassis")[1]
                                        list_serial_device.append(
                                            {'member_id': 0, 'sn_number': member_serial_number, 'master': False})
                                    ###update data dict for adding
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

                                    return [True,kwargs]

                                except SSHException as err:
                                    print(f"\n\n\n{err}\n\n\n")
                                    return [False, ip_conn, err]
                    except Exception as e:
                        print(f"Error {e}")
                        return [False, ip_conn, e]

                except Exception as err:
                        try:
                            if kwargs['purpose_value'] == "add":
                                data = kwargs['data']['add']  ####add data for consider adding dict
                                data_for_add = kwargs['data']['add']
                            elif kwargs['purpose_value'] == "edit":
                                data = kwargs['data']['edit']  #### edit data for consider data from extract_nb.py
                                data_for_add = kwargs['data']['add']
                            else:
                                return [False, "Undefined device", None]
                            ip_conn = data['ip_conn']
                        except Exception as err:
                            return [False, "Undefined ip address", err]
                        return [False, ip_conn, err]






