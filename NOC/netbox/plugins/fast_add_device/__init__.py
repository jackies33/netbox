

from extras.plugins import PluginConfig


class MyScanConfig(PluginConfig):
    name = 'fast_add_device'
    verbose_name = 'fast_add_device'
    description = 'Scan device by ip for add new devices'
    version = '0.1.2'
    author = 'Stepanov Evgeniy'
    author_email = 'jacksontur@yandex.ru'


config = MyScanConfig

