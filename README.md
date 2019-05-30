# Dockerfile to build Intel® Distribution of OpenVINO™ Toolkit docker image for Raspberry Pi

** Note: for seting up your own local docker registry, follow [this tutoral](LOCAL_DOCKER_REGISTRY.md).

# Make commands

~~~bash
# Usage: Building ARM docker image on x86 machines
#         help            Display this message
#         install_qemu    Install QEMU (for building ARM image on x86 machines)
#         build           Build docker image
#         run             Run the docker image
#         runx11          Run the docker image with X11 forwarding
~~~

## Build

~~~bash
# use make
$ make build [ [file=Dockerfile] [image=raspbian:openvino] ]

# or docker build
$ docker build -t raspbian:openvino .
~~~

## Run the Docker image in privileged mode

~~~bash
# use make
$ make run [ [image=raspbian:openvino] ]

# or docker run
$ docker run --privileged –v /dev:/dev -it --rm raspbian:openvino
~~~

## Run the Docker image with X11 forwarding

### Using make

~~~bash
# run docker image with simple CLI
$ make run [ [image=raspbian:openvino] ]

# or with X11 forwarding
$ make runx11 [ [image=raspbian:openvino] ]
~~~

### Using docker commands

- Setup X11

~~~bash
$ XSOCK=/tmp/.X11-unix
$ XAUTH=/tmp/.docker.xauth
$ touch ${XAUTH}
$ xauth nlist ${DISPLAY} | sed 's/^..../ffff/' | xauth -f ${XAUTH} nmerge -
~~~

- Starting the docker container

~~~bash
# Adds docker to X server access control list (ACL)
$ xhost + local:docker

# Runs the container with X forwarding
$ docker run --privileged \
  -v /dev:/dev \
  -v ${XSOCK}:${XSOCK} \
  -v ${XAUTH}:${XAUTH} \
  -e XAUTH=${XAUTH} \
  -e DISPLAY \
  -it --rm --name=rpi-openvino \
  raspbian:openvino

# Removes docker out of X server ACL if you are not working with
$ xhost - local:docker
 ~~~

Reference: [Create Docker* Images with Intel® Distribution of OpenVINO™ toolkit for Linux* OS
](https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_docker.html#building_docker_image_for_intel_movidius_neural_compute_stick)
