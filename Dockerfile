# parameters
ARG REPO_NAME="dt-commons"

ARG ARCH=arm32v7
ARG MAJOR=daffy
ARG OS_DISTRO=xenial
ARG BASE_TAG=${OS_DISTRO}
ARG BASE_IMAGE=ubuntu

# define base image
FROM ${ARCH}/${BASE_IMAGE}:${BASE_TAG}

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

# add python3.7 sources to APT
RUN echo "deb http://ppa.launchpad.net/deadsnakes/ppa/ubuntu xenial main" >> /etc/apt/sources.list
RUN echo "deb-src http://ppa.launchpad.net/deadsnakes/ppa/ubuntu xenial main" >> /etc/apt/sources.list
RUN gpg --keyserver keyserver.ubuntu.com --recv 6A755776 \
 && gpg --export --armor 6A755776 | apt-key add -

# copy dependencies (APT)
COPY ./dependencies-apt.txt "${REPO_PATH}/"

# install apt dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    $(awk -F: '/^[^#]/ { print $1 }' dependencies-apt.txt | uniq) \
  && rm -rf /var/lib/apt/lists/*

# update alternatives for python, python3
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1
RUN update-alternatives --install /usr/bin/python3 python /usr/bin/python3.7 1

# install pip3
RUN cd /tmp \
  && wget --no-check-certificate http://bootstrap.pypa.io/get-pip.py \
  && python3 ./get-pip.py \
  && rm ./get-pip.py

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

# configure entrypoint
COPY assets/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# store module name
LABEL org.duckietown.label.module.type "${REPO_NAME}"
ENV DT_MODULE_TYPE "${REPO_NAME}"

# store module metadata
ARG MAJOR
ARG BASE_TAG
ARG BASE_IMAGE
LABEL org.duckietown.label.architecture "${ARCH}"
LABEL org.duckietown.label.code.location "${REPO_PATH}"
LABEL org.duckietown.label.code.version.major "${MAJOR}"
LABEL org.duckietown.label.base.image "${BASE_IMAGE}:${BASE_TAG}"

# define maintainer
LABEL maintainer="Andrea F. Daniele (afdaniele@ttic.edu)"
