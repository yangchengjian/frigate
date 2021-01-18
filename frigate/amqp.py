#!/usr/bin/env python
import json
import logging
import pika

from frigate.http import send_to_server

logger = logging.getLogger(__name__)


class Publisher:
    def __init__(self, host, username = '', password = ''):
        self.host = host
        self.username = username
        self.password = password
        self.connection = None
        
    def connect(self):
        try:
            self.params = pika.ConnectionParameters(host=self.host, heartbeat=600,
                                       blocked_connection_timeout=300)
            self.connection = pika.BlockingConnection(self.params)

            channel = self.connection.channel()
            channel.queue_declare(queue='from_recognize_frame')

            def callback_from_recognize(ch, method, properties, body):
                print(f"AMQP callback_from_recognize method: {method}, properties: {properties}")
                body_json = json.loads(body.decode())
                print(f"AMQP callback_from_recognize recognize_result : {body_json['recognize_result']}")
                ## POST recognize_result to server
                send_to_server(body)

            print('AMQP [*] Waiting for messages.')
            channel.basic_consume(queue='from_recognize_frame',
                          on_message_callback=callback_from_recognize, auto_ack=True)
        except Exception as e:
            print(f"AMQP connect except error: {e}")

    def send_config_to_recognize(self, message):
        print(f"AMQP send_config_to_recognize from_frigate_config")
        self.send_message('', 'from_frigate_config', 'from_frigate_config', message)

    def send_frame_to_recognize(self, message):
        print(f"AMQP send_frame_to_recognize from_frigate_frame")
        self.send_message('', 'from_frigate_frame', 'from_frigate_frame', message)

    def send_sync_to_recognize(self, message):
        print(f"AMQP send_sync_to_recognize from_frigate_sync")
        self.send_message('', 'from_frigate_sync', 'from_frigate_sync', message)

    def send_message(self, exchange, routing_key, queue, message):
        try:
            channel = self.connection.channel()
            channel.queue_declare(queue=queue)
            channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                )
            )
        except Exception as e:
            print(f"AMQP send_message except error: {e}")
            self.connect()


    def process_message(self):
        self.connection.process_data_events(time_limit=0)


    def stop(self):
        self.connection.close()
