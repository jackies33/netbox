


import pynetbox
from .my_pass import netbox_url,netbox_api_token
from .add_device import ADD_NB



class OFFLINE_DEV():

    """
    Class for connection to different device
    """

    def __init__(self, device_name = None ,site = None , location= None ,tenants = None ,device_role = None,
                 manufacturer = None ,platform = None ,device_type = None ,ip_address = None,
                 interface_name = None, conn_scheme = None, management = None, racks = None):

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


    def offline_preparing(self, *args):
                print("<<< Start offline_device.py >>>")
                nb = pynetbox.api(url=netbox_url, token=netbox_api_token)
                nb.http_session.verify = False
                adding = ADD_NB(self.device_name, self.site, self.location, self.tenants, self.device_role,
                                self.manufacturer,
                                self.platform, self.device_type, self.ip_address, self.interface_name, self.conn_scheme,
                                self.management, self.racks)
                result = adding.add_device()
                return result

