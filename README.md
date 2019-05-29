# Dockerfile to build Intel® Distribution of OpenVINO™ Toolkit docker image for Raspberry Pi


## Build

~~~bash
$ docker build -t raspbian:openvino .
~~~


## Run the Docker image in privileged mode

~~~bash
$ docker run --privileged –v /dev:/dev -it --rm raspbian:openvino
~~~


## Run the Docker image with X11 forwarding

- Setup X11

~~~bash
$ XSOCK=/tmp/.X11-unix
$ XAUTH=/tmp/.docker.xauth
$ touch $XAUTH
$ xauth nlist $DISPLAY | sed 's/^..../ffff/' | xauth -f $XAUTH nmerge -
~~~

- Starting the docker container

~~~bash
# Adds docker to X server access control list.
$ xhost + local:docker

# Run the container with X forwarding
$ docker run --privileged \
  -v /dev:/dev \
  -v $XSOCK:$XSOCK \
  -v $XAUTH:$XAUTH \
  -e XAUTH=$XAUTH \
  -e DISPLAY \
  -it --rm --name=rpi-openvino \
  raspbian:openvino
 ~~~
 
 
Reference: [Create Docker* Images with Intel® Distribution of OpenVINO™ toolkit for Linux* OS
](https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_docker.html#building_docker_image_for_intel_movidius_neural_compute_stick)
