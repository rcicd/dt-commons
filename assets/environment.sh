#!/bin/bash

_DT_AVAHI_SERVICES_CLEARED=false
_DT_AVAHI_SERVICES_DIR=/etc/avahi/services
_DT_PROJECT_SERVICES_DIR=/avahi-services

dt_install_service() {
  service_name=$1
  # install service
  if [ -f "${_DT_PROJECT_SERVICES_DIR}/${service_name}.service" ]; then
    mkdir -p ${_DT_AVAHI_SERVICES_DIR}
    echo "=> Activating service [${service_name}]..."
    cp ${_DT_PROJECT_SERVICES_DIR}/${service_name}.service ${_DT_AVAHI_SERVICES_DIR}/${service_name}.service
    echo -e "<= Done!\n"
  fi
}

dt_install_all_services() {
  # adding services
  if [ -d "${_DT_PROJECT_SERVICES_DIR}" ]; then
    mkdir -p ${_DT_AVAHI_SERVICES_DIR}
    echo "=> Activating services broadcast..."
    find ${_DT_PROJECT_SERVICES_DIR} -type f -name "dt.*.service" -execdir cp ${_DT_PROJECT_SERVICES_DIR}/{} ${_DT_AVAHI_SERVICES_DIR}/{} \;
    echo -e "<= Done!\n"
  fi
}

dt_remove_all_services() {
  # removing services
  if [ -d "${_DT_AVAHI_SERVICES_DIR}" ] && [ -d "${_DT_PROJECT_SERVICES_DIR}" ] && [ "${_DT_AVAHI_SERVICES_CLEARED}" = false ]; then
    if [ "${DEBUG}" = "1" ]; then echo "Deactivating services broadcast..."; fi
    find ${_DT_PROJECT_SERVICES_DIR} -type f -name "dt.*.service" -execdir rm -f ${_DT_AVAHI_SERVICES_DIR}/{} \;
    _DT_AVAHI_SERVICES_CLEARED=true
  fi
}

dt_wait_for_app() {
  # wait for the process to end
  set +e
  wait `cat /process.pid` &> /dev/null
  set -e
  printf "<= App terminated!\n"
}

dt_terminate() {
  # remove installed services
  dt_remove_all_services
  # send SIGINT signal to monitored process
  kill -INT `cat /process.pid` 2> /dev/null
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
  CODE_DIR="$( cd "$( dirname "${LAUNCHFILE}" )" > /dev/null 2>&1 && pwd )"
}

dt_launchfile_terminate() {
  # wait for the process to end
  dt_wait_for_app
  # remove installed services
  dt_remove_all_services
}

dt_exec() {
  cmd="$@"
  cmd="${cmd%&} &"
  echo "=> Launching app..."
  eval "${cmd}"
  echo $! > /process.pid
}
