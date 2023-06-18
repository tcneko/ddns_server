## DDNS Server



### How to use

##### Build and run the container

* Build the docker image

```bash
cd .../ddns_server/
docker build -t ddns_server:1.0.0 .
```

* Prepare configuration for docker

```bash
mkdir -p /opt/docker_service/ddns_server/docker
cd /opt/docker_service/ddns_server/docker
cp .../ddns_server/docker-compose.yaml.j2 docker-compose.yaml
vim docker-compose.yaml

```

* Prepare configuration for ddns server

``` bash
mkdir -p /opt/docker_service/ddns_server/volume/opt/ddns_server
cd /opt/docker_service/ddns_server/volume/opt/ddns_server
mkdir -p data
touch data/ddns_record.yaml
chown -R {{uid}}:{{gid}} data
cp .../ddns_server/ddns_server.yaml.j2 ddns_server.yaml
vim ddns_server.yaml
```

* Run the docker container

```bash
cd /opt/docker_service/ddns_server/docker
docker-compose up -d
```



#####  Run the reverse proxy web server

* Create a web server configuration (the following is a sample configuration of Caddy)

``` bash
${hostname}:${port} {
  reverse_proxy /api/v1/* ${listen_addr}:${listen_port}
}
```

* Run the web server


