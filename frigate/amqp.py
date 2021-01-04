#!/usr/bin/env python
import json
import logging
import pika

from frigate.http import send_to_server

logger = logging.getLogger(__name__)

def create_amqp_client():
    # connection = pika.BlockingConnection(
    #    pika.ConnectionParameters(host='RabbitmqModule'))
    params = pika.ConnectionParameters(host='RabbitmqModule', heartbeat=600,
                                       blocked_connection_timeout=300)
    connection = pika.BlockingConnection(params)

    channel = connection.channel()
    channel.queue_declare(queue='from_recognize_frame')

    # def callback(ch, method, properties, body):
    #     print(f"body : {body.decode()}")
    #     # send_message(connection, body)
    def callback_from_recognize(ch, method, properties, body):
        print(f"AMQP callback_from_recognize method: {method}, properties: {properties}")
        body_json = json.loads(body.decode())
        print(f"AMQP callback_from_recognize recognize_result : {body_json['recognize_result']}")
        ## POST recognize_result to server
        send_to_server(body)

    print('AMQP [*] Waiting for messages.')
    channel.basic_consume(queue='from_recognize_frame',
                          on_message_callback=callback_from_recognize, auto_ack=True)
    # channel.start_consuming()
    return connection


def send_frame_to_recognize(connection, message):
    print(f"AMQP send_frame_to_recognize from_frigate_frame")
    send_message(connection, '', 'from_frigate_frame', 'from_frigate_frame', message)

def send_message(connection, exchange, routing_key, queue, message):
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        )
    )

def process_message(connection):
    connection.process_data_events(time_limit=0)


def stop(connection):
    connection.close()
