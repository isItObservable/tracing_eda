FROM python:3.10-slim-bullseye


WORKDIR /usr/src/app/
COPY requirements.txt ./
COPY DigiCertGlobalRootCA.crt.pem ./truststore/

RUN pip install --upgrade pip
RUN pip install  -r requirements.txt

COPY ./solace_telemetry_consumer_Database.py ./solace_telemetry_consumer_Database.py
ENTRYPOINT [  "python", "solace_telemetry_consumer_Database.py" ]