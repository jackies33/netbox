


from django.views import generic
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse,HttpResponseBadRequest
from http import HTTPStatus
#from django.core import serializers



from dcim.models.sites import Location
from dcim.models.racks import Rack
from .core_exec import CORE
from .forms import Device_Offline_PluginForm,Device_Active_PluginForm,Device_Change_Active_PluginForm





class Add_Device_Active_View(generic.TemplateView):
    print("<<< Start views.py >>>")
    template_success = 'fast_add_device/active_success.html'
    template_main_active = 'fast_add_device/main_active.html'
    template_bad_result = 'fast_add_device/bad_result_active.html'
    form_class = Device_Active_PluginForm

    def get_context_data(self, **kwargs):
        try:
            con = super().get_context_data(**kwargs)
            con['form'] = self.form_class
            print(con['form'])
            return con
        except Exception as err:
            return JsonResponse({'response': 'False', 'connecting':err}, status=500)

    def get(self, request):
        try:
            return render(request, self.template_main_active, context={'form': self.form_class})
        except Exception as err:
            return JsonResponse({'response': 'False', 'connecting':err}, status=500)

    def post(self, request):
        try:
            form = self.form_class(request.POST)
            if form.is_valid():
                ip_address = form.cleaned_data['ip_address']
                platform = form.cleaned_data['platform'].id
                device_role = form.cleaned_data['device_role'].id
                tenants = form.cleaned_data['tenants'].id
                site = form.cleaned_data['site'].id
                tg_resource_group = form.cleaned_data['tg_resource_group'].id
                stack_enable = form.cleaned_data['stack']
                if stack_enable == 'False':
                    stack_enable = False
                elif stack_enable == 'True':
                    stack_enable = True
                try:
                    location = form.cleaned_data['location'].id
                    location = int(location)
                except Exception as err:
                    location = None
                try:
                    racks = form.cleaned_data['racks'].id
                    racks = int(racks)
                except Exception as err:
                    racks = None
                try:
                    map_resource_group = form.cleaned_data['map_resource_group'].id
                    map_resource_group = int(map_resource_group)
                except Exception as err:
                    map_resource_group = None

                trans_dict = {'purpose_value': 'add',
                                                    'data': {
                                                        'edit': {},
                                                        'add': {
                                                                'primary_ip': str(ip_address),
                                                                'site':int(site),
                                                                'location':location,
                                                                'tenants':int(tenants),
                                                                'device_role': int(device_role),
                                                                'platform': int(platform),
                                                                'management_status':1,### number 2 becuase online
                                                                'rack': racks,
                                                                'stack_enable': stack_enable,
                                                                'tg_resource_group': tg_resource_group,
                                                                'map_resource_group': map_resource_group
                                                        },
                                                        'diff': {}
                                                    }
                }
                call = CORE()
                connecting = call.add_edit_plugin(**trans_dict)
                if connecting[0] == True:
                    return render(request, self.template_success,
                                  context={'response': "True", 'connecting': connecting[1]}, status=HTTPStatus.CREATED)

                elif connecting[0] == False:
                    return render(request, self.template_bad_result,
                                  context={'response': "False", 'connecting': connecting[1]},
                                  status=HTTPStatus.INTERNAL_SERVER_ERROR)
                else:
                    return HttpResponse('Something gone wrong', status=HTTPStatus.BAD_REQUEST)
            else:
                return HttpResponse('Something gone wrong', status=HTTPStatus.BAD_REQUEST)
        except Exception as err:
            return render(request, self.template_bad_result,
                          context={'response': "False", 'connecting': err},
                          status=HTTPStatus.INTERNAL_SERVER_ERROR)



