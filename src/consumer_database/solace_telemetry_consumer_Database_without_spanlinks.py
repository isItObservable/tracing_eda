import os
import time

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.context import attach, detach
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import SpanContext,SpanKind,TraceFlags,set_span_in_context,use_span,NonRecordingSpan
from solace.messaging.messaging_service import MessagingService
from solace.messaging.resources.topic_subscription import TopicSubscription
from solace.messaging.receiver.message_receiver import MessageHandler
from solace.messaging.config.transport_security_strategy import TLS
from solace.messaging.config.authentication_strategy import ClientCertificateAuthentication , BasicUserNamePassword
import random
# Callback function to handle received messages
class MessageHandlerImpl(MessageHandler):
    def on_message(self, message: 'InboundMessage'):
        tracer = trace.get_tracer(__name__)
        traceid = int.from_bytes(message.get_trace_id(), 'big')
        spanid = int.from_bytes(message.get_span_id(), 'big')

        propagated_context = SpanContext(trace_id =int(traceid),span_id =int(spanid), is_remote=True,trace_flags=TraceFlags(0x01))
        ctx =  set_span_in_context(NonRecordingSpan(propagated_context))

        childSpan = tracer.start_span("RideUpdated receive for database",context=ctx, kind=trace.SpanKind.CONSUMER)
        with use_span(childSpan,end_on_exit=True):
            topic = message.get_destination_name()
            payload_str = message.get_payload_as_string()

            with tracer.start_as_current_span("Parse message") as child:
              self.parseMessage(payload_str)

            print("\n" + f"DATABASE CALLBACK: Message Received on Topic: {topic}.\n"
                         f"{int(time.time())}: {payload_str} \n")

            time.sleep(random.uniform(0.6, 1.9))

            with tracer.start_as_current_span("Store Data") as childs:
                self.sendrequest(topic)



    def parseMessage(self,payload: str):
        for letter in payload:
            print(letter)
            time.sleep(random.uniform(0.4, 2.9))


    def sendrequest(self,topic: str):
        for letter in topic:
            print(letter)
            time.sleep(random.uniform(0.3, 2.9))

def direct_message_consume(messaging_service: MessagingService, topic_subscription: str):
    try:
        topics = [TopicSubscription.of(topic_subscription)]
        # Create a direct message consumer service with the topic subscription and start it
        direct_receive_service = messaging_service \
                                .create_direct_message_receiver_builder() \
                                .with_subscriptions(topics) \
                                .build()
        direct_receive_service.start()

        # Register a callback message handler
        direct_receive_service.receive_async(MessageHandlerImpl())
        print(f"Subscribed to: {topic_subscription}")
        # Infinite loop until Keyboard interrupt is received
        try: 
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print('\nDisconnecting Messaging Service')
    finally:
        messaging_service.disconnect()
        direct_receive_service.terminate()

inboundTopic = "opentelemetry/helloworld"

broker_props = {"solace.messaging.transport.host": os.environ['SOLACE_HOST'],
                "solace.messaging.service.vpn-name": os.environ['SOLACE_VPN'],
                "solace.messaging.authentication.scheme.basic.username": os.environ['SOLACE_USERNAME'],
                "solace.messaging.authentication.scheme.basic.password": os.environ['SOLACE_PASSWORD']}
transport_security = TLS.create() \
  .with_certificate_validation(False, validate_server_name=False, trust_store_file_path="/usr/src/app/truststore")


messaging_service = MessagingService.builder().from_properties(broker_props)\
                    .with_transport_security_strategy(transport_security)\
                    .with_authentication_strategy(BasicUserNamePassword.of(os.environ['SOLACE_USERNAME'], os.environ['SOLACE_PASSWORD']))\
                    .build()
messaging_service.connect()


trace.set_tracer_provider(TracerProvider())
otlp_exporter = OTLPSpanExporter( insecure=True)

trace.get_tracer_provider().add_span_processor(
       BatchSpanProcessor(otlp_exporter)
)

direct_message_consume(messaging_service, inboundTopic)