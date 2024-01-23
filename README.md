# anvio-node.js

### An anvio` pangenome server for HOMD (Human Oral Microbiome Database)
### To be called like this:  http://*{servername}*/anvio?pg=*{pangenomename}*

### Links
[HOMD](https://homd.org/)

[Anvio`](https://anvio.org/)

[https://merenlab.org/2015/08/22/docker-image-for-anvio/](https://merenlab.org/2015/08/22/docker-image-for-anvio/)

This is a custom node.js project for the HOMD (Human Oral Microbiome Database). Using a docker environment
to contain the anvio code we use it to serve any custom HOMD pangenomes. 

If you want to use it on your system you will need to install the docker environment listed in Meren's website:
[docker-image-for-anvio](https://merenlab.org/2015/08/22/docker-image-for-anvio/)
When running the container we open as many as 10 ports for simultaneous open anvio pangenomes
`-p 8080-8089:8080-8089`. The same ten ports need to be listed in the app.js file of the anvio-node.js app
and in the anvio_port_monitor.py python script. 



---
Helpful Docker commands:
How to start docker anvio
 Some helpful docker commands:
 - list images:
 
      `docker images`
 - list containers:
 
     `docker ps -a`
 - kill a container:
     `docker system prune`
     `docker kill 06a1c7bc96ab <container_id>`
 - stop docker:
 
    `docker ps`
    
    `docker stop <container_id>`
 - start a stopped container:
 
    `docker start <container_id>`
---
Start docker daemon on ubuntu: https://docs.docker.com/config/daemon/start/
   `sudo systemctl start docker`
    or manually: `sudo dockerd`

For 7 ports run this command in the pangenomes directory:

 ``docker run -d --cpus=".5" --name anvio -i -v `pwd`:`pwd` -w `pwd` -p 8080-8086:8080-8086 meren/anvio:8``
 
For 10 ports: Change `8080-8084:8080-8084` to `8080-8089:8080-8089`

Testing: Run anvi-diplay-pan from inside Docker:

 ``anvi-display-pan -P 8080 -p Mitis_Group/PAN.db -g Mitis_Group/GENOMES.db --read-only --server-only --debug``

Or outside Docker:

 ``docker exec anvio anvi-display-pan -P 8080 -p Mitis_Group/PAN.db -g Mitis_Group/GENOMES.db --read-only --server-only --debug``

Enter a running container:
 >docker exec -it <container_name> bash>
 >docker exec -it anvio bash


---
### install anvio-homd.js
*`git clone` from github*

*`npm install` to install required libraries.*

*Edit config/config.js to fit your system*

*`npm start` to test system.*

*Use systemd on production system (see anvio.service.TEMPLATE)*

Place pangenomes in a pangenome directory outside of the nodejs app root. And make sure the 'PATH_TO_PANGENOMES' in config.js points to it.
  The name of the pangenome is important and will be used throughout.
  Also the names of the databases inside the pangenome directory must be the same (PAN.db and GENOMES.db) for every pangenome.


Example:
```
~/pangenomes/
  Prochlorococcus_31/
    PAN.db
    GENOMES.db
  Veillonella_Atypica/
    PAN.db
    GENOMES.db
```

---
### anvio_port_monitor.py script
script purpose is to remove unused running anvio pangenomes and report on open port numbers.
./anvio_port_monitor.py -host aws -debug
-debug prints to STDOUT otherwise it will print to a file.
-host defaults to 'localhost'

*Edit the script public/scripts/anvio_port_monitor.py to suit your system (check pangenome directory path and server name).*

*Copy the public/scripts/anvio_port_monitor.py script to the pangenomes directory. Run this script from inside the anvio docker container.*

*Start the anvio_port_monitor.py script (-h for usage)*

---
### nginx

*copy nginx.confTEMPLATE to the system's nginx installation (usually /etc/nginx/conf.d/)*

*test nginx `sudo nginx -t`*

*If okay start it `sudo systemd restart nginx`*

---
*Start this node app (anvio-node.js) `sudo systemd restart anvio`*

*Here is the URL that you use to start an Anvio` pangenome:*

```http://anvio.homd.org/anvio?pg=<pangenome_name>```
