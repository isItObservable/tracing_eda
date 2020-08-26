import time
from concurrent.futures.thread import ThreadPoolExecutor

from opentelemetry import trace
from opentelemetry.ext import jaeger
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from opentelemetry.trace import SpanContext
from pysolace.messaging.messaging_service import MessagingService
from pysolace.messaging.utils.resources.topic_subscription import TopicSubscription

"""CHANGE THESE VALUES"""
hostName = "tcp://mr-d8f4yze27kt.messaging.solace.cloud:55555"
vpnName = "cto-demo-virginia-azure"
solaceUserName = "solace-cloud-client"
solacePassword = "ceo79nfo0ndf94niceral94t2n"
"""END CHANGE THESE VALUES"""
inboundTopic = "opentelemetry/helloworld"

broker_props = {"solace.messaging.transport.host": hostName,
                "solace.messaging.service.vpn-name": vpnName,
                "solace.messaging.authentication.scheme.basic.user-name": solaceUserName,
                "solace.messaging.authentication.scheme.basic.password": solacePassword}
MAX_SLEEP = 120


def direct_message_handler(msg):
    """ Message receive callback """

    tracer = trace.get_tracer(__name__)
    trace_id = str(msg.get_property("trace_id"))
    span_id = str(msg.get_property("span_id"))
    print("parentSpan trace_id on receiver side:" + trace_id)
    print("parentSpan span_id on receiver side:" + span_id)
    propagated_context = SpanContext(int(trace_id), int(span_id), True)

    childSpan = tracer.start_span("RideUpdated receive", parent=propagated_context)
    topic = msg.get_destination_name()
    payload_as_string = msg.get_payload_as_string()
    print("\n" + f"CALLBACK: Message Received on Topic: {topic}.\n"
                 f"Message String: {payload_as_string} \n"
          )
    time.sleep(1)
    childSpan.end()


class DirectMessageConsumeServiceSampler:
    """
    class to show how to create a messaging service
    """

    @staticmethod
    def direct_message_consume(messaging_service: MessagingService, consumer_subscription: str):
        """ to publish str or byte array type message"""
        try:

            trace.set_tracer_provider(TracerProvider())

            jaeger_exporter = jaeger.JaegerSpanExporter(
                service_name="<Solace> REST Messaging call to Security Co",
                agent_host_name="localhost",
                agent_port=6831,
            )

            trace.get_tracer_provider().add_span_processor(
                BatchExportSpanProcessor(jaeger_exporter)
            )

            tracer = trace.get_tracer(__name__)
            topics = [TopicSubscription.of(inboundTopic)]

            direct_receive_service = messaging_service.create_direct_message_receiver_builder()
            direct_receive_service = direct_receive_service.with_subscriptions(topics).build()
            direct_receive_service.start()
            direct_receive_service.receive_async(direct_message_handler)
            print(f"Subscribed to: {consumer_subscription}")
            while True:
                global MAX_SLEEP
                if MAX_SLEEP <= 0:
                    break
                else:
                    MAX_SLEEP -= 1
                    time.sleep(1)
        finally:
            messaging_service.disconnect()

    @staticmethod
    def run():
        """
        :return:
        """
        service = MessagingService.builder().from_properties(broker_props).build()
        service.connect_async()
        consumer_subscription = "opentelemetry/helloworld"

        print("Execute Direct Consume - String")
        DirectMessageConsumeServiceSampler().direct_message_consume(service, consumer_subscription)


if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=1) as e:
        e.submit(DirectMessageConsumeServiceSampler.run)
