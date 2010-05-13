# One Hour Photo Hunt

## Installation Instructions

### Non-Python dependencies

1. MySQL
1. Apache2

### Package requirements (Ubuntu)

apache2, mysql-server python-setuptools python-mysqldb python-dev git-core subversion libapache2-mod-wsgi build-essential libjpeg-dev libpng12-dev

### Installation

    sudo easy_install -U virtualenv
    virtualenv gonzo
    source gonzo/bin/activate
    easy_install -U pip

Next, install 1hph from git and all of its dependencies

    pip install -e git+git@github.com:paulcwatts/1hph.git#egg=1hph
    pip install -U -r gonzo/src/1hph/requirements.txt

### Configuration

Next you'll need to create a local settings module to add your specific database settings
and SECRET_KEY. This can live anywhere in the Python path, and can be specified using the environment
variable GONZO_LOCAL_SETTINGS_MODULE. The default is 'gonzo.local_settings'.

TODO: Use the gonzo.wsgi file template to hook into Apache.

### Database

Step-by-step instructions to set up MySQL.

    mysql -u root -p
    (enter password)

    mysql> create database gonzo;
    mysql> create user 'gonzo'@'localhost' identified by 'some_pass';
    mysql> grant all privileges on *.* to 'gonzo'@'localhost' with grant option;

Use this user in your Django settings.

### Syncing the database

Once you have your database and Apache configuration set up, you can then sync the Django DB to MySQL:

    source gonzo/bin/activate
    django-admin.py syncdb --settings=gonzo.settings --pythonpath=<path_to_local_settings>
