
from extras.plugins import PluginMenuItem

menu_items = (
    PluginMenuItem(
        link='plugins:fast_add_device:add_device_active',
        link_text='Active_equipment',
    ),
    PluginMenuItem(
        link='plugins:fast_add_device:add_device_csv',
        link_text='Devices_CSV_import',
    ),
    PluginMenuItem(
        link='plugins:fast_add_device:add_sites_csv',
        link_text='Sites_CSV_import',
    ),
    PluginMenuItem(
        link='plugins:fast_add_device:add_prefix_csv',
        link_text='Prefixes_CSV_import',
    ),
    PluginMenuItem(
        link='plugins:fast_add_device:add_device_offline',
        link_text='Offline_equipment',
    ),
    PluginMenuItem(
        link='plugins:fast_add_device:edit_device_active',
        link_text='Edit_active_equipment',
    ),

)