class Add_Device_Offline_View(generic.TemplateView):
    print("<<< Start views.py >>>")
    template_success = 'fast_add_device/offline_success.html'
    template_main_offline = 'fast_add_device/main_offline.html'
    template_bad_result = 'fast_add_device/bad_result_offline.html'
    form_class = Device_Offline_PluginForm

    def get_context_data(self, **kwargs):
        try:
            con = super().get_context_data(**kwargs)
            con['form'] = self.form_class
            print(con['form'])
            return con
        except Exception as err:
            return JsonResponse({'response': 'False', 'connecting': err}, status=500)

    def get(self, request):
        try:
            return render(request, self.template_main_offline, context={'form': self.form_class})
        except Exception as err:
            return JsonResponse({'response': 'False', 'connecting': err}, status=500)

    def post(self, request):
        try:

            form = Device_Offline_PluginForm(request.POST)
            if form.is_valid():
                ip_address = form.cleaned_data['ip_address']
                device_name = form.cleaned_data['device_name']
                platform = form.cleaned_data['platform'].id
                manufacturer = form.cleaned_data['manufacturer']
                device_type = form.cleaned_data['device_type'].id
                device_role = form.cleaned_data['device_role'].id
                tenants = form.cleaned_data['tenants'].id
                site = form.cleaned_data['site'].id
                tg_resource_group = form.cleaned_data['tg_resource_group'].id
                conn_scheme = form.cleaned_data['conn_scheme']
                interface_name = form.cleaned_data['interface_name']
                serial_number = form.cleaned_data['serial_number']

                try:
                    location = form.cleaned_data['location'].id
                    location = int(location)
                except Exception as err:
                    print(err)
                    location = None

                try:
                    racks = form.cleaned_data['racks'].id
                    racks = int(racks)
                except Exception as err:
                    print(err)
                    racks = None
                try:
                    map_resource_group = form.cleaned_data['map_resource_group'].id
                    map_resource_group = int(map_resource_group)
                except Exception as err:
                    map_resource_group = None
                list_serial_devices = []
                list_serial_devices.append({'member_id': 0, 'sn_number': str(serial_number), 'master': False})
                trans_dict = {'purpose_value': 'add',
                                                    'data': {
                                                            'edit': {},
                                                            'add': {
                                                                'site':int(site),
                                                                'location':location,
                                                                'tenants':int(tenants),
                                                                'device_role': int(device_role),
                                                                'platform': int(platform),
                                                                'primary_ip': str(ip_address),
                                                                'device_name':str(device_name),
                                                                'manufacturer':str(manufacturer),
                                                                'device_type':int(device_type),
                                                                'interface_name':str(interface_name),
                                                                'list_serial_device':list_serial_devices,
                                                                'conn_scheme': str(conn_scheme),
                                                                'management_status':2,### number 2 becuase offline
                                                                'rack': racks,
                                                                'stack_enable': False,
                                                                'tg_resource_group': int(tg_resource_group),
                                                                'map_resource_group': map_resource_group
                                                            },
                                                            'diff': {}
                                                    }
                }

                call = CORE()
                connecting = CORE.add_edit_plugin(**trans_dict)

                if connecting[0] == True :
                    return render(request, self.template_success, context={'response': "True",'connecting': connecting[1]},status=HTTPStatus.CREATED)

                elif connecting[0] == False:
                    return render(request, self.template_bad_result,
                                  context={'response': "False", 'connecting': connecting[1]}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
                else:
                    return HttpResponse('Something gone wrong', status=HTTPStatus.BAD_REQUEST)
            else:
                return HttpResponse('Something gone wrong', status=HTTPStatus.BAD_REQUEST)
        except Exception as err:
            return render(request, self.template_bad_result,
                          context={'response': "False", 'connecting': err},
                          status=HTTPStatus.INTERNAL_SERVER_ERROR)


class Change_Device_Active_View(generic.TemplateView):
    print("<<< Start views.py >>>")
    template_success = 'fast_add_device/active_change_success.html'
    template_main = 'fast_add_device/main_change_active.html'
    template_bad_result = 'fast_add_device/bad_result_change_active.html'
    form_class = Device_Change_Active_PluginForm

    def get_context_data(self, **kwargs):
        try:
            con = super().get_context_data(**kwargs)
            con['form'] = self.form_class
            print(con['form'])
            return con
        except Exception as err:
            return JsonResponse({'response': 'False', 'connecting': err}, status=500)

    def get(self, request):
        try:
            return render(request, self.template_main, context={'form': self.form_class})
        except Exception as err:
            return JsonResponse({'response': 'False', 'connecting': err}, status=500)
    def post(self, request):
        try:

            form = self.form_class(request.POST)
            if form.is_valid():
                device = form.cleaned_data['devices'].id
                print(device)
                trans_dict = {'purpose_value': 'edit',
                           'data':{
                               'edit':{"device_id":int(device)},
                               'add':{},
                               'diff':{}
                    }
                }
                call = CORE()
                print(trans_dict)
                connecting = call.add_edit_plugin(**trans_dict)
                if connecting[0] == True :
                    return render(request, self.template_success, context={'response': "True",'connecting': connecting[1]},status=HTTPStatus.CREATED)
                elif connecting[0] == False:
                    return render(request, self.template_bad_result,
                                  context={'response': "False", 'connecting': connecting[1]}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
                else:
                    return HttpResponse('Something gone wrong', status=HTTPStatus.BAD_REQUEST)
            else:
                return HttpResponse('Something gone wrong', status=HTTPStatus.BAD_REQUEST)

        except Exception as err:
            return render(request, self.template_bad_result,
                          context={'response': "False", 'connecting': err},
                          status=HTTPStatus.INTERNAL_SERVER_ERROR)



"""

def get_location(request):
    print("test get_location")
    site_id = request.GET.get('site_id')
    location = Location.objects.filter(site_id=site_id)
    print(location)
    location = {'location':list(location.values('name', 'id'))}
    print(location)
    #data_json = serializers.serealize('json',location)
    #print(data_json)
    return JsonResponse(location, safe=False)
   # return HttpResponse({'locations': list(location)}, content_type="application/json")
    #return JsonResponse({'locations': list(location)})
"""


def get_location(request):    ##### method for get data location via AJAX request from form in web page
    try:
        site_id = request.GET.get('site_id')
        if site_id:
            location = Location.objects.filter(site_id=site_id).values('id', 'name')
            return JsonResponse({'location': list(location)})
        else:
            return JsonResponse({'error': 'Site ID is missing'}, status=400)

    except Exception as err:
        return JsonResponse({'response': 'False', 'connecting':err}, status=500)

def get_racks(request):  ##### method for get data racks via AJAX request from form in web page
    try:
        location_id = request.GET.get('location_id')
        if location_id:
            racks = Rack.objects.filter(location_id=location_id).values('id', 'name')
            return JsonResponse({'racks': list(racks)})
        else:
            return JsonResponse({'error': 'Site ID is missing'}, status=400)

    except Exception as err:
        return JsonResponse({'response': 'False', 'connecting':err}, status=500)


