

#external imports
from concurrent.futures import ThreadPoolExecutor
import functools
import pynetbox
import csv
from io import TextIOWrapper

#internal imports
from .preparing import CONNECT_PREPARE,CSV_PARSE
from .nb_exec.add_device import ADD_NB
from .nb_exec.add_device_from_csv import ADD_NB_CSV
from .nb_exec.extract_nb import EXTRACT_NB
from .nb_exec.edit_device import EDIT_NB
from .my_pass import netbox_url,netbox_api_token
from .device_types.huawei import HUAWEI_CONN
from .device_types.juniper import JUNIPER_CONN
from .device_types.cisco import CISCO_CONN
from .device_types.fortinet import FORTINET_CONN
from .device_types.ibm import IBM
from .device_types.aruba import ARUBA_OS
from .device_types.linux import LINUX
from .device_types.hpe import HPProCurve9xxx
from .device_types.mikrotik import MIKROTIK_CONN
from .device_types.qtech import QTECH_CONN



class CORE():#main class of plugin

        """
        Core of plugin for analyze data and make decisions
        """

        def __init__(self, **kwargs):
            """
            Initialize the values
            """

        def add_edit_plugin(self,**kwargs):#method for make tasks in "add" and "edit" parts of pligin
            print("<<< Start core_exec.py >>>")
            ####call function for preparing data for connection to device
            if kwargs['purpose_value'] == 'add' and kwargs['data']['add']['management_status'] == 1:
                call = CONNECT_DEVICE()
                prep = call.add_preparing(**kwargs)#prepare data for connect to device
                print("<<< Start core_exec.py >>>")
                call = CONNECT_DEVICE()
                conn_data = call.connection_exec(**prep)#connection executing to target device, parse and prepare data for adding to netbox
                print("<<< Start core_exec.py >>>")
            elif kwargs['purpose_value'] == 'edit':
                call = EXTRACT_NB()
                extract = call.extract_for_edit(**kwargs)#extract all data about recieved device from netbox
                if extract[0] == False:
                    return [False, extract[1]]
                elif extract[0] == True:
                    extract = extract[1]
                print("<<< Start core_exec.py >>>")
                call = CONNECT_DEVICE()
                prep = call.edit_preparing(**extract)#prepare data for connect to device
                print("<<< Start core_exec.py >>>")
                call = CONNECT_DEVICE()
                conn_data = call.connection_exec(**prep)#connection executing to target device, parse and prepare data for next tasks
                print("<<< Start core_exec.py >>>")
            else:
                return [False,None]
            ###call function for connection to device and collect the data

            if kwargs['purpose_value'] == 'add':
                call = ADD_NB()
                result = call.add_device(**conn_data)#add device to netbox
                print("<<< Start core_exec.py >>>")
            elif kwargs['purpose_value'] == 'edit':
                call = PARSE_DATA()
                diff = call.compare_diff_for_edit(**conn_data)#compare differents between extracted data fro netbox and collected from connection to device
                print("<<< Start core_exec.py >>>")
                if diff['data']['add']['stack_enable'] == True:
                        call = EDIT_NB()
                        result = call.edit_vc(**diff)#edit device, but that is stack , this devices will be delete and add for new then
                        print("<<< Start core_exec.py >>>")
                elif diff['data']['add']['stack_enable'] == False:
                        call = EDIT_NB()
                        result = call.edit_device(**diff)# edit device , only changed data will be edit
                        print("<<< Start core_exec.py >>>")
                else:
                    result = [False, None]
            else:
                result = [False,None]
            return result

        def add_offline(self, **kwargs):
            print("<<< Start core_exec.py >>>")
            call = ADD_NB()
            result = call.add_device(**kwargs)
            return result

        def add_csv(self,csv_file): #method for add ,multiple devices by csv file
            print("<<< Start core_exec.py >>>")
            list_bad_result = []
            list_success_result = []
            csv_content = TextIOWrapper(csv_file, encoding='cp866')#encode in specific format because in csv file might be latin characters
            csv_reader = csv.DictReader(csv_content)
            list_for_connect = []
            call = CSV_PARSE()#consider instance of class for recieve some data from netbox, parsing it and prepare data for connection to devices
            my_list = []
            for row in csv_reader:
                my_list.append(row)
            with ThreadPoolExecutor(max_workers=30) as executor:#use multiple stream for quicker get and parse data
                partial_func = functools.partial(call.find_out_csv_values)
                for data in executor.map(partial_func, my_list):
                    list_for_connect.append(data)
            list_bad = [item for item in list_for_connect if item['data']['add']['conn_scheme'] == False]
            list_for_connect = [item for item in list_for_connect if item['data']['add']['conn_scheme'] != False]
            for r in list_bad:
                list_bad_result.append(str(r['data']['add']['primary_ip']))
            list_after_conn = []
            call = CONNECT_DEVICE()#consider istance of class for connection to devices
            with ThreadPoolExecutor(max_workers=30) as executor:#use multiple stream for quicker get and parse data from connection to devices
                partial_func = functools.partial(call.connection_csv_exec)
                for data in executor.map(partial_func, list_for_connect):
                    list_after_conn.append(data)
            print("<<< Start core_exec.py >>>")
            for l in list_after_conn:
                nb = pynetbox.api(url=netbox_url, token=netbox_api_token)
                nb.http_session.verify = False
                call = CSV_PARSE()
                devices = nb.dcim.devices.all()
                list_devices_name = []
                for dev in devices:
                    list_devices_name.append(dev)
                update_list_after_connect=[]
                for l in list_after_conn:
                    result = call.check_exist_devices(list_devices_name, l)
                    data = result['data']['add']
                    if data['exist_device'] == True:
                        list_bad_result.append(data['device_name'])#check which device already exist in netbox and add it in bad list for report
                    elif data['exist_device'] == False:
                        update_list_after_connect.append(result)#prepare list which include devices for add
                for l in update_list_after_connect:
                    call = ADD_NB_CSV()
                    result = call.add_device_csv(**l)#add to netbox
                    if result[0] == False:
                        pass
                    elif result[0] == True:
                        list_success_result.append(result[1])
            return [True, [list_bad_result, list_success_result]]



