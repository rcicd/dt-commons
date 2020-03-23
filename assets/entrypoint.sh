#!/bin/bash
set -e

export DT_MODULE_INSTANCE=$(basename $(cat /proc/1/cpuset))

configure_vehicle(){
  # check the mandatory arguments
  VEHICLE_NAME_IS_SET=1
  if [ ${#VEHICLE_NAME} -le 0 ]; then
    VEHICLE_NAME_IS_SET=0
    VEHICLE_NAME=$(hostname)
    echo "The environment variable VEHICLE_NAME is not set. Using '${VEHICLE_NAME}'."
  fi
  export VEHICLE_NAME="${VEHICLE_NAME}"

  # check optional arguments
  VEHICLE_IP_IS_SET=0
  if [ ${#VEHICLE_IP} -ne 0 ]; then
    VEHICLE_IP_IS_SET=1
    echo "The environment variable VEHICLE_IP is set to '${VEHICLE_IP}'. Adding to /etc/hosts."
    echo "${VEHICLE_IP} ${VEHICLE_NAME} ${VEHICLE_NAME}.local" >> /etc/hosts
  fi

  # configure hosts
  if [ "${VEHICLE_NAME_IS_SET}" -eq "0" ]; then
    # vehicle name not set (assume vehicle is localhost)
    echo "127.0.0.1 ${VEHICLE_NAME} ${VEHICLE_NAME}.local" >> /etc/hosts
  fi
}

configure_python(){
  # make the code discoverable by python
  for d in $(find ${SOURCE_DIR} -mindepth 1 -maxdepth 1 -type d); do
    if [ "${DEBUG}" = "1" ]; then echo " > Adding ${d} to PYTHONPATH"; fi
    export PYTHONPATH="${d}:${PYTHONPATH}"
  done
}

# configure
if [ "${DEBUG}" = "1" ]; then echo "=> Setting up vehicle configuration..."; fi
configure_vehicle
if [ "${DEBUG}" = "1" ]; then echo -e "<= Done!\n"; fi

if [ "${DEBUG}" = "1" ]; then echo "=> Setting up PYTHONPATH"; fi
configure_python
if [ "${DEBUG}" = "1" ]; then echo -e "<= Done!\n"; fi

# reuse LAUNCHFILE as CMD if the var is set and the first argument is `--`
if [ ${#LAUNCHFILE} -gt 0 ] && [ "$1" == "--" ]; then
  shift
  exec bash -c "$LAUNCHFILE $*"
else
  exec "$@"
fi
