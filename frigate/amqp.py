#!/usr/bin/env python
import pika


def create_amqp_client(callback):
    # connection = pika.BlockingConnection(
    #    pika.ConnectionParameters(host='RabbitmqModule'))
    params = pika.ConnectionParameters(host='RabbitmqModule', heartbeat=60,
                                       blocked_connection_timeout=300)
    connection = pika.BlockingConnection(params)

    channel = connection.channel()
    channel.queue_declare(queue='from_recognize_frame')

    # def callback(ch, method, properties, body):
    #     print(f"body : {body.decode()}")
    #     # send_message(connection, body)

    print(' [*] Waiting for messages.')
    channel.basic_consume(queue='from_recognize_frame',
                          on_message_callback=callback, auto_ack=True)
    # channel.start_consuming()
    return connection


def send_message(connection, message):
    channel = connection.channel()
    channel.queue_declare(queue='from_frigate_frame')
    channel.basic_publish(
        exchange='',
        routing_key='from_frigate_frame',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        )
    )


def process_message(connection):
    connection.process_data_events(time_limit=0)


def stop(connection):
    connection.close()
