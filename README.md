# Sport Item Catalog
Study project. Applying knowledge
about SQLAlchemy ORM, Flask framework, and OAuth.

## Running on VM

### Prerequisites
* Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
* Install [Vagrant](https://www.vagrantup.com/)

### Installation
* Download Vagrant VM<br>
`git clone https://github.com/udacity/fullstack-nanodegree-vm.git`
* In terminal change directory to<br>
`cd <your path>/fullstack-nanodegree-vm/vagrant`
* Download project to vagrant folder<br>
`git clone https://github.com/MariiaSurmenok/ItemCatalog.git`

### Start Virtual Machine
* In terminal (in vagrant folder) launch virtual machine<br>
`vagrant up`<br>
(The first launch requires some time to install all dependencies)
* Connect to vm<br>
`vagrant ssh`
* Return to project folder<br>
`cd /vagrant/ItemCatalog`

### OAuth Credentials

#### Facebook login
* To get credentials for Facebook, create a project in [Facebook developer console](https://developers.facebook.com/)
* Update file **fb_client_secrets.json** with your app_id and app_secret
* Go to file `cd templates/login.html` and update value **appId** in line 9

#### Google login
* To get credential for Google, create a project in [Google developer console](https://console.developers.google.com)
* Go to credentials page and add URIs for Web client
* Download json with credentials with name **g_client_secrets.json** in the *ItemCatalog* folder
* Go to file `cd templates/login.html` and update value **data-clientid** in line 66
### Run project
* To initialize PostgreSQL database run<br>
`bash create_db.sh`
* Start web server<br>
`python application.py`





