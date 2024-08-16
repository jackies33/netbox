


import socket
import pynetbox
import telnetlib
from unidecode import unidecode
import re
import requests
import json
import yaml


from .my_pass import mylogin , mypass ,rescue_login, rescue_pass,netbox_url,netbox_api_token
from .keep_api import netbox_api_instance
from .nb_exec.add_device_from_csv import ADD_NB_CSV


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
        site = None
        #try:
        #    preparing_name = re.sub(r'[.,\s]', '', row["site"].lower().strip())
        #    #print(f"1RESULT\n\n\n{preparing_name}\n\n\n1RESULT")
        #    for site_prepare in nb.dcim.sites.all():
        #        site_name = str(re.sub(r'[.,\s]', '', site_prepare.name.lower().strip()))
        #       site_physical_address = str(re.sub(r'[.,\s]', '', site_prepare.physical_address.lower().strip()))
        #        #print(f"2RESULT\n\n\n{site_name}\n\n\n2RESULT")
        #       if preparing_name in site_name:
        #            site = int(site_prepare.id)
        #        elif preparing_name in site_physical_address:
        #            site = int(site_prepare.id)
        #except Exception as err:
        #    try:
        #        site = int(nb.dcim.sites.get(name=row['site']).id)
        #    except Exception as err:
        #        site = None
        site = int(nb.dcim.sites.get(id=int(row['site'])).id)
        if site == None:
            return [False,f"site is None for device - {primary_ip}"]
        #site = int(nb.dcim.sites.get(name=row['site']).id)
        """
        if site == None:
            site_name = row["site"]
            slug_site = self.create_slug(site_name)
            region = int(nb.dcim.regions.get(name=row['region']).id)
            my_dict = {'purpose_value': 'add_site',
                       'data': {
                           'edit': {},
                           'add': {
                               'name': site_name,
                               'slug': slug_site,
                               'region': region,
                               'physical_address': site_name,
                           },
                           'diff': {}
                       }
                       }
            call = ADD_NB_CSV()
            call.add_sites_csv(**my_dict)
            site = int(nb.dcim.sites.get(name=row['site']).id)
        #print(f"RESULT\n\n\n{site}\n\n\nRESULT")
        """
        location_row = row['location']
        if location_row == '' or location_row == "None":
            location = None
        else:
            try:
                location = nb.dcim.locations.get(name=location_row, site_id=site)
                location = int(location.id)
            except Exception as err:
                slug = self.create_slug(location_row)
                new_location = nb.dcim.locations.create(
                    name=location_row,
                    site=site,
                    slug=slug
                )
                location = int(new_location.id)
        rack_row = row['rack']
        if rack_row == '' or rack_row == "None":
            rack = None
        else:
            try:
                rack = nb.dcim.racks.get(name=rack_row, location_id=location)
                rack = int(rack.id)
            except Exception as err:
                slug = self.create_slug(rack_row)
                new_rack = nb.dcim.racks.create(
                    name=rack_row,
                    location=location,
                    slug=slug
                )
                rack = int(new_rack.id)
        try:
            device_role = int(nb.dcim.device_roles.get(name=row['device_role']).id)
        except Exception as err:
            device_role = None
        #print(f"1RESULT\n\n\n{row['tg_resource_group']}\n\n\n1RESULT")
        try:
            tg_resource_group = int(nb.tenancy.contact_roles.get(name=row['tg_resource_group']).id)
            #print(f"2RESULT\n\n\n{tg_resource_group}\n\n\n2RESULT")
        except Exception as err:
            tg_resource_group = None
        #print(f"3RESULT\n\n\n{tg_resource_group}\n\n\n3RESULT")
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
        return [True,my_dict]

    def csv_parse_sites(self, row):
        name = row["name"]
        check_name = self.check_exist_sites(name)
        if check_name[0] == False:
            slug = self.create_slug(name)
            nb = pynetbox.api(url=netbox_url, token=netbox_api_token)
            nb.http_session.verify = False
            try:
                region = int(nb.dcim.regions.get(name=row['region']).id)
            except AttributeError as err:
                return [False,f"_____there isn't exist the 'Region' for site name - '''{name}''' please create one_____"]
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
            return ["not exist", my_dict]
        elif check_name[0] == True:
            return ["exist", f"_______this site - '''{name}''' is alreasy exist, check it please manually_______"]

    def csv_parse_prefixes(self, row):
        name = row["Prefix_name"]
        check_name = self.check_exist_sites(name)
        if check_name[0] == False:
            slug = self.create_slug(name)
            nb = pynetbox.api(url=netbox_url, token=netbox_api_token)
            nb.http_session.verify = False
            try:
                region = int(nb.dcim.regions.get(name=row['region']).id)
            except AttributeError as err:
                return [False,
                        f"_____there isn't exist the 'Region' for site name - '''{name}''' please create one_____"]
            my_dict = {'purpose_value': 'add_prefixes',
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
            return ["not exist", my_dict]
        elif check_name[0] == True:
            return ["exist", f"_______this site - '''{name}''' is alreasy exist, check it please manually_______"]



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


    def check_exist_sites(self,name):
        preparing_name = re.sub(r'[.,\s]', '', name.lower().strip())
        nb = pynetbox.api(url=netbox_url, token=netbox_api_token)
        nb.http_session.verify = False
        for site in nb.dcim.sites.all():
            site_name = str(re.sub(r'[.,\s]', '', site.name.lower().strip()))
            site_physical_address = str(re.sub(r'[.,\s]', '', site.physical_address.lower().strip()))
            if preparing_name in site_name:
                return [True,name]
            elif preparing_name in site_physical_address:
                return [True,name]
        return [False,name]

    def check_exist_prefixes(self, kwargs):
        nb = netbox_api_instance.get_instance()
        tenant_group = nb.tenancy.tenant_groups.get(name=kwargs['tenant_group_name'])
        if tenant_group == None:
            tenant_group_data = {
                "name": kwargs['tenant_group_name'],
                'slug': self.create_slug(kwargs['tenant_group_name']),
            }
            nb.tenancy.tenant_groups.create(tenant_group_data)
            tenant_group = nb.tenancy.tenant_groups.get(name=kwargs['tenant_group_name'])
        tenant = nb.tenancy.tenants.get(name=kwargs['tenant_name'])
        if tenant == None:
            tenant_data = {
                "name": kwargs['tenant_name'],
                'slug': self.create_slug(kwargs['tenant_name']),
                "group": tenant_group.id,
            }
            nb.tenancy.tenants.create(tenant_data)
            tenant = nb.tenancy.tenants.get(name=kwargs['tenant_name'])
        prefix = nb.ipam.prefixes.get(prefix=kwargs['prefix_name'])
        if prefix:  # if prefix already exists, in this block we are trying to check all fields and correct them if it necessarily
            try:
                vrf = prefix.vrf
                if vrf == None:
                    vrf = nb.ipam.vrfs.get(name=kwargs['vrf_name'])
                    if vrf != None:
                        if vrf.rd == None:
                            vrf.update({'rd': kwargs['vrf_rd']})
                        if vrf.import_targets == []:
                            if nb.ipam.route_targets.get(name=kwargs['vrf_rd']) == None:
                                nb.ipam.route_targets.create({"name": kwargs['vrf_rd'],
                                                              "tenant": tenant.id,
                                                              "tenant_group": tenant_group.id})
                            rt = nb.ipam.route_targets.get(name=kwargs['vrf_rd'])
                            vrf.update({'import_targets': [rt.id]})
                        prefix.update({'vrf': vrf})
                    elif vrf == None:
                        vrf = nb.ipam.vrfs.get(rd=kwargs['vrf_rd'])
                    if vrf == None:
                        if nb.ipam.route_targets.get(name=kwargs['vrf_rd']) == None:
                            nb.ipam.route_targets.create({"name": kwargs['vrf_rd'],
                                                          "tenant": tenant.id,
                                                          "tenant_group": tenant_group.id})
                        rt = nb.ipam.route_targets.get(name=kwargs['vrf_rd'])
                        nb.ipam.vrfs.create({
                            "name": kwargs['vrf_name'],
                            "rd": kwargs['vrf_rd'],
                            "tenant": tenant.id,
                            "tenant_group": tenant_group.id,
                            'import_targets': [rt.id],
                        })
                        vrf = nb.ipam.vrfs.get(name=kwargs['vrf_name'])
                    prefix.update({'vrf': vrf.id})
                """
                if prefix.role == None:
                    role = nb.ipam.roles.get(name=kwargs['role_name'])
                    if role == None:
                        print(kwargs['role_name'])
                        if kwargs['role_name'] != '':
                            role_data = {
                                'name': kwargs['role_name'],
                                'slug': self.create_slug(kwargs['role_name']),
                                'weight': kwargs['role_weight']
                            }
                            nb.ipam.roles.create(role_data)
                            role = nb.ipam.roles.get(name=kwargs['role_name'])
                            if role == None:
                                role_id = None
                            else:
                                role_id = role.id
                                prefix.update({'role': role_id})
                        else:
                            role_id = None
                    else:
                        role_id = role.id
                        prefix.update({'role': role_id})
                else:
                    role_id = prefix.role.id
                    prefix.update({'role': role_id})
                """
                if prefix.vlan == None:
                    vlan = nb.ipam.vlans.get(name=kwargs['vlan_name'])
                    #role = nb.ipam.roles.get(name=kwargs['role_name'])
                    if vlan == None:
                        vlan_group = nb.ipam.vlan_groups.get(name=kwargs['vlan_group'])
                        """
                        if role_id != None:
                            vlan_data = {
                                "name": kwargs['vlan_name'],
                                "vid": kwargs['vlan_id'],
                                "group": vlan_group.id,
                                "tenant": tenant.id,
                                "status": "active",
                                'role': role_id
                            }
                            nb.ipam.vlans.create(vlan_data)
                            vlan = nb.ipam.vlans.get(name=kwargs['vlan_name'])
                        elif role_id == None:
                        """
                        vlan_data = {
                            "name": kwargs['vlan_name'],
                            "vid": kwargs['vlan_id'],
                            "group": vlan_group.id,
                            "tenant": tenant.id,
                            "status": "active"
                        }
                        nb.ipam.vlans.create(vlan_data)
                        vlan = nb.ipam.vlans.get(name=kwargs['vlan_name'])
                    prefix.update({'vlan': vlan.id})
                if prefix.site == None:
                    site = nb.dcim.sites.get(name=kwargs['site_name'])
                    if site == None:
                        site_data = {
                            "name": kwargs['site_name'],
                            'slug': self.create_slug(kwargs['site_name']),
                        }

                        nb.dcim.sites.create(site_data)
                    prefix.update({'site': site.id})
                if prefix.tenant == None:
                    prefix.update({'tenant': tenant.id})
                return ["exist", kwargs['prefix_name']]
            except AttributeError as err:
                print(err)
                return [False, kwargs['prefix_name'], err]
            except ValueError as err:
                print(err)
                return [False, kwargs['prefix_name'], err]
            except Exception as err:
                print(err)
                return [False, kwargs['prefix_name'], err]
        else:  # if prefix isn't exist , we would check all dependecies refers to prefix and update or create it
            try:
                vrf = nb.ipam.vrfs.get(name=kwargs['vrf_name'])
                if vrf != None:
                    if vrf.rd == None:
                        vrf.update({'rd': kwargs['vrf_rd']})
                    if vrf.import_targets == []:
                        if nb.ipam.route_targets.get(name=kwargs['vrf_rd']) == None:
                            nb.ipam.route_targets.create({"name": kwargs['vrf_rd'],
                                                          "tenant": tenant.id,
                                                          "tenant_group": tenant_group.id})
                        rt = nb.ipam.route_targets.get(name=kwargs['vrf_rd'])
                        vrf.update({'import_targets': [rt.id]})
                        vrf = nb.ipam.vrfs.get(name=kwargs['vrf_name'])
                elif vrf == None:
                    vrf = nb.ipam.vrfs.get(rd=kwargs['vrf_rd'])
                if vrf == None:
                    if nb.ipam.route_targets.get(name=kwargs['vrf_rd']) == None:
                        nb.ipam.route_targets.create({"name": kwargs['vrf_rd'],
                                                      "tenant": tenant.id,
                                                      "tenant_group": tenant_group.id})
                    rt = nb.ipam.route_targets.get(name=kwargs['vrf_rd'])
                    nb.ipam.vrfs.create({
                        "name": kwargs['vrf_name'],
                        "rd": kwargs['vrf_rd'],
                        "tenant": tenant.id,
                        "tenant_group": tenant_group.id,
                        'import_targets': [rt.id],
                    })
                    vrf = nb.ipam.vrfs.get(name=kwargs['vrf_name'])
                #role = nb.ipam.roles.get(name=kwargs['role_name'])
                """
                if role == None:
                    print(kwargs['role_name'])
                    if kwargs['role_name'] != '':
                        role_data = {
                            'name': kwargs['role_name'],
                            'slug': self.create_slug(kwargs['role_name']),
                            'weight': kwargs['role_weight']
                        }
                        nb.ipam.roles.create(role_data)
                        role = nb.ipam.roles.get(name=kwargs['role_name'])
                        if role == None:
                            role_id = None
                        else:
                            role_id = role.id
                    else:
                        role_id = None
                else:
                    role_id = prefix.role.id
                """
                vlan = nb.ipam.vlans.get(name=kwargs['vlan_name'])
                if vlan == None:
                    vlan_group = nb.ipam.vlan_groups.get(name=kwargs['vlan_group'])
                    """
                    if role_id != None:
                        vlan_data = {
                            "name": kwargs['vlan_name'],
                            "vid": kwargs['vlan_id'],
                            "group": vlan_group.id,
                            "tenant": tenant.id,
                            "status": "active",
                            'role': role_id
                        }
                        nb.ipam.vlans.create(vlan_data)
                        vlan = nb.ipam.vlans.get(name=kwargs['vlan_name'])
                    elif role_id == None:
                    """
                    vlan_data = {
                        "name": kwargs['vlan_name'],
                        "vid": kwargs['vlan_id'],
                        "group": vlan_group.id,
                        "tenant": tenant.id,
                        "status": "active"
                    }
                    nb.ipam.vlans.create(vlan_data)
                    vlan = nb.ipam.vlans.get(name=kwargs['vlan_name'])
                site = nb.dcim.sites.get(name=kwargs['site_name'])
                if site == None:
                    site_data = {
                        "name": kwargs['site_name'],
                        'slug': self.create_slug(kwargs['site_name']),
                    }
                    nb.dcim.sites.create(site_data)
                    site = nb.dcim.sites.get(name=kwargs['site_name'])
                """
                if role_id != None:
                    my_dict = {'purpose_value': 'add_prefixes',
                               'data': {
                                   'edit': {},
                                   'add': {
                                       "prefix": kwargs['prefix_name'],
                                       "vrf": vrf.id,
                                       "tenant": tenant.id,
                                       "site": site.id,
                                       "vlan": vlan.id,
                                       "role": role.id,
                                   },
                                   'diff': {}
                               }
                               }
                    return ["not exist", my_dict]
                elif role_id == None:
                """
                my_dict = {'purpose_value': 'add_prefixes',
                           'data': {
                               'edit': {},
                               'add': {
                                   "prefix": kwargs['prefix_name'],
                                   "vrf": vrf.id,
                                   "tenant": tenant.id,
                                   "site": site.id,
                                   "vlan": vlan.id,
                               },
                               'diff': {}
                           }
                           }
                return ["not exist", my_dict]
            except AttributeError as err:
                print(err)
                return [False, kwargs['prefix_name'], err]
            except ValueError as err:
                print(err)
                return [False, kwargs['prefix_name'], err]
            except Exception as err:
                print(err)
                return [False, kwargs['prefix_name'], err]













