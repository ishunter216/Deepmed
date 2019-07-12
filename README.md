# What's inside?
 * [Django](https://github.com/django/django) 1.11 /[Django REST framework](https://github.com/tomchristie/django-rest-framework)
 * [Redis](https://github.com/antirez/redis)
 * [PostgreSQL](https://github.com/postgres/postgres)
 * [Mongo DB](https://www.mongodb.com/)
 * [Gunicorn](https://github.com/benoitc/gunicorn) WSGI HTTP Server
 * [Nginx](https://nginx.org/)
 * [Celery](https://github.com/celery/celery) Distributed Task Queue
 * [Flower](http://flower.readthedocs.io/en/latest/) is a tool for monitoring and administrating [Celery](https://github.com/celery/celery) clusters.
 * [Supervisor](https://github.com/Supervisor/supervisor) - client/server process management system
 * Config samples for each tool from above
 * and more...

# How to start:
 1. Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads) if not installed.
 2. Install [Vagrant](https://www.vagrantup.com/downloads.html) if not installed.
 3. Install  [Ansible (2.0.0+)](http://docs.ansible.com/ansible/intro_installation.html) if not installed.
 4. Run `sudo ansible-galaxy install -r ./ansible/requirements.yml` from root project directory for installing Ansible role dependencies.
 5. Run `sudo -- sh -c "echo '192.168.44.77 deepmed.local flower.deepmed.local api.deepmed.local' >> /etc/hosts"` for simple accessing to Vagrant machine in your browser.
 6. Run `vagrant up` from root project directory for start the Vagrant machine. At first time machine will be automatically provisioned.
 7. Configure PyCharm (if you are using it):
     - Configuring Python interpreter: File > Settings > Project Interpreter > Add Remote > Vagrant > Python interpreter path: `/home/ubuntu/deepmed/venv/bin/python` > OK
     - Configuring Django support: File > Settings > Languages & Frameworks > Django > Enable Django support; Django project root: `{project_dir}`; Settings: `deepmed/settings.py`
     - Configuring Django run/debug configurations: Run > Edit configurations… > Add new configuration > Django server > Name: Django Development Server; Host: 0.0.0.0; Port: 8000; Run browser: http://api.deepmed.local:8000/; Path mapping: `Local path - path to project on host system : Remote path - path to project on vagrant machine`
     - Configuring database: Database > Add > Data Source > PostgreSQL > Download Driver > Host: `localhost`; Port: `5432`; Database: `deepmed`; User: `deepmed`; Password: `{password}` > Configure SSH > Check use SSH tunnel; Proxy host: `127.0.0.1`; Port: `2222`; Proxy user: `vagrant`; Auth type: Key pair; Private key file: `./.vagrant/machines/default/virtualbox/private_key` > OK > Test Connection > OK

# Project structure:
## Directories
Directory structure in the deployed virtual machine.

 *  `/home/{deploy user}/{project name}/` - Main director.
 *  `/home/{deploy user}/{project name}/etc/` - Directory contains configuration files.
 *  `/home/{deploy user}/{project name}/log/` - Directory contains logs.
 *  `/home/{deploy user}/{project name}/run/` - Directory contains unix sockets and pid files.
 *  `/home/{deploy user}/{project name}/src/` - Directory contains source code of project.
 *  `/home/{deploy user}/{project name}/bin/` - Directory contains scripts.
 *  `/home/{deploy user}/{project name}/venv/` - Directory with virtualenv.

## Manage services
>   `./ansible/group_vars/` directory contains files with variables for generation configuration files of Supervisor and Systemd.

### List services
 List of services which installed and configured by Ansible.

> Names of service could be changed in `./ansible/group_vars/`

 -  Nginx - `sudo service nginx start|stop|restart|reload|force-reload|status`
 -  Postgresql - `sudo service postgresql start|stop|restart|reload|force-reload|status`
 -  Redis - `sudo service redis_6379 start|stop|restart|reload|force-reload|status`
 -  Celery worker - `sudo service {project_name}-worker start|stop|restart|reload|force-reload|status`
 -  Celery beat - `sudo service {project_name}-beat start|stop|restart|reload|force-reload|status`
 -  Gunicorn (WSGI HTTP Server) for Django - `sudo supervisorctl {actions: start|restart|stop|status|...} {gunicorn_supervisor_name|default({project_name}-gunicorn)}`
 -  Flower (Monitoring&Management of Celery) for Django - `sudo supervisorctl {actions: start|restart|stop|status|...} {flower_supervisor_name|default({project_name}-flower)}`

## Nginx configurations
Domain initialized in `./ansible/group_vars/project.yml`|`./ansible/host_vars/staging/vars.yaml`|`./ansible/host_vars/production/vars.yaml` files and used by default NGINX configs (`./ansible/group_vars/nginx.yaml`).

Default structure of domains:
 -  {site_domain} - default `project.local`. Main domain (which could used for frontend application).
 -  {api_domain} - default `api.{site_domain}.local`. sub-domain which uses for Django application.
 -  {flower_domain} - default `flower.{site_domain}.local`. sub-domain for Flower (monitoring and management tool for Celery)

> By default WebSocket connection is available by `api.{site_domain}.local/ws/` address.

## Notices of Django application structure
Source code of Django application is in `project` directory of boilerplate.
> All configuration and code of stuff such as ansible|vagrant|docker|other should be in root directory of boilerplate at the same level as `project` and `ansible` directories.

#### oAuth2 & Fixtures
This boilerplate has implemented oAuth2 authorization by using [Django OAuth Toolkit](https://django-oauth-toolkit.readthedocs.io/en/latest/) library.
During setup of server Ansible will load fixtures to create default superuser and oAuth application (You could find credentials in `/home/{deploy user}/{project name}/src/project/fixtures/`) also you could disable loading fixtures in `./ansible/group_vars/backend.yml` or `./ansible/host_vars/vagrant|develop|staging|production`.

#### Django settings file
Ansible creates local_settings.py file (by template (`./ansible/roles/webtier/templates/local_settings.py`) and variables in `./ansible/group_vars/` and `./ansible/host_vars/`) which contains configs to services and libraries (DB/Redis/python libraries and etc) according to environment (vagrant/develop/staging/production - values are defined in `./ansible/host_vars/vagrant|develop|stating|production`).
 The local_settings.py is re-created every time after deploying with Ansible and is in the root directory of Django code at the same level as `manage.py` file.

***
##### _Notice!_ In this project is used Ansible Vault!
Files `./ansible/host_vars/staging/vault.yml` and `./ansible/host_vars/staging/vault.yml` are encrypted by default (Default password is `Ulumulu88`).
They're used to store sensitive data as db names, passwords, keys, secrets etc.
Before deploying to public servers as production or staging you must:

 1. Decrypt necessary files by command `ansible-vault decrypt ./ansible/host_vars/staging/vault.yml ./ansible/host_vars/production/vault.yml --ask-vault-pass` (run it from ansible directory) using default password.
 2. Edit configuration in those files as needed.
    Also if it's first edition of those files you _SHOULD_ edit:
     - database name, user and password;
     - django secret key (http://www.miniwebtool.com/django-secret-key-generator/);
    For passwords better to use generated (http://passwordsgenerator.net/).
 3. Encrypt files again with your _NEW AND SECURE_ password using command `ansible-vault encrypt ./ansible/host_vars/staging/vault.yml ./ansible/host_vars/production/vault.yml --ask-vault-pass`.
 4. Have fun!
***

## How to deploy the project to remote server(s)
 1. Edit respective files in a `host_vars` directory, as well as inventory files. This repo includes default configuration samples for production and staging environments.
 2. Execute `./deploy <inventory name> <tags>` command in the project's root directory, where <inventory name> is the name of your inventory (e.g. "staging" or "production"), and <tags> are optional tags that will execute only the tasks that were marked by this tag (e.g. "provision" tag, which will skip installing most part of the setup and only update the code from a repo and restart services).
 3. Give password to decrypt necessary vault data.
 3. Enjoy deployment :)

# Useful commands

## Deploy.sh script
 - `./deploy {environment} {tags}` - Deploy to {environment} servers by chosen tags. Example: `./deploy vagrant` - will run all deploy process to vagrant machine, `./deploy vagrant backend` - will run backend part of deploy process to vagrant machine.

## Ansible
 - `bin/ansible-playbook -i ./ansible/{environment}.ini ./ansible/site.yml` - Deploy to {environment} servers.

## Vagrant
 - `vagrant up` - Start the virtual machine.
 - `vagrant halt` - Shutdown the virtual machine.
 - `vagrant destroy` - Destroy the virtual machine.
 - `vagrant provision` - Triggers provisioning on a running virtual machine.
 - `vagrant ssh` - Create an ssh connection with the virtual machine.
 - `vagrant reload` - Restarts vagrant machine, loads new Vagrantfile configuration.
 - `vagrant status` - Outputs status of the vagrant machine.
 - `vagrant suspend` - Suspends the machine.
 - `vagrant resume` - Resume a suspended vagrant machine.
 - `vagrant share` - Share your Vagrant environment with anyone in the world.

### SSH
 - `ssh-keygen -t rsa -f ~/.ssh/id_rsa -C "your_email@example.com"` - Generate a new SSH key (https://help.github.com/articles/generating-ssh-keys/).
 - `cat ~/.ssh/id_rsa.pub` - Show SSH public key.
 - `cat ~/.ssh/id_rsa` - Show SSH private key.
