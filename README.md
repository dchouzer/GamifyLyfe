gamify-lyfe
===========

CS316 - An achievement-based approach to life.

Setting up for local (vagrant) development
==========================================

1) Follow the instructions here for setting up Django on your VM:
http://sites.duke.edu/compsci316_01_f2014/help/django/

(The admin password and specifics that you use don't matter because your local "sample module" is not the one we're using)

2) Add your vagrant ssh key found at ~/.ssh/id_rsa.pub to github:
https://help.github.com/articles/generating-ssh-keys/
https://github.com/settings/ssh

3) Clone the git repository (in your shared folder would probably be best for really local development)
git@github.com:leeviana/gamify-lyfe.git 
	This will make a new gamify-lyfe folder

4) Running 'python manage.py runserver 0.0.0.0:8000' will run the django instance on localhost:8000