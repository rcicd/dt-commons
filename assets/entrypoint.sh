#!/bin/bash

# constants
CONFIG_DIR=/data/config
ROBOT_TYPE_FILE=${CONFIG_DIR}/robot_type
ROBOT_CONFIGURATION_FILE=${CONFIG_DIR}/robot_configuration
ROBOT_HARDWARE_FILE=${CONFIG_DIR}/robot_hardware
DOCKER_BRIDGE_IP_RANGE=(172.17.0.0 172.31.255.255)

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


is_nethost(){
  ipval(){
    # returns the integer representation of an IP arg passed in ascii notation (x.y.z.w)
    IP=$1; IPNUM=0
    for (( i=0 ; i<4 ; ++i )); do
      ((IPNUM+=${IP%%.*}*$((256**$((3-${i}))))))
      IP=${IP#*.}
    done
    echo $IPNUM
  }
  GATEWAY=$(route -n | grep 'UG[ \t]' | awk '{print $2}')
  GATEWAY_INT=$(ipval "${GATEWAY}")
  BRIDGE_MIN_INT=$(ipval "${DOCKER_BRIDGE_IP_RANGE[0]}")
  BRIDGE_MAX_INT=$(ipval "${DOCKER_BRIDGE_IP_RANGE[1]}")
  ! [[ ${GATEWAY_INT} -ge ${BRIDGE_MIN_INT} && ${GATEWAY_INT} -le ${BRIDGE_MAX_INT} ]]
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
      echo "${VEHICLE_IP} ${VEHICLE_NAME} ${VEHICLE_NAME}.local" >> /etc/hosts
    } || {
      echo "WARNING: Failed writing to /etc/hosts. Will continue anyway."
    }
  fi

  # configure hosts
  if [ "${VEHICLE_NAME_IS_SET}" -eq "0" ]; then
    # vehicle name not set (assume vehicle is localhost)
    {
      echo "127.0.0.1 localhost ${VEHICLE_NAME} ${VEHICLE_NAME}.local" >> /etc/hosts
    } || {
      echo "WARNING: Failed writing to /etc/hosts. Will continue anyway."
    }
  fi

  # configure (fake) mDNS
  {
    echo "127.0.0.1 localhost $(hostname) $(hostname).local" >> /etc/hosts
  } || {
    echo "WARNING: Failed writing to /etc/hosts. Will continue anyway."
  }

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
}


configure_python(){
  # make the code discoverable by python
  for d in $(find "${SOURCE_DIR}" -mindepth 1 -maxdepth 1 -type d); do
    debug " > Adding ${d}/packages to PYTHONPATH"
    export PYTHONPATH="${d}/packages:${PYTHONPATH}"
  done
  # make the code discoverable by python
  if [ ${#CATKIN_WS_DIR} -gt 0 ] && [ -d "${CATKIN_WS_DIR}/src" ]; then
      for d in $(find "${CATKIN_WS_DIR}/src" -mindepth 1 -maxdepth 1 -type d); do
        debug " > Adding ${d}/packages to PYTHONPATH"
        export PYTHONPATH="${d}/packages:${PYTHONPATH}"
      done
  fi
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

  # configure ROS_IP / ROS_HOSTNAME
  if is_nethost; then
    # configure ROS_HOSTNAME
    MACHINE_HOSTNAME="$(hostname).local"
    debug "Detected '--net=host', setting ROS_HOSTNAME to '${MACHINE_HOSTNAME}'"
    export ROS_HOSTNAME=${MACHINE_HOSTNAME}
  else
    # configure ROS_IP
    CONTAINER_IP=$(hostname -I 2>/dev/null | cut -d " " -f 1)
    debug "Detected '--net=bridge', setting ROS_IP to '${CONTAINER_IP}'"
    export ROS_IP=${CONTAINER_IP}
  fi

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
