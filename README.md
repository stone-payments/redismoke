Redismoke
=========
Simple Python script to test that writes on Redis masters are being correctly
propagated to Redis slaves.

# Usage
You can run the script standalone, or run easily inside a Docker container
(recommended). Run the following instructions for your prefered method,
replacing `conf/config.yml` with the config file for your environment.

To clone the repository, run:
```bash
git clone https://github.com/stone-payments/redismoke.git
cd redismoke
```

## Docker container
```bash
docker build -t redismoke .
docker run -d -v confs/config.yml:/etc/redismoke.yml redismoke
```

## Standalone
```bash
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 src/redismoke.py conf/config.yml
```

# Configuration
The configuration is written in YAML, and it is the sole argument that must be
passed to the Python script. A commented example exists in the `confs`
directory, named `config.yml`, along with configuration files for Redis daemons
used for testing of the code itself.

# Testing
The code is currently being manually tested. Patches for automated testing are
welcome. Run the following:
```
docker-compose build && docker-compose up
```

# Contributing
Just open a PR to this repository with your changes. Notice that there mustn't
be any PEP8 violation in your code in order for your change to be approved.

# License
This code is licensed under the MIT license.
