#!/bin/bash

# constants
CONFIG_DIR=/data/config
ROBOT_TYPE_FILE=${CONFIG_DIR}/robot_type
ROBOT_CONFIGURATION_FILE=${CONFIG_DIR}/robot_configuration
ROBOT_HARDWARE_FILE=${CONFIG_DIR}/robot_hardware
ROBOT_TAG_ID_FILE=${CONFIG_DIR}/robot_tag_id
ROBOT_MAP_NAME_FILE=${CONFIG_DIR}/robot_map_name

echo "==> Entrypoint"

# if anything weird happens from now on, STOP
set -e

# reset health
echo ND > /health

# get container ID
DT_MODULE_INSTANCE=$(basename "$(cat /proc/1/cpuset)")
export DT_MODULE_INSTANCE


debug(){
  if [ "${DEBUG}" = "1" ]; then
    echo "DEBUG: $1";
  fi
}


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
  if [ ${#VEHICLE_IP} -ne 0 ]; then
    echo "The environment variable VEHICLE_IP is set to '${VEHICLE_IP}'. Adding to /etc/hosts."
    {
      echo "${VEHICLE_IP} ${VEHICLE_NAME} ${VEHICLE_NAME}.local" | dd of=/etc/hosts &>/dev/null
    } || {
      echo "WARNING: Failed writing to /etc/hosts. Will continue anyway."
    }
  fi

  # configure hosts
  if [ "${VEHICLE_NAME_IS_SET}" -eq "0" ]; then
    # vehicle name not set (assume vehicle is localhost)
    {
      echo "127.0.0.1 localhost ${VEHICLE_NAME} ${VEHICLE_NAME}.local" | dd of=/etc/hosts &>/dev/null
    } || {
      echo "WARNING: Failed writing to /etc/hosts. Will continue anyway."
    }
  fi

  # robot_type
  if [ ${#ROBOT_TYPE} -le 0 ]; then
      if [ -f "${ROBOT_TYPE_FILE}" ]; then
          ROBOT_TYPE=$(cat "${ROBOT_TYPE_FILE}")
          debug "ROBOT_TYPE[${ROBOT_TYPE_FILE}]: '${ROBOT_TYPE}'"
          export ROBOT_TYPE
      else
          echo "WARNING: robot_type file does not exist. Using 'duckiebot' as default type."
          export ROBOT_TYPE="duckiebot"
      fi
  else
      echo "INFO: ROBOT_TYPE is externally set to '${ROBOT_TYPE}'."
  fi

  # robot_configuration
  if [ ${#ROBOT_CONFIGURATION} -le 0 ]; then
      if [ -f "${ROBOT_CONFIGURATION_FILE}" ]; then
          ROBOT_CONFIGURATION=$(cat "${ROBOT_CONFIGURATION_FILE}")
          debug "ROBOT_CONFIGURATION[${ROBOT_CONFIGURATION_FILE}]: '${ROBOT_CONFIGURATION}'"
          export ROBOT_CONFIGURATION
      else
          echo "WARNING: robot_configuration file does not exist."
          export ROBOT_CONFIGURATION="__NOTSET__"
      fi
  else
      echo "INFO: ROBOT_CONFIGURATION is externally set to '${ROBOT_CONFIGURATION}'."
  fi

  # robot_hardware
  if [ ${#ROBOT_HARDWARE} -le 0 ]; then
      if [ -f "${ROBOT_HARDWARE_FILE}" ]; then
          ROBOT_HARDWARE=$(cat "${ROBOT_HARDWARE_FILE}")
          debug "ROBOT_HARDWARE[${ROBOT_HARDWARE_FILE}]: '${ROBOT_HARDWARE}'"
          export ROBOT_HARDWARE
      else
          echo "WARNING: robot_hardware file does not exist."
          export ROBOT_HARDWARE="__NOTSET__"
      fi
  else
      echo "INFO: ROBOT_HARDWARE is externally set to '${ROBOT_HARDWARE}'."
  fi

  # robot_tag_id
  if [ ${#ROBOT_TAG_ID} -le 0 ]; then
      if [ -f "${ROBOT_TAG_ID_FILE}" ]; then
          ROBOT_TAG_ID=$(cat "${ROBOT_TAG_ID_FILE}")
          if [[ "${ROBOT_TAG_ID}" -le 0 ]]; then
              echo "WARNING: robot_tag_id file has an invalid value, '${ROBOT_TAG_ID}'."
              export ROBOT_TAG_ID="__NOTSET__"
          else
              debug "ROBOT_TAG_ID[${ROBOT_TAG_ID_FILE}]: '${ROBOT_TAG_ID}'"
              export ROBOT_TAG_ID
          fi
      else
          echo "WARNING: robot_tag_id file does not exist."
          export ROBOT_TAG_ID="__NOTSET__"
      fi
  else
      echo "INFO: ROBOT_TAG_ID is externally set to '${ROBOT_TAG_ID}'."
  fi

  # robot_map_name
  if [ ${#ROBOT_MAP_NAME} -le 0 ]; then
      if [ "${ROBOT_TYPE}" = "duckietown" ]; then
          # robots of type `duckietown` belong to themselves
          export ROBOT_MAP_NAME="${VEHICLE_NAME}"
      else
          # any other robot type can declare a map name in a file
          if [ -f "${ROBOT_MAP_NAME_FILE}" ]; then
              ROBOT_MAP_NAME=$(cat "${ROBOT_MAP_NAME_FILE}")
              if [ ${#ROBOT_MAP_NAME} -le 0 ]; then
                  export ROBOT_MAP_NAME="__NOTSET__"
              else
                  debug "ROBOT_MAP_NAME[${ROBOT_MAP_NAME_FILE}]: '${ROBOT_MAP_NAME}'"
                  export ROBOT_MAP_NAME
              fi
          else
              echo "WARNING: robot_map_name file does not exist."
              export ROBOT_MAP_NAME="__NOTSET__"
          fi
      fi
  else
      echo "INFO: ROBOT_MAP_NAME is externally set to '${ROBOT_MAP_NAME}'."
  fi
}


configure_python(){
  # make the code discoverable by python
  for d in $(find "${SOURCE_DIR}" -mindepth 1 -maxdepth 1 -type d); do
    debug " > Adding ${d}/packages to PYTHONPATH"
    export PYTHONPATH="${d}/packages:${PYTHONPATH}"
  done
}


configure_ROS(){
  # check if ROS_MASTER_URI is set
  ROS_MASTER_URI_IS_SET=0
  if [ -n "${ROS_MASTER_URI}" ]; then
    ROS_MASTER_URI_IS_SET=1
  fi

  # constants
  ROS_SETUP=(
    "/opt/ros/${ROS_DISTRO}/setup.bash"
    "${SOURCE_DIR}/catkin_ws/devel/setup.bash"
    "${SOURCE_DIR}/setup.bash"
  )

  # setup ros environment
  for ROS_SETUP_FILE in "${ROS_SETUP[@]}"; do
    if [ -f "${ROS_SETUP_FILE}" ]; then
      source "${ROS_SETUP_FILE}";
    fi
  done

  # TODO: disabled because it causes issues, should revisit
#  # configure ROS IP (do not use IPs starting with 172., those are Docker internal IPs)
#  for IP in $(hostname -I 2>/dev/null); do
#      if echo "${IP}" | grep -q -v "^172\."; then
#          export ROS_IP=${IP}
#      fi
#  done

  # configure ROS IP
  CONTAINER_IP=$(hostname -I 2>/dev/null | cut -d " " -f 1)
  export ROS_IP=${CONTAINER_IP}

  # configure ROS MASTER URI
  if [ "${ROS_MASTER_URI_IS_SET}" -eq "0" ]; then
    export ROS_MASTER_URI="http://${VEHICLE_NAME}.local:11311/"
  fi
}


# configure
debug "=> Setting up vehicle configuration..."
configure_vehicle
debug "<= Done!\n"

debug "=> Setting up PYTHONPATH..."
configure_python
debug "<= Done!\n"

debug "=> Setting up ROS environment..."
configure_ROS
debug "<= Done!\n"

# mark this file as sourced
DT_ENTRYPOINT_SOURCED=1
export DT_ENTRYPOINT_SOURCED

# if anything weird happens from now on, CONTINUE
set +e

echo "<== Entrypoint"

# exit if this file is just being sourced
if [ "$0" != "${BASH_SOURCE[0]}" ]; then
    return
fi

# reuse DT_LAUNCHER as CMD if the var is set and the first argument is `--`
if [ ${#DT_LAUNCHER} -gt 0 ] && [ "$1" == "--" ]; then
  shift
  exec bash -c "dt-launcher-$DT_LAUNCHER $*"
else
  exec "$@"
fi
