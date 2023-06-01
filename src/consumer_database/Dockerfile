FROM python:3.10-slim-bullseye


WORKDIR /usr/src/app/
COPY requirements.txt ./
COPY DigiCertGlobalRootCA.crt.pem ./truststore/
COPY solace_pubsubplus-.1.4.1_context_prop_-py36-none-any.whl ./
RUN pip install solace_pubsubplus-.1.4.1_context_prop_-py36-none-any.whl
RUN pip install --upgrade pip
RUN pip install  -r requirements.txt

COPY ./solace_telemetry_consumer_Database.py ./solace_telemetry_consumer_Database.py
ENTRYPOINT [  "python", "solace_telemetry_consumer_Database.py" ]