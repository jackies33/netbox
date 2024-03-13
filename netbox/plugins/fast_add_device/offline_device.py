


import pynetbox
from .my_pass import netbox_url,netbox_api_token
from .add_device import ADD_NB



class OFFLINE_DEV():

    """
    Class for connection to different device
    """

    def __init__(self, device_name = None ,site = None , location= None ,tenants = None ,device_role = None,
                 manufacturer = None ,platform = None ,device_type = None ,ip_address = None,
                 interface_name = None, conn_scheme = None, management = None, racks = None, serial_number = None):

        self.device_name = device_name
        self.site = site
        self.location = location
        self.tenants = tenants
        self.device_role = device_role
        self.manufacturer = manufacturer
        self.platform = platform
        self.device_type = device_type
        self.ip_address = ip_address
        self.interface_name = interface_name
        self.conn_scheme = conn_scheme
        self.management = management
        self.racks = racks
        self.serial_number = serial_number


    def offline_preparing(self, *args):
                print("<<< Start offline_device.py >>>")
                nb = pynetbox.api(url=netbox_url, token=netbox_api_token)
                nb.http_session.verify = False
                list_serial_devices = []
                #if self.conn_scheme == "1":
                #    self.conn_scheme = "ssh"
                #elif self.conn_scheme == "2":
                #    self.conn_scheme = "telnet"
                list_serial_devices.append({'member_id': 0, 'sn_number': self.serial_number, 'master': False})
                stack_enable = False
                adding = ADD_NB(self.device_name, self.site, self.location, self.tenants, self.device_role,
                                self.manufacturer,
                                self.platform, self.device_type, self.ip_address, self.interface_name, self.conn_scheme,
                                self.management, self.racks, list_serial_devices,stack_enable)
                result = adding.add_device()
                return result

