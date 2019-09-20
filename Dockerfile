# parameters
ARG REPO_NAME="dt-commons"

ARG ARCH=arm32v7
ARG OS_DISTRO=xenial

# define base image
FROM ${ARCH}/ubuntu:${OS_DISTRO}

# configure environment
ENV SOURCE_DIR /code
ENV DUCKIEFLEET_ROOT "/data/config"
ENV READTHEDOCS True
WORKDIR "${SOURCE_DIR}"

# define repository path
ARG REPO_NAME
ARG REPO_PATH="${SOURCE_DIR}/${REPO_NAME}"
WORKDIR "${REPO_PATH}"

# create repo directory
RUN mkdir -p "${REPO_PATH}"

# copy dependencies files only
COPY ./dependencies-apt.txt "${REPO_PATH}/"
COPY ./dependencies-py.txt "${REPO_PATH}/"

# install apt dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    $(awk -F: '/^[^#]/ { print $1 }' dependencies-apt.txt | uniq) \
  && rm -rf /var/lib/apt/lists/*

# install python dependencies
RUN pip install -r ${REPO_PATH}/dependencies-py.txt

# copy the source code
COPY ./code/. "${REPO_PATH}/"

# configure entrypoint
COPY assets/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

LABEL maintainer="Andrea F. Daniele (afdaniele@ttic.edu)"
