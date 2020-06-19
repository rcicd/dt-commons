import os
import logging

from .constants import HEALTH_FILE

# create logger
logging.basicConfig()
logger = logging.getLogger(os.environ.get('DT_MODULE_TYPE', 'module'))
logger.setLevel(logging.INFO)
if 'DEBUG' in os.environ and os.environ['DEBUG'].lower() in ['true', 'yes', '1']:
    logger.setLevel(logging.DEBUG)


def get_module_health():
    health = "ND"
    if os.path.exists(health):
        try:
            with open(HEALTH_FILE, 'rt') as fin:
                health = fin.read().strip('\n').strip(' ')
        except BaseException:
            logger.warning('An error occurred while trying to fetch the module\'s health.')
    return health


def _set_module_health(new_health):
    health = get_module_health()
    if new_health not in ['healthy', 'unhealthy']:
        logger.warning(f'Health "{new_health}" not recognized!')
        return
    # ---
    if health == new_health:
        return
    logger.debug(f'Updating module health [{health}] -> [{new_health}]')
    # try to write the health status
    try:
        with open(HEALTH_FILE, 'wt') as fout:
            fout.write(new_health)
    except BaseException:
        logger.warning('An error occurred while trying to set the module\'s health.')


def set_module_healthy():
    _set_module_health('healthy')


def set_module_unhealthy():
    _set_module_health('unhealthy')