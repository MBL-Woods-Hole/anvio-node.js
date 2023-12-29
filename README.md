# anvio-node.js

An anvio` server for HOMD (Human Oral Microbiome Database)

https://anvio.org/
https://homd.org/
  
How to start docker anvio
  ssh -t -i ~/.ssh/andy.pem ubuntu@anvio.homd.org
list images:
  docker images
list containers:
 docker ps -a
kill a container:
   docker kill 06a1c7bc96ab <CONTAINER ID>
   
Start docker daemon on ubuntu: https://docs.docker.com/config/daemon/start/
   'sudo systemctl start docker'
   or manually: 'sudo dockerd'  
Start anvio container with ports (cd to pangenomes directory first)
   -i, --interactive                    Keep STDIN open even if not attached
   docker run -d --platform linux/amd64 --name anvio --rm -i -v `pwd`:`pwd` -w `pwd` -p 8080-8089:8080-8089 meren/anvio:8
   docker run -d --name anvio -i -v `pwd`:`pwd` -w `pwd` -p 8080-8084:8080-8084 meren/anvio:8
   anvi-display-pan -P 8080 -p Mitis_Group/PAN.db -g Mitis_Group/GENOMES.db --server-only --debug
on local host and other server

kill docker:
docker ps
docker stop <container_id>

Enter a running container:
   docker exec -it <container_name> bash
   docker exec -it anvio bash
   
cd anvio/pangenomes
