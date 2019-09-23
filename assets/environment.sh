#!/bin/bash

dt_install_services() {
  # adding services
  if [ -d /avahi-services ]; then
    echo "Activating services broadcast..."
    find /avahi-services -type f -name "dt.*.service" -execdir cp /avahi-services/{} /etc/avahi/services/{} \;
    echo "Done!"
    echo ""
  fi
}

dt_remove_services() {
  # removing services
  if [ -d /avahi-services ]; then
    echo ""
    echo "Deactivating services broadcast..."
    find /avahi-services -type f -name "dt.*.service" -execdir rm -f /etc/avahi/services/{} \;
    echo "Done!"
  fi
}

dt_terminate() {
  dt_remove_services
  kill -INT `cat /process.pid` 2>/dev/null
}

dt_register_signals() {
  trap dt_terminate SIGINT
  trap dt_terminate SIGTERM
  trap dt_terminate SIGKILL
}

dt_launchfile_init() {
  # install avahi services
  dt_install_services
  # register signal handlers
  dt_register_signals
  # create CODE_DIR variable
  CODE_DIR="$( cd "$( dirname "${LAUNCHFILE}" )" >/dev/null 2>&1 && pwd )"
}

dt_launchfile_terminate() {
  # wait for the process to end
  set +e
  wait `cat /process.pid`&> /dev/null
  set -e
  # remove installed services
  dt_remove_services
}

dt_exec() {
  cmd="$@"
  cmd="${cmd%&} &"
  eval "${cmd}"
  echo $! > /process.pid
}
