.PHONY: help
help:
	@echo Usage: Building ARM docker image on x86 machines
	@echo "\thelp			Display this message"
	@echo "\tinstall_qemu		Install QEMU (for building ARM image on x86 machines)"
	@echo "\tbuild			Build docker image"
	@echo "\trun			Run the docker image"

.PHONY: install_qemu
install_qemu:
	@/bin/bash qemu_install.sh

ifndef file
	file = Dockerfile
endif

.PHONY: build
build:
	@if [ ! -f "/usr/bin/qemu-arm-static" ]; \
	then \
		$(MAKE) install_qemu; \
	fi;

	@if [ ! -f "${file}" ]; \
	then \
		echo "Dockerfile {${file}} NOT FOUND!\n\n"; \
		exit 1; \
	fi;

	@echo Building docker image...
	@docker build -t raspbian:openvino -f ${file} .

ifndef image
	image = raspbian:openvino
endif
XSOCK=/tmp/.X11-unix
XAUTH=/tmp/.docker.xauth

.PHONY: run
run:
	@touch ${XAUTH}
	@xauth nlist ${DISPLAY} | sed 's/^..../ffff/' | xauth -f ${XAUTH} nmerge -
	@xhost + local:docker
	@docker run --privileged \
		-v /dev:/dev \
		-v ${XSOCK}:${XSOCK} \
		-v ${XAUTH}:${XAUTH} \
		-e XAUTH=${XAUTH} \
		-e DISPLAY \
		-it --rm \
		${image}
