


import re
from airwaveapiclient import AirWaveAPIClient


from ..classifier import classifier_device_type
from ..my_pass import mylogin , mypass






class ARUBA_OS():
            """
            Class for connection to different device
            """

            def __init__(self, **kwargs):
                """
                Initialize the values
                """


            def conn_AWMP(self ,**kwargs):
                print("<<< Start aruba.py >>>")
                ###consider data for collect and return
                if kwargs['purpose_value'] == "add":
                    data = kwargs['data']['add']  ####add data for consider adding dict
                    data_for_add = kwargs['data']['add']
                elif kwargs['purpose_value'] == "edit":
                    data = kwargs['data']['edit']  #### edit data for consider data from extract_nb.py
                    data_for_add = kwargs['data']['add']
                else:
                    return [False, None]
                ip_conn = data['ip_conn']
                mask = data['mask']
                stack_enable = data['stack_enable']
                airwave = AirWaveAPIClient(username=mylogin, password=mypass, url=f'https://{ip_conn}')
                try:
                    airwave.login()
                    output = airwave.amp_stats().text
                    manufacturer = "Hewlett Packard Enterprise"
                    device_type = classifier_device_type(
                        manufacturer,re.findall("<name>.*</name>", output)[0].split('<name>')[1].split('</name>')
                    )
                    print("<<< Start aruba.py >>>")
                    primary_ip = (f'{ip_conn}/{mask}')
                    interface_name = "VirtInt"
                    device_name = f'AWMP_{ip_conn}'
                    list_serial_device = []
                    list_serial_device.append({'member_id': 0, 'sn_number': "NNNNNNN000000", 'master': False})
                    data_for_add.update(
                                         {
                                             'site':data['site'],
                                             'location':data['location'],
                                             'tenants':data['tenants'],
                                             'device_role': data['device_role'],
                                             'platform': data['platform'],
                                             'primary_ip': data['primary_ip'],
                                             'device_name':device_name,
                                             'manufacturer':manufacturer,
                                             'device_type':device_type[0],
                                             'interface_name':interface_name,
                                             'list_serial_device':list_serial_device,
                                             'conn_scheme': data['conn_scheme'],
                                             'management_status':data['management_status'],
                                             'rack': data['rack'],
                                             'stack_enable': data['stack_enable'],
                                             'tg_resource_group': data['tg_resource_group'],
                                             'map_resource_group': data['map_resource_group'],
                                             'name_of_establishment': data['name_of_establishment']
                                         }
                                )

                    return kwargs
                except Exception as err:
                    print(f"Error {err}")
                    return [False, err]