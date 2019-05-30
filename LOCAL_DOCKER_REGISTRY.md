# Setup Docker Registry on your local machine

## Create docker-compose.yml with following information

~~~yaml
version: '3.0'

services:
  my-local-registry:
    image: registry:latest
    container_name: my-local-registry
    volumes:
      - registry:/var/lib/registry
    ports:
      - "50000:5000"
    restart: unless-stopped
volumes:
  registry:
~~~

## Start the Local Registry

~~~bash
$ docker-compose up -d
~~~

## Pushing Images to Local Docker Registry

Let say your local registry machine has ip `192.168.1.99`, and you want to push your docker images there

~~~bash
# To push the image to local registry we need to tag it appropriately first
$ docker tag raspbian:openvino 192.168.1.99:50000/aitl/raspbian:openvino

# And then we can push it to the registry:
$ docker push 192.168.1.99:50000/aitl/raspbian:openvino
~~~

Now, if we browse to http://192.168.1.99:50000/v2/_catalog we will see that our repository list is no longer empty. We successfully added our image to the local registry!

~~~json
{
    "repositories": [
        "aitl/raspbian"
    ]
}
~~~

Moreover, if we navigate to http://192.168.1.99:50000/v2/aitl/raspbian/tags/list we’ll see:

~~~json
{
    "name": "aitl/raspbian",
    "tags": [
        "openvino"
    ]
}
~~~

## Some errors

If you get this message bellow:

~~~
Using default tag: <some_tag>
Error response from daemon: Get https://<your_local_registry_id>:5000/v1/_ping: http: server gave HTTP response to HTTPS client
~~~

Do as following to resolve:

1. Create or modify /etc/docker/daemon.json

    ~~~bash
    echo '{ "insecure-registries":["myregistry.example.com:5000"] }' \
    sudo tee -a /etc/docker/daemon.json
    ~~~

2. Restart docker daemon

    ~~~bash
    sudo service docker restart
    ~~~

Reference: [Docker Hub vs Creating a Local Docker Registry](https://code-maze.com/docker-hub-vs-creating-docker-registry/)