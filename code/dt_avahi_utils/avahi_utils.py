import os
import shutil

def get_available_services_dir():
    return '/avahi-services'

def get_install_services_dir():
    return '/etc/avahi/services'

def enable_service(service_name, force_replace=False):
    source_service_path = os.path.join(get_available_services_dir(), service_name+".service")
    if not os.path.exists(source_service_path):
        raise ValueError('The service [{}] does not exist.'.format(source_service_path))
    dest_service_path = os.path.join(get_install_services_dir(), service_name+".service")
    # install service
    if not os.path.exists(dest_service_path) or force_replace:
        shutil.copyfile(source_service_path, dest_service_path)

def disable_service(service_name, force=False):
    source_service_path = os.path.join(get_available_services_dir(), service_name+".service")
    if not os.path.exists(source_service_path):
        if force:
            print('WARNING: You are disabling a service that does not belong to you.')
        else:
            raise ValueError('You tried to disable a service [{}] that does not belong to you. Force it or fix it.'.format(service_name))
            exit(1)
    dest_service_path = os.path.join(get_install_services_dir(), service_name+".service")
    # remove service
    if os.path.exists(dest_service_path):
        os.remove(dest_service_path)
