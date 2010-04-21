# One Hour Photo Hunt

## Installation Instructions

### Non-Python dependencies

1. Cassandra
1. Thrift
1. MySQL

### Package requirements (Ubuntu)

apache2, mysql-server, python-setuptools, python-mysqldb, git-core, subversion, libapache2-mod-wsgi, build-essential

### Python dependencies

Ensure you have the required python tools: virtualenv

    sudo easy_install -U virtualenv
    virtualenv gonzo
    source gonzo/bin/activate

Next, download and install pycassa and thrift (these don't work well with pip)

    easy_install -U thrift
    git clone git://github.com/vomjom/pycassa.git
    cd pycassa; python setup.py --cassandra install

Next, create a virtual environment for 1hph and install all dependencies:

    easy_install -U pip
    pip install -U -r 1hph/requirements.txt

