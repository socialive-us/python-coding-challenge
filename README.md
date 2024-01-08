### python-coding-challenge

This project is used for interviews.

### Dependencies

* Python3
* pip3
* virtualenv

#### Linux (Ubuntu)

```
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
```

#### MacOS

#### MacOS

```
brew update
# First time python installation
brew install python
# Or, if python is already installed, but not Python3
brew upgrade python
```

### Activate the Virtual Environment

First time:
```
mkdir .venv
python3 -m venv .venv
source .venv/bin/activate
```

Each following time:
```
source .venv/bin/activate
export PATH=${PATH}:${PWD}/node_modules/.bin
```

### Run Automated Tests

Activate the virtual environment, then

```
cd src/lambdas
./run_tests.sh
```
