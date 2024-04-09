



import pynetbox


from .preparing import CONNECT_PREPARE
from .nb_exec.add_device import ADD_NB
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



class CORE():

        """
        Core of plugin for analyze data and make decision
        """

        def __init__(self, **kwargs):
            """
            Initialize the values
            """

        def add_edit_plugin(self,**kwargs):
            print("<<< Start core_exec.py >>>")
            ####call function for preparing data for connection to device
            if kwargs['purpose_value'] == 'add' and kwargs['data']['add']['management_status'] == 1:
                call = CONNECT_DEVICE()
                prep = call.add_preparing(**kwargs)
                print("<<< Start core_exec.py >>>")
                call = CONNECT_DEVICE()
                conn_data = call.connection_exec(**prep)
                print("<<< Start core_exec.py >>>")
            elif kwargs['purpose_value'] == 'edit':
                call = EXTRACT_NB()
                extract = call.extract_for_edit(**kwargs)
                print("<<< Start core_exec.py >>>")
                call = CONNECT_DEVICE()
                prep = call.edit_preparing(**extract)
                print("<<< Start core_exec.py >>>")
                call = CONNECT_DEVICE()
                conn_data = call.connection_exec(**prep)
                print("<<< Start core_exec.py >>>")
            else:
                return [False,None]
            ###call function for connection to device and collect the data

            if kwargs['purpose_value'] == 'add':
                call = ADD_NB()
                result = call.add_device(**conn_data)
                print("<<< Start core_exec.py >>>")
            elif kwargs['purpose_value'] == 'edit':
                call = PARSE_DATA()
                diff = call.compare_diff_for_edit(**conn_data)
                print("<<< Start core_exec.py >>>")
                if diff['data']['add']['stack_enable'] == True:
                        call = EDIT_NB()
                        result = call.edit_vc(**diff)
                        print("<<< Start core_exec.py >>>")
                elif diff['data']['add']['stack_enable'] == False:
                        call = EDIT_NB()
                        result = call.edit_device(**diff)
                        print("<<< Start core_exec.py >>>")
                else:
                    result = [False, None]
            else:
                result = [False,None]
            return result

class CONNECT_DEVICE():

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

        def connection_exec(self, **kwargs):
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


class PARSE_DATA():
        """
        Class for parse , compare data and etc
        """

        def __init__(self, **kwargs):
            """
            Initialize the values
            """
        def compare_diff_for_edit(self,**kwargs):
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


