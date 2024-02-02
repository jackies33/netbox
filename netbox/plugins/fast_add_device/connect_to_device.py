




from .preparing import CONNECT_PREPARE
import pynetbox
from .my_pass import netbox_url,netbox_api_token
from .device_types.huawei import HUAWEI_CONN
from .device_types.juniper import JUNIPER_CONN
from .device_types.cisco import CISCO_CONN
from .device_types.fortinet import FORTINET_CONN
from .device_types.ibm import IBM
from .device_types.aruba import ARUBA_OS
from .device_types.linux import LINUX
from .device_types.hpe import HPProCurve9xxx


class CONNECT_DEVICE():

        """
        Class for prepare data before connection to device
        """

        def __init__(self, ip_address,platform,
                     device_role,tenants,site,location,racks,stack_enable):

            self.ip_address = ip_address
            self.platform = platform
            self.device_role = device_role
            self.tenants = tenants
            self.site = site
            self.location = location
            self.racks = racks
            self.stack_enable = stack_enable


        def prepare_for_connection(self, *args):

                    print("<<< Start connect_to_device.py >>>")
                    ip_conn = self.ip_address.split('/')[0]
                    mask = self.ip_address.split('/')[1]
                    connecting = CONNECT_PREPARE(ip_conn)
                    conn_scheme = connecting.check_ssh()
                    print("<<< Start connect_to_device.py >>>")
                    if conn_scheme == 0:
                        print('No connection to device!!!')
                        return [False, "No connection to device! "]
                    if conn_scheme == 'telnet':
                        conn_scheme = '2'
                        print('Are you sure that use telnet!?')
                    if conn_scheme == 'ssh':
                        conn_scheme = '1'
                        print("ssh is ok")

                    nb = pynetbox.api(url=netbox_url, token=netbox_api_token)
                    nb.http_session.verify = False
                    platform_main = nb.dcim.platforms.get(id=self.platform)
                    platform = str(platform_main)
                    platform_id = int(platform_main.id)
                    result = []
                    if platform == "Huawei.VRP":
                         connection = HUAWEI_CONN(ip_conn,mask,platform_id,self.site,
                                                      self.location,self.device_role,
                                                      self.tenants,conn_scheme,self.racks,self.stack_enable)
                         result = connection.conn_Huawei()
                    elif platform == "Juniper.JUNOS":
                         connection = JUNIPER_CONN(ip_conn,mask,platform_id,self.site,
                                                      self.location,self.device_role,
                                                      self.tenants,conn_scheme,self.racks,self.stack_enable)
                         result = connection.conn_Juniper_rpc()
                    elif platform == "Cisco.IOS":
                         connection = CISCO_CONN(ip_conn,mask,platform_id,self.site,
                                                      self.location,self.device_role,
                                                      self.tenants,conn_scheme,self.racks,self.stack_enable)
                         result = connection.conn_Cisco_IOS()
                    elif platform == "Cisco.IOSXR":
                         connection = CISCO_CONN(ip_conn,mask,platform_id,self.site,
                                                      self.location,self.device_role,
                                                      self.tenants,conn_scheme,self.racks,self.stack_enable)
                         result = connection.conn_Cisco_IOS_XR()
                    elif platform == "IBM.NOS":
                         connection = IBM(ip_conn,mask,platform_id,self.site,
                                                      self.location,self.device_role,
                                                      self.tenants,conn_scheme,self.racks,self.stack_enable)
                         result = connection.conn_IBM_lenovo_sw()
                    elif platform == "Cisco.NXOS":
                         connection = CISCO_CONN(ip_conn,mask,platform_id,self.site,
                                                      self.location,self.device_role,
                                                      self.tenants,conn_scheme,self.racks,self.stack_enable)
                         result = connection.conn_Cisco_NXOS()
                    elif platform == "Aruba.ArubaOS":
                        connection = ARUBA_OS(ip_conn, mask, platform_id, self.site,
                                                     self.location,self.device_role,
                                                     self.tenants, conn_scheme,self.racks,self.stack_enable)
                        result = connection.conn_AWMP()
                    elif platform == "Fortinet.Fortigate":
                        connection = FORTINET_CONN(ip_conn, mask, platform_id, self.site,
                                                     self.location,self.device_role,
                                                     self.tenants, conn_scheme,self.racks,self.stack_enable)
                        result = connection.conn_FortiGate()
                    elif platform == "OS.Linux":
                        connection = LINUX(ip_conn, mask, platform_id, self.site,
                                                     self.location,self.device_role,
                                                     self.tenants, conn_scheme,self.racks,self.stack_enable)
                        result = connection.conn_OS_Linux()
                    elif platform == "HP.ProCurve9xxx":
                        connection = HPProCurve9xxx(ip_conn, mask, platform_id, self.site,
                                           self.location, self.device_role,
                                           self.tenants, conn_scheme, self.racks, self.stack_enable)
                        result = connection.conn_ProCurve9xxx()
                    return result



if __name__ == '__main__':
    print("__main__")
