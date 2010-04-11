# One Hour Photo Hunt

## Installation Instructions

### Non-Python dependencies

1. Cassandra
1. Thrift
1. MySQL

### Python dependencies

Ensure you have the required python tools: virtualenv

    sudo easy_install -U virtualenv

Next, create a virtual environment for 1hph and install all dependencies:

    virtualenv gonzo
    source gonzo/bin/activate
    easy_install -U pip
    pip install -U -r 1hph/requirements.txt
