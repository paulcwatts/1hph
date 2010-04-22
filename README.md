# One Hour Photo Hunt

## Installation Instructions

### Non-Python dependencies

1. MySQL
1. Apache2

### Package requirements (Ubuntu)

apache2, mysql-server, python-setuptools, python-mysqldb, git-core, subversion, libapache2-mod-wsgi, build-essential

### Python dependencies

Ensure you have the required python tools: virtualenv

    sudo easy_install -U virtualenv
    virtualenv gonzo
    source gonzo/bin/activate

Next, create a virtual environment for 1hph and install all dependencies:

    easy_install -U pip
    pip install -U -r 1hph/requirements.txt

### Configuration

You'll need to create a local_settings.py in the 1hph/gonzo directory (or otherwise in your PYTHONPATH)
to add your database configuration and SECRET_KEY.
