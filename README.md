# Is it Observable
<p align="center"><img src="/image/logo.png" width="40%" alt="Is It observable Logo" /></p>

## Episode : Building Traces for Event Driven Architecture
This repository contains the files utilized during the tutorial presented in the dedicated IsItObservable episode related to Traces for Event Driven Architecture.
<p align="center"><img src="/image/opentelemetry-stacked-color.png" width="40%" alt="OpenTelemery Logo" /></p>
using Solace PubSub:
<p align="center"><img src="/image/solace.png" width="40%" alt="OpenTelemery Logo" /></p>

What you will learn :
* How to use  [Span Links](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/overview.md#links-between-spans)

This repository showcase the usage of OpenTelemetry  with :
* The modified version of Solace trace tutorial
* The OpenTelemetry Operator
* Dynatrace
* Solace 


We will send all Telemetry data produced  from  python application to Dynatrace.
We will have 1 producer sending messages to Solace Pub/Sub and 2 consumers. 

Let's see 2 way of tracing this type of application.

## Prerequisite
The following tools need to be install on your machine :
- jq
- kubectl
- git
- gcloud ( if you are using GKE)
- Helm


## Deployment Steps in GCP

You will first need a Kubernetes cluster with 2 Nodes.
You can either deploy on Minikube or K3s or follow the instructions to create GKE cluster:
### 1.Create a Google Cloud Platform Project
```shell
PROJECT_ID="<your-project-id>"
gcloud services enable container.googleapis.com --project ${PROJECT_ID}
gcloud services enable monitoring.googleapis.com \
    cloudtrace.googleapis.com \
    clouddebugger.googleapis.com \
    cloudprofiler.googleapis.com \
    --project ${PROJECT_ID}
```
### 2.Create a GKE cluster
```shell
ZONE=europe-west3-a
NAME=isitobservable-eda
gcloud container clusters create "${NAME}" --zone ${ZONE} --machine-type=e2-standard-2 --num-nodes=2
```


## Getting started
### Dynatrace Tenant
#### 1. Dynatrace Tenant - start a trial
If you don't have any Dyntrace tenant , then i suggest to create a trial using the following link : [Dynatrace Trial](https://bit.ly/3KxWDvY)
Once you have your Tenant save the Dynatrace tenant url in the variable `DT_TENANT_URL` (for example : https://dedededfrf.live.dynatrace.com)
```
DT_TENANT_URL=<YOUR TENANT Host>
```

#### 2. Create the Dynatrace API Tokens
Create a Dynatrace token with the following scope ( left menu Acces Token):
* ingest metrics
* ingest OpenTelemetry traces
* ingest logs
<p align="center"><img src="/image/data_ingest.png" width="40%" alt="data token" /></p>
Save the value of the token . We will use it later to store in a k8S secret

```
DATA_INGEST_TOKEN=<YOUR TOKEN VALUE>
```

### Solace Service
#### 1. Solace Service - start a trial
If you don't have any Solace account , then i suggest to create a trial using the following link : [Solace Account ](https://console.solace.cloud/login/new-account?_gl=1*1wrqey0*_ga*Njk0OTM5NjU3LjE2Nzk1ODcwNzc.*_ga_XZ3NWMM83E*MTY4MDg3MTg1Mi42LjEuMTY4MDg3MTg1OC4wLjAuMA..)
Once you have your Solace Accout, login and go to Cluster Manager
<p align="center"><img src="/image/clustermanager.png" width="40%" alt="Cluster Manager" /></p>

Click on Create a new Service, and specify :
- the name
- the Cloud location ( in my case i'm using the same reagion as my GKE cluster)

And click on Create Service.

Once the service is created click , on the connect tab and expand Solace Messaging to get the Connection details required for this tutorial :
<p align="center"><img src="/image/connect.png" width="40%" alt="Solace connect" /></p>

```
SOLACE_HOST=<YOUR Solace Host>
SOLACE_VPN=<YOUR Solace VPN>
SOLACE_USERNAME=<YOUR solace Username>
SOLACE_PASSWORD=<Your Solace Password>
```
#### 2. Download the trusted store

From the Connect tab, download the TrustStore ( .pem) and name it: `DigiCertGlobalRootCA.crt.pem`
<p align="center"><img src="/image/trustore.png" width="40%" alt="Solace connect" /></p>

### 3.Clone the Github Repository
```shell
https://github.com/isItObservable/tracing_eda
cd tracing_eda
```
Copy your certificate  `DigiCertGlobalRootCA.crt.pem` in:
- `src/consumer_database`
- `src/consumer_rest`
- `src/publisher`

### 5.Configure the Telemetry Profile in Solace

#### Create the Telemtry Profile 

Within the default message VPN, navigate to Telemetry and select Create Telemetry Profile
<p align="center"><img src="/image/telemetry.png" width="40%" alt="Telemery" /></p>

Name the Telemetry profile  and click Apply. We'll come back to this page later to update additional settings.
<p align="center"><img src="/image/26508580cb4d05a5.pngtelemetry _profile_name.png" width="40%" alt="Telemery profile name" /></p>

Next, we need to enable the receiver. From the trace Telemetry Profile page, select Receiver Connect ACLs and update the Client Connect Default Action to AllowTip: Double-click the input to enable edit mode
<p align="center"><img src="/image/receiver_acl.png" width="40%" alt="Telemery profile acl " /></p>

After applying the ACL, edit the trace Telemetry Profile page to enable the Reciever and Trace settings.
<p align="center"><img src="/image/acl_receiver_enable.png" alt="Telemery profile acl enabled " /></p>

Finally, let's create a Trace Filter and add a subscription that will attract all topic messages (using the > subscription)
<p align="center"><img src="/image/trace_filter_.png" alt="Telemery profile trace filter " /></p>

Create the filter with name default. Be sure to enable before clicking Apply.
<p align="center"><img src="/image/subscription.png" alt="Telemery profile subscription " /></p>

Add the `>` subscription

#### Create OpenTelmetry Collector Client UserName

Within the default message VPN. Navigate to Access Control -> Client Usernames and add a new Client Username.
<p align="center"><img src="/image/elemetry_username1.png" alt="Telemery profile username " /></p>


Create the new client username with a name of trace. Apply the following settings to the trace client username:
* Enable the client username
* Change the password to trace
* Assign #telemetry-trace for both the Client Profile and ACL Profile 
<p align="center"><img src="/image/crete_user_telemtry.png" alt="Telemery profile username password " /></p>

Note your telemetry user & password :
```
SOLACE_TELEMETRY_USER=<YOUR SOLACE telemetry user>
SOLACE_TELEMETRY_PASSWORD=<Your Solace telemetry password>
```

#### Get the telemetry queue name

In the Solace, click on Queues.
You should see a queue create from our Telemetry Profile.
<p align="center"><img src="/image/queeu_name.png" alt="Telemery profile username password " /></p>

Note the name of your telemetry queue 
```
SOLACE_TELMETRY_QUEUE=<YOUR SOLACE TElemetry queue name>
```
#### Get AMQP url of our telemetry queue 
In cluster management UI of Solace, click on "Connect", expend the AMQP section.
It will give us the connection details using the amqp protocol:
<p align="center"><img src="/image/connection_detail.png" alt="Telemery profile username password " /></p>

Note the Url without amqp://
```
SOLACE_TELEMETRY_AMQP_URL=<YOUR Solace AMQP URL>
```
### 4.Deploy most of the components
The application will deploy the openTelemtry Solace Tutorial :
```shell
chmod 777 deployment.sh
./deployment.sh  --solaceusername "${SOLACE_USERNAME}" --dthost "${DT_TENANT_URL}" --dttoken "${DATA_INGEST_TOKEN}" --solacepassword "${SOLACE_PASSWORD}" --solacehost "${SOLACE_HOST}"  --solacevpn "${SOLACE_VPN}" --solaceamqpurl "${SOLACE_TELEMETRY_AMQP_URL}" --solacetelemetryqueue "${SOLACE_TELMETRY_QUEUE}" --solacetelemetryuser "${SOLACE_TELEMETRY_USER}" --solacetelemetrypwd "${SOLACE_TELEMETRY_PASSWORD}"
```
### 5.Look at the produced traces 

### 6.Let's look at collector pipeline


### 6. Let's now use SpanLinks

