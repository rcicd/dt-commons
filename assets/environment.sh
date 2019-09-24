#!/bin/bash

_DT_AVAHI_SERVICES_CLEARED=false

dt_install_service() {
  service_name=$1
  # install service
  if [ -f "/avahi-services/${service_name}.service" ]; then
    echo ""
    echo "Activating service [${service_name}]..."
    cp /avahi-services/${service_name}.service /etc/avahi/services/${service_name}.service
    echo "Done!"
  fi
}

dt_install_all_services() {
  # adding services
  if [ -d /avahi-services ]; then
    echo "Activating services broadcast..."
    find /avahi-services -type f -name "dt.*.service" -execdir cp /avahi-services/{} /etc/avahi/services/{} \;
    echo "Done!"
    echo ""
  fi
}

dt_remove_all_services() {
  # removing services
  if [ -d /avahi-services ] && [ "${_DT_AVAHI_SERVICES_CLEARED}" = false ]; then
    echo ""
    echo "Deactivating services broadcast..."
    find /avahi-services -type f -name "dt.*.service" -execdir rm -f /etc/avahi/services/{} \;
    _DT_AVAHI_SERVICES_CLEARED=true
    echo "Done!"
  fi
}

dt_terminate() {
  dt_remove_all_services
  kill -INT `cat /process.pid` 2>/dev/null
}

dt_register_signals() {
  trap dt_terminate SIGINT
  trap dt_terminate SIGTERM
  trap dt_terminate SIGKILL
}

dt_launchfile_init() {
  set -e
  # register signal handlers
  dt_register_signals
  # create CODE_DIR variable
  CODE_DIR="$( cd "$( dirname "${LAUNCHFILE}" )" >/dev/null 2>&1 && pwd )"
}

dt_launchfile_terminate() {
  # wait for the process to end
  set +e
  wait `cat /process.pid` &> /dev/null
  set -e
  # remove installed services
  dt_remove_all_services
}

dt_exec() {
  cmd="$@"
  cmd="${cmd%&} &"
  eval "${cmd}"
  echo $! > /process.pid
}
