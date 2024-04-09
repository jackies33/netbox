

from extras.plugins import PluginConfig


class MyScanConfig(PluginConfig):
    name = 'fast_add_device'
    verbose_name = 'fast_add_device'
    description = 'Scan device by ip for add new devices'
    version = '0.2.1'
    author = 'Stepanov Evgeniy'
    author_email = 'jacksontur@yandex.ru'
    #packages = ["fast_add_device"],
    #package_data = {"fast_add_device": ["templates/fast_add_device/*.html", "device_types/*", "nb_exec/*"]},


config = MyScanConfig

