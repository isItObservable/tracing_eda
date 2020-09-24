# nycmoderntaxi

## Env setup
1. Install python 3.7
1. Setup python virtual environment `python3 -m venv venv`

## Install Dependencies 
1. `pip install -r requirements.txt`

## How to run

### REST consumer intro
1. navigate to opentelemtry-intro directory
1. Execute `SOL_HOST=<host_name> SOL_VPN=<vpn_name> SOL_USERNAME=<username> SOL_PASSWORD=<password> python solace_telemetry_consumer_REST.py.py`

### Database consumer intro
1. navigate to opentelemtry-intro directory
1. Execute `SOL_HOST=<host_name> SOL_VPN=<vpn_name> SOL_USERNAME=<username> SOL_PASSWORD=<password> python solace_telemetry_consumer_Database.py.py`

### Publisher intro
1. navigate to opentelemtry-intro directory
1. Execute `SOL_HOST=<host_name> SOL_VPN=<vpn_name> SOL_USERNAME=<username> SOL_PASSWORD=<password> python solace_telemetry_publisher_Salesforce.py`

## Notes
1. Codelab associated with this repo can be found on [Solace Codelabs](https://codelabs.solace.dev/codelabs/opentelemetry-intro)
1. More information on the Solace Python API can be found on the [Solace Community](https://solace.community/discussion/336/python-whos-in-for-a-real-treat)
