from setuptools import setup



setup(
    name='fast_add_device',
    version='2.1.5',
    description='Scan device by ip',
    long_description='Scan device by ip for add new devices',
    long_description_content_type='text',
    author='Steanov Evgeniy',
    author_email='jacksontur@yandex.ru',
    license='Nginx',
    install_requires=[],
    packages=["fast_add_device"],
    package_data={"fast_add_device": ["templates/fast_add_device/*.html","device_types/*","nb_exec/*"]},
    zip_safe=False
)

