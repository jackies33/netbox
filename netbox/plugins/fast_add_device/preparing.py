

import socket
from .my_pass import mylogin , mypass ,rescue_login, rescue_pass


class CONNECT_PREPARE():
        """
        Class for preparing data to connection to diff devices
        """

        def __init__(self, ip_conn = None, type_device_for_conn = None, conn_scheme = None):

            self.ip_conn = ip_conn
            self.type_device_for_conn = type_device_for_conn
            self.conn_scheme = conn_scheme


        def check_ssh(self, *args):
            print("<<< Start preparing.py >>>")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((self.ip_conn, 22))
            scheme = 0
            if result == 0:
                scheme = 'ssh'
            else:
                result = sock.connect_ex((self.ip_conn, 23))
                if result == 0:
                    scheme = 'telnet'
                else:
                    scheme = 0
            sock.close()
            return scheme

        def template_conn(self, *args):
            print("<<< Start preparing.py >>>")
            if self.conn_scheme == "ssh" and self.type_device_for_conn != "hp_procurve":
                host1 = {

                    "host": self.ip_conn,
                    "username": mylogin,
                    "password": mypass,
                    "device_type": self.type_device_for_conn,
                    "global_delay_factor": 0.5,
                }
            elif  self.conn_scheme == "ssh" and self.type_device_for_conn == "hp_procurve":
                host1 = {

                        "host": self.ip_conn,
                        "username": mylogin,
                        "password": mypass,
                        "device_type": self.type_device_for_conn,
                        "global_delay_factor": 3,
                        "secret": mypass,
                }

            else:
                host1 = {

                    "host": self.ip_conn,
                    "username": mylogin,
                    "password": mypass,
                    "device_type": self.type_device_for_conn,
                    "global_delay_factor": 3,
                }

            return host1

