



import pynetbox
import csv
from pynetbox import RequestError

from .my_pass import netbox_url,netbox_api_token



def check_exist_sites(file_path):
    ips_from_file = []
    with open(file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if 'ip' in row:
                ips_from_file.append(row['ip'].strip())
    nb = pynetbox.api(url=netbox_url, token=netbox_api_token)
    nb.http_session.verify = False
    for device in nb.dcim.devices.all():
        try:
            device_ip = str(device.primary_ip.address)
        except AttributeError as err:
            continue
        for ips in ips_from_file:
            if ips == device_ip:
                ips_from_file.remove(ips)
    print(ips_from_file)



file_path = "/Users/jackson33/Desktop/result_kag.csv"
check_exist_sites(file_path)

