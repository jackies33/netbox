



import pynetbox
import atexit
import urllib3

from .my_pass import netbox_url,netbox_api_token


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



class NetboxAPIInstance:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.nb = None
        return cls._instance

    def get_instance(self):
        if not self.nb:
            self.url = netbox_url
            self.token = netbox_api_token
            self.nb = pynetbox.api(url=self.url, token=self.token)
            self.nb.http_session.verify = False
            atexit.register(self.logout)
        return self.nb

    def logout(self):
        if self.nb:
            try:
                self.nb.http_session.close()
            except Exception as e:
                print(f"Error during logout: {e}")


netbox_api_instance = NetboxAPIInstance()
