# nycmoderntaxi

## Env setup
1. [Install Python 3.7](https://www.python.org/downloads/)
1. [Optional] Install virtualenv `python -m pip install --user virtualenv`
1. Clone this repository
1. [Optional] Setup python virtual environment `python -m venv venv`
1. [Optional] Activate virtual environment: `source venv/bin/activate`  
    1.1 MacOS: `source venv/bin/activate`   
    1.2 Windows: `source venv/Scripts/activate`

## Install Dependencies 
1. `pip install -r requirements.txt`

## Install Solace Python API 
1. Install the API from the [Solace Community](https://solace.community/discussion/336/python-whos-in-for-a-real-treat)
1. From this directory execute `pip install <path_to_API_wheel>`


## How to run

### REST consumer intro
1. navigate to opentelemetry-intro directory
1. Execute `SOL_HOST=<host_name> SOL_VPN=<vpn_name> SOL_USERNAME=<username> SOL_PASSWORD=<password> python solace_telemetry_consumer_REST.py.py`

### Database consumer intro
1. navigate to opentelemetry-intro directory
1. Execute `SOL_HOST=<host_name> SOL_VPN=<vpn_name> SOL_USERNAME=<username> SOL_PASSWORD=<password> python solace_telemetry_consumer_Database.py`

### Publisher intro
1. navigate to opentelemetry-intro directory
1. Execute `SOL_HOST=<host_name> SOL_VPN=<vpn_name> SOL_USERNAME=<username> SOL_PASSWORD=<password> python solace_telemetry_publisher_Salesforce.py`

## Notes
1. Codelab associated with this repo can be found on [Solace Codelabs](https://codelabs.solace.dev/codelabs/opentelemetry-intro)
1. More information on the Solace Python API can be found on the [Solace Community](https://solace.community/discussion/336/python-whos-in-for-a-real-treat)
1. If the Solace API is still not public, you can install it from the community link and from this directory execute `pip install <path_to_API_wheel>`