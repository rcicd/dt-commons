#!/bin/bash
set -e

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

# execute given commands (if any)
exec "$@"
