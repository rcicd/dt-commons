# parameters
ARG REPO_NAME="dt-commons"

ARG ARCH=arm32v7
ARG OS_DISTRO=xenial

# define base image
FROM ${ARCH}/ubuntu:${OS_DISTRO}

# configure environment
ARG ARCH
ENV SOURCE_DIR /code
ENV DUCKIEFLEET_ROOT "/data/config"
ENV READTHEDOCS True
ENV QEMU_EXECVE 1
WORKDIR "${SOURCE_DIR}"

# copy QEMU
COPY ./assets/qemu/${ARCH}/ /usr/bin/

# define repository path
ARG REPO_NAME
ARG REPO_PATH="${SOURCE_DIR}/${REPO_NAME}"
WORKDIR "${REPO_PATH}"

# create repo directory
RUN mkdir -p "${REPO_PATH}"

# copy dependencies (APT)
COPY ./dependencies-apt.txt "${REPO_PATH}/"

# install apt dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    $(awk -F: '/^[^#]/ { print $1 }' dependencies-apt.txt | uniq) \
  && rm -rf /var/lib/apt/lists/*

# copy dependencies (PIP3)
COPY ./dependencies-py3.txt "${REPO_PATH}/"

# install python dependencies
RUN pip3 install -r ${REPO_PATH}/dependencies-py3.txt

# copy the source code
COPY ./code/. "${REPO_PATH}/"

# copy avahi services
COPY ./assets/avahi-services/. /avahi-services/

# copy environment
COPY assets/environment.sh /environment.sh

# create default process ID file
RUN echo 1 > /process.pid

# configure entrypoint
COPY assets/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

LABEL maintainer="Andrea F. Daniele (afdaniele@ttic.edu)"
