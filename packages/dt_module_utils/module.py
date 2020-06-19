from .constants import HEALTH_FILE


def get_module_health():
    health = "ND"
    try:
        with open(HEALTH_FILE, 'rt') as fin:
            health = fin.read().strip('\n').strip(' ')
    finally:
        return health


def set_module_healthy():
    health = get_module_health()
    if health in ['ND', 'none', 'healthy']:
        try:
            with open(HEALTH_FILE, 'wt') as fout:
                fout.write('healthy')
        except BaseException:
            print('WARNING: An error occurred while trying to set the module\'s health.')


def set_module_unhealthy():
    try:
        with open(HEALTH_FILE, 'wt') as fout:
            fout.write('unhealthy')
    except BaseException:
        print('WARNING: An error occurred while trying to set the module\'s health.')