Redismoke
=========
[![Build Status](https://travis-ci.org/stone-payments/redismoke.svg?branch=master)](https://travis-ci.org/stone-payments/redismoke)
[![Updates](https://pyup.io/repos/github/stone-payments/redismoke/shield.svg)](https://pyup.io/repos/github/stone-payments/redismoke/)
[![Python 3](https://pyup.io/repos/github/stone-payments/redismoke/python-3-shield.svg)](https://pyup.io/repos/github/stone-payments/redismoke/)

Simple Python script to test that writes on Redis masters are being correctly propagated to Redis slaves.

## Usage
You can either use a pre-built Docker container, build one container yourself or use the script with a simple
virtualenv.

### Use a pre-built Docker image
Run the following to use the latest pre-built docker image from Docker Hub. Don't forget to create a config file
following [our example file](https://github.com/stone-payments/redismoke/blob/master/confs/config.yml). The path you
must pass to the Docker volume argument (-v) must be absolute.
```bash
docker run -v /absolute/path/redismoke.yml:/opt/redismoke/redismoke.yml bcdonadio/redismoke:latest
```

### Use the source
To clone the repository, run:
```bash
git clone https://github.com/stone-payments/redismoke.git
cd redismoke
```
#### Use a self-built Docker container
Build and run the Docker container with the following commands:
```bash
docker build -t redismoke .
docker run -d -v /absolute/path/redismoke.yml:/opt/redismoke/redismoke.yml redismoke
```

#### Use a virtualenv
You can run the script inside a simple virtualenv also:
```bash
virtualenv -p python3 .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 src/redismoke.py --config conf/config.yml
```

#### Use directly on RPM-based systems
Running the script directly on RPM-based systems is also an option, just substitute yum for dnf if necessary:
```bash
sudo yum install python3{,-redis,-PyYAML}
python3 src/redismoke.py --config conf/config.yml
```

## CLI Options
The script is pretty simple, and therefore takes only a small number of arguments:
* --config [file.yml]: Configuration file to use
* --solarwinds: Use the Solarwinds output and die as soon as the test completes
* --wait [n]: wait n seconds before actually performing the test

## Configuration
The configuration is written in YAML, and it is the sole argument that must be passed to the Python script. A commented
example exists in the `confs` directory, named `config.yml`, along with configuration files for Redis daemons used for
testing of the code itself.

## Testing
The code is currently being manually tested. Patches for automated testing are welcome. Run the following to test the
daemon with oneline output feature:
```bash
docker-compose build && docker-compose up
```

You may also run the following to test the SolarWinds output feature:
```bash
docker-compose -f docker-compose_solarwinds.yml build && docker-compose -f docker-compose_solarwinds.yml up
```

## Contributing
Just open a PR to this repository with your changes. Notice that there mustn't be any PEP8 violation in your code in
order for your change to be approved.

## License
This code is licensed under the MIT license.
