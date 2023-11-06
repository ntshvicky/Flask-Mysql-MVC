# generate flask secret key and add on .env
python3 -c 'import secrets, base64;print(base64.urlsafe_b64encode(secrets.token_bytes(32)))'


# to push and pull
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
git add .
git commit -m "okay"
git push origin master

# for pdf printing install wkhtmltopdf
https://computingforgeeks.com/install-wkhtmltopdf-on-ubuntu-debian-linux/


# deploye api in Ubuntu server (aprox same in all Linux)
## Install Nginx - apt-get install nginx
## Install wkhtmltopdf - as above URL
## Install database mysql - 
1. apt-get install mysql-server 
2. setup using - sudo mysql_secure_installation
3. create database by executing sql file - mysql -u root -p < testdb2.sql
## Setup project
1. Download or clone your project
2. inside the project directory create python virtual environment
    a) python3 -m virtualenv env
    b) source env/bin/activate
3. install all dependencies - 
    pip3 install -r requirements.txt
    pip3 install 'pydantic[email]' # if required
    pip3 install 'flask-openapi3[yaml]' # if required
4. create service file same as api.service in /etc/systemd/system based on your environment
5. start service - systmctl start api.service
6. add service to startup - systmctl enable api.service
7. check if service is running - systemctl status api.service
8. Listen this service to nginx web server
    a) add a file like "api" in /etc/nginx/sites-available
    b) Link this file to nginx enable directory - /etc/nginx/sites-enabled
        sudo ln -s /etc/nginx/sites-available/api /etc/nginx/sites-enabled
9. check if service is running or there is no error on deployment - nginx -t
10. start nginx web server - systmctl restart nginx
11. Run in IP


If you are using cloud server like ubuntu or aws, dont forget to open 80 port or port you required to listen nginx for this api

# or setup via docker
## How to run docker and docker setup
1. Create Dockerfile in app folder
2. other project required files
3. create a docker-compose.yml in root folder, where you have to execute docker-compose command
4. create a nginx.conf file with nginx configuartion to run app in webserver 
    This is important to run app in any webserver so you can execute all running instances in one port with reverse proxy setting
    This can handle load balancer and traffic

## Some docker command
run docker - docker-compose up
run with rebuild image - docker-compose up --build
run with rebuild image and on background - docker-compose up -d --build
run multiple instance of app - docker-compose up -d --build --scale app=3 #3 is for three instance
check running instances - docker-compose ps or docker ps
stop docker running instances - docker-compose down
auto start docker - sudo chkconfig docker on

docker network inspect bridge



# install docker in linux server
## 1. AMAZON LINUX
sudo su
yum update -y
amazon-linux-extras install docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user
# check docker status
docker info 
# download project
git clone -b master <your-git-URL>
# download docker composer
sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose 
sudo chmod +x /usr/local/bin/docker-compose
# write this line on ~/.bashrc file for permanent setup
export PATH=$PATH:/usr/local/bin/
docker-compose version
# run project
docker-compose up -d --build --scale app=5

## Setup ECR for docker image upload
1. Create a new repo in ECR
2. Setup IAM role in EC2 instance
    a. go to IAM role
    b. create role
    c. select EC2
    d. next go to permission
    e. select AmazonEC2ContainerRegistryFullAccess 
    f. next go to tag (Optional)
    g. next go to create role , name the role like docker-ec2-ecr-access-role and Create Role.
3. Attach role in EC2 inatance
    a. select instance in ec2 
    b. go to action
    c. modify IAM role
4. Setup aws cli and configure aws  using command "aws configure"
5. run from push command instruction in ECR dashboard
Retrieve an authentication token and authenticate your Docker client to your registry.
Use the AWS CLI:

=> aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <aws-id-here>.dkr.ecr.ap-south-1.amazonaws.com
Note: If you receive an error using the AWS CLI, make sure that you have the latest version of the AWS CLI and Docker installed.
Build your Docker image using the following command. For information on building a Docker file from scratch see the instructions here . You can skip this step if your image is already built:

=> docker build -t test-docker app/
After the build completes, tag your image so you can push the image to this repository:

=> docker tag test-docker:latest <aws-id-here>.dkr.ecr.ap-south-1.amazonaws.com/test-docker:latest
Run the following command to push this image to your newly created AWS repository:

=> docker push <aws-id-here>.dkr.ecr.ap-south-1.amazonaws.com/test-docker:latest

6. Pull ECR file in EC2 or where you want
docker pull <aws-id-here>.dkr.ecr.ap-south-1.amazonaws.com/test-docker 



# database example, how to save data to database
Change your code as per your requirements and more security to save and pass data
while creating send sha256 of password
// Example sha256("12345") will be "5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5"
{
    "fullname": "Admin",
    "username": "admin",
    "password": sha256(plaintext_password), 
    "email": "admin@gmail.com",
    "mobile": "12345678"
}

same while login 
{
    "username": "username/email",
    "password": "5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5"
}