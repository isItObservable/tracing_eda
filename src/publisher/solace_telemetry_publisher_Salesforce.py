import os

""" Run this file then run how_to_publish_message.py so that it can listen to incoming messages """
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import SpanKind,use_span
from solace.messaging.messaging_service import MessagingService
from solace.messaging.resources.topic import Topic
from solace.messaging.config.transport_security_strategy import TLS
from solace.messaging.config.authentication_strategy import  BasicUserNamePassword, ClientCertificateAuthentication

def direct_message_publish(messaging_service: MessagingService, topic, message):
    try:
        # Create a direct message publish service and start it
        direct_publish_service = messaging_service.create_direct_message_publisher_builder().build()
        direct_publish_service.start_async()
        # Publish the message!
        direct_publish_service.publish(destination=topic, message=message)
    finally:
        direct_publish_service.terminate()

outboundTopic = "opentelemetry/helloworld"

broker_props = {"solace.messaging.transport.host": os.environ['SOLACE_HOST'],
                "solace.messaging.service.vpn-name": os.environ['SOLACE_VPN'],
                "solace.messaging.authentication.scheme.basic.username": os.environ['SOLACE_USERNAME'],
                "solace.messaging.authentication.scheme.basic.password": os.environ['SOLACE_PASSWORD'],
               "solace.messaging.tls.trust-store-path": "/usr/src/app/truststore/DigiCertGlobalRootCA.crt.pem"}

trace.set_tracer_provider(TracerProvider())
otlp_exporter = OTLPSpanExporter( insecure=True)


trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)

tracer = trace.get_tracer(__name__)
# THIS IS PER https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/semantic_conventions/messaging.md
parentSpan = tracer.start_span(
    "RideUpdated send",
    kind=SpanKind.PRODUCER,
    attributes={
        "messaging.system": "solace",
        "messaging.destination": outboundTopic,
        "messaging.destination-kind": "topic",
        "messaging.protocol": "jcsmp",
        "messaging.protocol_version": "1.0",
        "messaging.url": os.environ['SOLACE_HOST']}
)
with use_span(parentSpan,end_on_exit=True):
    with tracer.start_as_current_span("Connect pub/sub") as child :
        transport_security = TLS.create() \
          .with_certificate_validation(False, validate_server_name=False, trust_store_file_path="/usr/src/app/truststore")

        messaging_service = MessagingService.builder().from_properties(broker_props)\
                            .with_transport_security_strategy(transport_security)\
                            .with_authentication_strategy(BasicUserNamePassword.of(os.environ['SOLACE_USERNAME'], os.environ['SOLACE_PASSWORD']))\
                            .build()
        messaging_service.connect()

    with tracer.start_as_current_span("Send message") as sendspan :
        trace_id = sendspan.get_span_context().trace_id
        span_id = sendspan.get_span_context().span_id
        print("parentSpan trace_id  on sender side:" + str(trace_id))
        print("parentSpan span_id  on sender side:" + str(span_id))

        destination_name = Topic.of(outboundTopic)

        outbound_msg = messaging_service.message_builder() \
            .with_trace_id(bytearray(trace_id.to_bytes(16, 'big'))) \
            .with_span_id(bytearray(span_id.to_bytes(8, 'big'))) \
            .build("Hello World! This is a message published from Python!")

        direct_message_publish(messaging_service, destination_name, outbound_msg)


