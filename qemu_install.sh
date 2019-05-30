#!/bin/bash

# install prequisites qemu packages
sudo apt-get update && \
sudo apt-get install -y --no-install-recommends qemu-user-static binfmt-support
sudo update-binfmts --enable qemu-arm
sudo update-binfmts --display qemu-arm

# git clone git://git.qemu.org/qemu.git
# cd qemu
# ./configure --target-list=arm-linux-user --static
# make

sudo mount binfmt_misc -t binfmt_misc /proc/sys/fs/binfmt_misc
echo ':arm:M::\x7fELF\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x28\x00:\xff\xff\xff\xff\xff\xff\xff\x00\xff\xff\xff\xff\xff\xff\xff\xff\xfe\xff\xff\xff:/usr/bin/qemu-arm-static:' | sudo tee /proc/sys/fs/binfmt_misc/register

cp --force /usr/bin/qemu-arm-static .
