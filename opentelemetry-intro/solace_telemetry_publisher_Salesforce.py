import os

""" Run this file then run how_to_publish_message.py so that it can listen to incoming messages """
from opentelemetry import trace
from opentelemetry.ext import jaeger
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from opentelemetry.trace import SpanKind
from pysolace.messaging.messaging_service import MessagingService
from pysolace.messaging.utils.topic import Topic

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

broker_props = {"solace.messaging.transport.host": os.environ['SOL_HOST'],
                "solace.messaging.service.vpn-name": os.environ['SOL_VPN'],
                "solace.messaging.authentication.scheme.basic.user-name": os.environ['SOL_USERNAME'],
                "solace.messaging.authentication.scheme.basic.password": os.environ['SOL_PASSWORD']}

trace.set_tracer_provider(TracerProvider())
jaeger_exporter = jaeger.JaegerSpanExporter(
    service_name="<Boomi> Listen for Salesforce Platform Account, publish Solace DriverUpserted",
    agent_host_name="localhost",
    agent_port=6831,
)

trace.get_tracer_provider().add_span_processor(
    BatchExportSpanProcessor(jaeger_exporter)
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
        "messaging.url": os.environ['SOL_HOST']}
)

messaging_service = MessagingService.builder().from_properties(broker_props).build()
messaging_service.connect_async()


trace_id = parentSpan.get_context().trace_id
span_id = parentSpan.get_context().span_id
print("parentSpan trace_id  on sender side:" + str(trace_id))
print("parentSpan span_id  on sender side:" + str(span_id))

destination_name = Topic.of(outboundTopic)

outbound_msg = messaging_service.message_builder() \
    .with_property("trace_id", str(trace_id)) \
    .with_property("span_id", str(span_id)) \
    .build("Hello World! This is a message published from Python!")

direct_message_publish(messaging_service, destination_name, outbound_msg)

parentSpan.end()
