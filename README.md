gamify-lyfe
===========

CS316 - An achievement-based approach to life.

Extra README information for final project submission
=====================================================
Code is structured like a typical Django project - one module "core" contains our project.

Assuming django project is set up with setup-django.sh methods:
python manage.py syncdb (or makemigrations if necessary) should set up the db
python manage.py runserver 0.0.0.0:8000
Go to localhost:8000/core to visit site.

Setting up for local (vagrant) development
==========================================

1) Follow the instructions here for setting up Django on your VM:
http://sites.duke.edu/compsci316_01_f2014/help/django/

(The admin password and specifics that you use don't matter because your local "sample module" is not the one we're using)

2) Add your vagrant ssh key found at ~/.ssh/id_rsa.pub to github:
https://help.github.com/articles/generating-ssh-keys/
https://github.com/settings/ssh

3) Clone the git repository (in your shared folder would probably be best for really local development)
'git clone git@github.com:leeviana/gamify-lyfe.git'

(This will make a new gamify-lyfe folder)

4) Running 'python manage.py runserver 0.0.0.0:8000' will run the django instance on localhost:8000

How to fix your out of sync DB
==============================
1) Pull from git (to get the updated .gitignore file)

2) Delete everything in your core/migrations folder except for the __init__.py file[s]

3) Run "python manage.py makemigrations"

4) Run "python manage.py syncdb"
