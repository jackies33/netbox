


import socket
import pynetbox
import telnetlib
from unidecode import unidecode
import re


from .my_pass import mylogin , mypass ,rescue_login, rescue_pass,netbox_url,netbox_api_token


class CONNECT_PREPARE():
        """
        Class for preparing data to connection to diff devices
        """

        def __init__(self, **kwargs):
                        """
                        Initialize the values
                        """

        def check_ssh(self, **kwargs):# func for check ssh or telnet - connections method
            ip_conn = kwargs['ip_conn']
            socket.setdefaulttimeout(1)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                result = sock.connect_ex((ip_conn, 22))
                if result == 0:
                    scheme = 'ssh'
                else:
                    """
                    result = sock.connect_ex((ip_conn, 23))
                    if result == 103:
                        scheme = 'telnet'
                    else:
                        scheme = 0
                    """
                    try:
                        telnetlib.Telnet(ip_conn, timeout=1)
                        scheme = 'telnet'
                    except ConnectionRefusedError:
                        scheme = 0
                    except Exception as e:
                        scheme = 0
            except Exception as err:
                print(err)
                scheme = 0
            sock.close()
            return scheme

        def template_conn(self, **kwargs):# method for make template for connection via netmiko
            print("<<< Start preparing.py >>>")
            ip_conn = kwargs['ip_conn']
            conn_scheme = kwargs['conn_scheme']
            type_device_for_conn = kwargs['type_device_for_conn']
            if conn_scheme == "1" and type_device_for_conn != "hp_procurve":
                host1 = {

                    "host": ip_conn,
                    "username": mylogin,
                    "password": mypass,
                    "device_type": type_device_for_conn,
                    "global_delay_factor": 0.5,
                }
            elif  conn_scheme == "1" and type_device_for_conn == "hp_procurve":
                host1 = {

                        "host": ip_conn,
                        "username": mylogin,
                        "password": mypass,
                        "device_type": type_device_for_conn,
                        "global_delay_factor": 3,
                        "secret": mypass,
                }
            else:
                host1 = {

                    "host": ip_conn,
                    "username": mylogin,
                    "password": mypass,
                    "device_type": type_device_for_conn,
                    "global_delay_factor": 3,
                }

            return host1





class CSV_PARSE():
    """
        Class for parsing data from csv file
    """

    def __init__(self, **kwargs):
        """
        Initialize the values
        """

    def find_out_csv_values(self,row):  #parse data from csv row and prepare it for connection
        print("<<< Start preparing.py >>>")
        #csv_content = TextIOWrapper(csv_file, encoding='cp1251')
        #csv_reader = csv.DictReader(csv_content)
        nb = pynetbox.api(url=netbox_url, token=netbox_api_token)
        nb.http_session.verify = False
        #my_list = []
        #for row in csv_reader:
        primary_ip = row['ip'].strip()
        ip_conn = primary_ip.split('/')[0]
        mask = primary_ip.split('/')[1]
        connecting = CONNECT_PREPARE()
        conn_scheme = connecting.check_ssh(**{'ip_conn': ip_conn})
        print("<<< Start core_exec.py >>>")
        if conn_scheme == 'telnet':
            conn_scheme = '2'
        elif conn_scheme == 'ssh':
            conn_scheme = '1'
        elif conn_scheme == 0:
            conn_scheme = False
        location = row['location']
        if location == '':
            location = None
        else:
            try:
                location = int(nb.dcim.locations.get(name=row['location']).id)
            except Exception as err:
                pass
        rack = row['rack']
        if rack == '':
            rack = None
        else:
            try:
                rack = int(nb.dcim.racks.get(name=row['rack']).id)
            except Exception as err:
                rack= None
        if row['stack'] == '0':
            stack = False
        elif row['stack'] == '1':
            stack = True
        else:
            stack = False
        map_resource_group = row['map_resource_group']
        if map_resource_group == '':
            map_resource_group = None
        else:
            try:
                map_resource_group = int(nb.tenancy.contact_roles.get(name=row['map_resource_group']).id)
            except Exception as err:
                pass
        try:
            platform_main = nb.dcim.platforms.get(name=row['platform'])
            platform_name = str(platform_main.name)
            platform_id = int(platform_main.id)
        except Exception as err:
            platform_name = None
            platform_id = None
        try:
            tenants = int(nb.tenancy.tenants.get(name=row['tenants']).id)
        except Exception as err:
            tenants = None

        try:
            site = int(nb.dcim.sites.get(name=row['site']).id)
        except Exception as err:
            site = None
        try:
            device_role = int(nb.dcim.device_roles.get(name=row['device_role']).id)
        except Exception as err:
            device_role = None
        try:
            tg_resource_group = int(nb.tenancy.contact_roles.get(name=row['tg_resource_group']).id)
        except Exception as err:
            tg_resource_group = None
        name_of_establishment = row['name_of_establishment']
        if name_of_establishment == '':
            name_of_establishment = None

        my_dict = {'purpose_value': 'add',
                   'data': {
                       'edit': {},
                       'add': {
                           'site': site,
                           'location': location,
                           'tenants': tenants,
                           'device_role': device_role,
                           'platform_name':platform_name,
                           'platform': platform_id,
                           'ip_conn': ip_conn,
                           'mask': mask,
                           'primary_ip': primary_ip,
                           'conn_scheme': conn_scheme,
                           'management_status': 1,  ### number 2 becuase online
                           'rack': rack,
                           'stack_enable': stack,
                           'tg_resource_group': tg_resource_group,
                           'map_resource_group': map_resource_group,
                           'name_of_establishment': name_of_establishment,
                       },
                       'diff': {}
                   }
                   }
        #my_list.append(my_dict)
        return my_dict

    def csv_parse_sites(self, row):
        name = row["name"]
        slug = self.create_slug(name)
        nb = pynetbox.api(url=netbox_url, token=netbox_api_token)
        nb.http_session.verify = False
        region = int(nb.dcim.regions.get(name=row['region']).id)
        my_dict = {'purpose_value': 'add_site',
                   'data': {
                       'edit': {},
                       'add': {
                           'name': name,
                           'slug': slug,
                           'region': region,
                           'physical_address': row['physical_address'],
                       },
                       'diff': {}
                   }
                   }
        return my_dict
    def create_slug(self, name):
        name_transliterated = unidecode(name)
        name_lower = name_transliterated.lower()
        name_cleaned = re.sub(r'[^a-z0-9]+', '-', name_lower)
        slug = name_cleaned.strip('-')
        return slug

    def check_exist_devices(self, exist_devices, new_devices):
        data = new_devices['data']['add']
        for dev in exist_devices:
            if data['device_name'] == dev:
                data.update({'exist_device':True})
                return new_devices
            elif data['device_name'] != dev:
                data.update({'exist_device': False})
                return new_devices





