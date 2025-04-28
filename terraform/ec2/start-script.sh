# Installing and Running Docker (taken from https://docs.aws.amazon.com/pt_br/serverless-application-model/latest/developerguide/install-docker.html) ----------
sudo yum update -y
sudo yum install -y docker
sudo service docker start

# Adding Permissions (https://docs.docker.com/engine/install/linux-postinstall/)
sudo groupadd docker
sudo usermod -aG docker $USER

# Installing Docker Compose (Manually) https://docs.docker.com/compose/install/linux/
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/download/v2.35.1/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
newgrp docker

docker compose up --build