class CONNECT_DEVICE():#func for parse and prepare data for connection and others tasks

        """
        Class for prepare data before connection to device
        """

        def __init__(self, **kwargs):
                    """
                    Initialize the values
                    """

        def add_preparing(self, **kwargs):
            print("<<< Start core_exec.py >>>")
            data = kwargs['data']['add']
            primary_ip = data['primary_ip']
            ip_conn = primary_ip.split('/')[0]
            mask = primary_ip.split('/')[1]
            connecting = CONNECT_PREPARE()
            conn_scheme = connecting.check_ssh(**{'ip_conn':ip_conn})
            print("<<< Start core_exec.py >>>")
            if conn_scheme == 0:
                return [False, "No connection to device! "]
            if conn_scheme == 'telnet':
                conn_scheme = '2'
            if conn_scheme == 'ssh':
                conn_scheme = '1'
            nb = pynetbox.api(url=netbox_url, token=netbox_api_token)
            nb.http_session.verify = False
            platform_main = nb.dcim.platforms.get(id=data['platform'])
            platform = str(platform_main)
            platform_id = int(platform_main.id)
            data.update({'ip_conn':ip_conn,'mask':mask,
                         'platform_name':platform,'platform':platform_id,
                         'primary_ip':primary_ip,'conn_scheme':conn_scheme

            })
            return kwargs

        def edit_preparing(self,**kwargs):
            print("<<< Start core_exec.py >>>")
            data = kwargs['data']['edit']
            primary_ip = data['primary_ip']
            ip_conn = primary_ip.split('/')[0]
            mask = primary_ip.split('/')[1]
            conn_scheme = data['conn_scheme']
            if conn_scheme == 'telnet':
                conn_scheme = '2'
            if conn_scheme == 'ssh':
                conn_scheme = '1'
            nb = pynetbox.api(url=netbox_url, token=netbox_api_token)
            nb.http_session.verify = False
            platform_main = nb.dcim.platforms.get(id=data['platform'])
            platform = str(platform_main)
            platform_id = int(platform_main.id)
            data.update({'ip_conn': ip_conn, 'mask': mask,
                         'platform_name': platform, 'platform_id': platform_id,
                         'primary_ip':primary_ip,'conn_scheme':conn_scheme

            })
            return kwargs

        def add_csv_preparing(self, kwargs):
            print("<<< Start core_exec.py >>>")
            data = kwargs['data']['add']
            primary_ip = data['primary_ip']
            ip_conn = primary_ip.split('/')[0]
            mask = primary_ip.split('/')[1]
            connecting = CONNECT_PREPARE()
            conn_scheme = connecting.check_ssh(**{'ip_conn': ip_conn})
            print("<<< Start core_exec.py >>>")
            if conn_scheme == 'telnet':
                conn_scheme = '2'
            elif conn_scheme == 'ssh':
                conn_scheme = '1'
            try:
                nb = pynetbox.api(url=netbox_url, token=netbox_api_token)
                nb.http_session.verify = False
                platform_main = nb.dcim.platforms.get(name=data['platform'])
                platform = str(platform_main.name)
                platform_id = int(platform_main.id)
            except Exception as err:
                platform = None
                platform_id = None
            data.update({'ip_conn': ip_conn, 'mask': mask,
                         'platform_name': platform, 'platform': platform_id,
                         'primary_ip': primary_ip, 'conn_scheme': conn_scheme

                         })
            return kwargs


        def connection_exec(self, **kwargs):# method for consider and execute connection to devices
            print("<<< Start core_exec.py >>>")

            platform_mappings = {
                "Huawei.VRP": (HUAWEI_CONN, "conn_Huawei"),
                "Juniper.JUNOS": (JUNIPER_CONN, "conn_Juniper_rpc"),
                "Cisco.IOS": (CISCO_CONN, "conn_Cisco_IOS"),
                "Cisco.IOSXR": (CISCO_CONN, "conn_Cisco_IOS_XR"),
                "IBM.NOS": (IBM, "conn_IBM_lenovo_sw"),
                "Cisco.NXOS": (CISCO_CONN, "conn_Cisco_NXOS"),
                "Aruba.ArubaOS": (ARUBA_OS, "conn_AWMP"),
                "Fortinet.Fortigate": (FORTINET_CONN, "conn_FortiGate"),
                "OS.Linux": (LINUX, "conn_OS_Linux"),
                "HP.ProCurve9xxx": (HPProCurve9xxx, "conn_ProCurve9xxx"),
                "MikroTik.RouterOS": (MIKROTIK_CONN, "conn_RouterOS"),
                "Cisco.ASA": (CISCO_CONN, "conn_Cisco_ASA"),
                "Qtech.QSW": (QTECH_CONN, "conn_qtech")
            }
            platform = None
            if kwargs['purpose_value'] == 'add':
                platform = kwargs['data']['add']['platform_name']
            elif kwargs['purpose_value'] == 'edit':
                platform = kwargs['data']['edit']['platform_name']
            if platform != None:
                connection_class, method_name = platform_mappings.get(platform, (None, None))
                if connection_class is not None and method_name is not None:
                    call = connection_class()
                    data_from_conn = getattr(call, method_name)(**kwargs)
                    return data_from_conn
                else:
                    return [False, None]


        def connection_csv_exec(self, kwargs):# method for consider and execute connection to devices for
            # csv part of lugin , so this another method because call via mutilple stream method
            print("<<< Start core_exec.py >>>")

            platform_mappings = {
                "Huawei.VRP": (HUAWEI_CONN, "conn_Huawei"),
                "Juniper.JUNOS": (JUNIPER_CONN, "conn_Juniper_rpc"),
                "Cisco.IOS": (CISCO_CONN, "conn_Cisco_IOS"),
                "Cisco.IOSXR": (CISCO_CONN, "conn_Cisco_IOS_XR"),
                "IBM.NOS": (IBM, "conn_IBM_lenovo_sw"),
                "Cisco.NXOS": (CISCO_CONN, "conn_Cisco_NXOS"),
                "Aruba.ArubaOS": (ARUBA_OS, "conn_AWMP"),
                "Fortinet.Fortigate": (FORTINET_CONN, "conn_FortiGate"),
                "OS.Linux": (LINUX, "conn_OS_Linux"),
                "HP.ProCurve9xxx": (HPProCurve9xxx, "conn_ProCurve9xxx"),
                "MikroTik.RouterOS": (MIKROTIK_CONN, "conn_RouterOS"),
                "Cisco.ASA": (CISCO_CONN, "conn_Cisco_ASA"),
                "Qtech.QSW": (QTECH_CONN, "conn_qtech")
            }
            platform = None
            if kwargs['purpose_value'] == 'add':
                platform = kwargs['data']['add']['platform_name']
            elif kwargs['purpose_value'] == 'edit':
                platform = kwargs['data']['edit']['platform_name']
            if platform != None:
                connection_class, method_name = platform_mappings.get(platform, (None, None))
                if connection_class is not None and method_name is not None:
                    call = connection_class()
                    data_from_conn = getattr(call, method_name)(**kwargs)
                    return data_from_conn
                else:
                    return [False, kwargs['data']['add']['primary_ip']]


class PARSE_DATA():
        """
        Class for parse , compare data and etc
        """

        def __init__(self, **kwargs):
            """
            Initialize the values
            """
        def compare_diff_for_edit(self,**kwargs):#method for parse and make diff dictionary for get difference
            print("<<< Start core_exec.py >>>")
            new_values = {}
            diff_data = kwargs['data']['diff']
            for key, value in kwargs['data']['add'].items():
                if key not in kwargs['data']['edit'] or value != kwargs['data']['edit'][key]:
                    new_values[key] = value
            diff_data.update(new_values)
            return kwargs


if __name__ == '__main__':
    print("__main__")


