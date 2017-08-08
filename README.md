# Item Catalog
Study project for applying knowledge
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
`cd ../../vagrant/ItemCatalog`

### Run project
* To initialize PostgreSQL database run<br>
`bash create_db.sh`
* Start web server<br>
`python application.py`





