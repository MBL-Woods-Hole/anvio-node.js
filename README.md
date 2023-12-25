# anvio-node.js

An anvio` server for HOMD (Human Oral Microbiome Database)

https://anvio.org/
https://homd.org/

How to start docker anvio

list images:
  docker images
list containers:
 docker ps -a
kill a container:
   docker kill 06a1c7bc96ab <CONTAINER ID>
   
Start docker daemon on ubuntu: https://docs.docker.com/config/daemon/start/
   'sudo systemctl start docker'
   or manually: 'sudo dockerd'  
Start anvio container with ports
   docker run -d --platform linux/amd64 --name anvio --rm -i -v `pwd`:`pwd` -w `pwd` -p 8080-8089:8080-8089 meren/anvio:8
on local host and other server

Enter a running container:
   docker exec -it <container_name> bash
   docker exec -it anvio bash
   
cd anvio/pangenomes
