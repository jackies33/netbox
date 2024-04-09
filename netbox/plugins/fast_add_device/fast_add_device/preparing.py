



import socket

from .my_pass import mylogin , mypass ,rescue_login, rescue_pass


class CONNECT_PREPARE():
        """
        Class for preparing data to connection to diff devices
        """

        def __init__(self, **kwargs):
                        """
                        Initialize the values
                        """


        def check_ssh(self, **kwargs):
            print("<<< Start preparing.py >>>")
            ip_conn = kwargs['ip_conn']
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((ip_conn, 22))
            scheme = 0
            if result == 0:
                scheme = 'ssh'
            else:
                result = sock.connect_ex((ip_conn, 23))
                if result == 0:
                    scheme = 'telnet'
                else:
                    scheme = 0
            sock.close()
            return scheme

        def template_conn(self, **kwargs):
            print("<<< Start preparing.py >>>")
            ip_conn = kwargs['ip_conn']
            conn_scheme = kwargs['conn_scheme']
            type_device_for_conn = kwargs['type_device_for_conn']
            if conn_scheme == "ssh" and type_device_for_conn != "hp_procurve":
                host1 = {

                    "host": ip_conn,
                    "username": mylogin,
                    "password": mypass,
                    "device_type": type_device_for_conn,
                    "global_delay_factor": 0.5,
                }
            elif  conn_scheme == "ssh" and type_device_for_conn == "hp_procurve":
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

