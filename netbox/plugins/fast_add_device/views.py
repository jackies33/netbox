


from django.shortcuts import render
from django.views import generic
from .forms import Device_Offline_PluginForm,Device_Active_PluginForm
from django.http import HttpResponse
from http import HTTPStatus
from .connect_to_device import CONNECT_DEVICE
from .offline_device import OFFLINE_DEV


class Add_Device_Active_View(generic.TemplateView):
    print("<<< Start views.py >>>")
    template_success = 'fast_add_device/active_success.html'
    template_main_active = 'fast_add_device/main_active.html'
    template_bad_result = 'fast_add_device/bad_result_active.html'
    form_class = Device_Active_PluginForm

    def get_context_data(self, **kwargs):
        con = super().get_context_data(**kwargs)
        con['form'] = self.form_class
        return con

    def get(self, request):
        form = Device_Active_PluginForm
        return render(request, self.template_main_active, context={'form': form})

    def post(self, request):
        form = Device_Active_PluginForm(request.POST)
        if form.is_valid():
            ip_address = form.cleaned_data['ip_address']
            platform = form.cleaned_data['platform'].id
            device_role = form.cleaned_data['device_role'].id
            tenants = form.cleaned_data['tenants'].id
            site = form.cleaned_data['site'].id
            stack_enable = form.cleaned_data['stack']

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

            device_connect = CONNECT_DEVICE(str(ip_address),int(platform),
                                            int(device_role),int(tenants),int(site), location, racks, stack_enable)
            connecting = device_connect.prepare_for_connection()
            #location_id = form.cleaned_data['location'].id
            #print(data)
            #print(ip_address,platform,device_type,device_role,tenants,location,managment)
            #object_model = DevicesPluginModel.objects.create(**form.cleaned_data)
            #object_model.save()
            if connecting[0] == True :
                #new_success = SuccessView.as_view()
                #return new_success(request, arg1=connecting[1])

                return render(request, self.template_success, context={'response': "True",'connecting': connecting[1]},status=HTTPStatus.CREATED)

            elif connecting[0] == False:
                return render(request, self.template_bad_result,
                              context={'response': "False", 'connecting': connecting[1]}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            else:
                return HttpResponse('Something gone wrong', status=HTTPStatus.BAD_REQUEST)
                #return render(request, self.template_name_main, context={'form': self.form_class, 'response': "True"}, status=HTTPStatus.CREATED)

        else:
            return HttpResponse('Something gone wrong', status=HTTPStatus.BAD_REQUEST)



class Add_Device_Offline_View(generic.TemplateView):
    print("<<< Start views.py >>>")
    template_success = 'fast_add_device/offline_success.html'
    template_main_offline = 'fast_add_device/main_offline.html'
    template_bad_result = 'fast_add_device/bad_result_offline.html'
    form_class = Device_Offline_PluginForm

    def get_context_data(self, **kwargs):
        con = super().get_context_data(**kwargs)
        con['form'] = self.form_class
        return con

    def get(self, request):
        form = Device_Offline_PluginForm
        return render(request, self.template_main_offline, context={'form': form})

    def post(self, request):
        form = Device_Offline_PluginForm(request.POST)
        if form.is_valid():
            ip_address = form.cleaned_data['ip_address']
            device_name = form.cleaned_data['device_name']
            platform = form.cleaned_data['platform'].id
            manufacturer = form.cleaned_data['manufacturer']
            device_type = form.cleaned_data['device_type'].id
            device_role = form.cleaned_data['device_role'].id
            tenants = form.cleaned_data['tenants'].id
            site = form.cleaned.data['site'].id
            conn_scheme = form.cleaned_data['conn_scheme']
            interface_name = form.cleaned_data['interface_name']
            management = 2

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

            adding = OFFLINE_DEV(str(device_name), int(site), location, int(tenants), int(device_role), str(manufacturer),
                            int(platform), int(device_type), str(ip_address), str(interface_name), conn_scheme, int(management),
                            racks)
            connecting = adding.offline_preparing()
            #location_id = form.cleaned_data['location'].id
            #print(data)
            #print(ip_address,platform,device_type,device_role,tenants,location,managment)
            #object_model = DevicesPluginModel.objects.create(**form.cleaned_data)
            #object_model.save()
            if connecting[0] == True :
                #new_success = SuccessView.as_view()
                #return new_success(request, arg1=connecting[1])

                return render(request, self.template_success, context={'response': "True",'connecting': connecting[1]},status=HTTPStatus.CREATED)

            elif connecting[0] == False:
                return render(request, self.template_bad_result,
                              context={'response': "False", 'connecting': connecting[1]}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            else:
                return HttpResponse('Something gone wrong', status=HTTPStatus.BAD_REQUEST)
                #return render(request, self.template_name_main, context={'form': self.form_class, 'response': "True"}, status=HTTPStatus.CREATED)

        else:
            return HttpResponse('Something gone wrong', status=HTTPStatus.BAD_REQUEST)


