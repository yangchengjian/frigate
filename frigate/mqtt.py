import json
import logging
import threading

import paho.mqtt.client as mqtt

from frigate.config import MqttConfig, HttpConfig

logger = logging.getLogger(__name__)

def create_mqtt_client(config: MqttConfig, http_config: HttpConfig, amqp_publisher):
    print("create_mqtt_client")
    client = mqtt.Client(client_id=config.client_id)

    def on_connect(client, userdata, flags, rc):
        threading.current_thread().name = "mqtt"
        if rc != 0:
            if rc == 3:
                logger.error("MQTT Server unavailable")
            elif rc == 4:
                logger.error("MQTT Bad username or password")
            elif rc == 5:
                logger.error("MQTT Not authorized")
            else:
                logger.error("Unable to connect to MQTT: Connection refused. Error code: " + str(rc))
            
        print("MQTT connected")
        ## SUBSCRIBE
        client.subscribe(config.topic_prefix+'/rpc/request/+')
        ## PUBLISH
        # client.publish(config.topic_prefix+'/available', 'online', retain=True)  
        client.publish(config.topic_prefix+'/telemetry', '{\'status\': \'online\'}', retain=True) 
        ## SEND config to Recognize
        datas = json.dumps({"host": http_config.host, "port": http_config.port, "access_token": http_config.user})
        amqp_publisher.send_config_to_recognize(datas)

    def on_message(client, userdata, message):
        payload = json.loads(message.payload.decode())
        print(f"MQTT on_message : {message.topic}, {payload}")
        if payload['method'] == 'syncCommand':
            params = payload['params']
            params_json = json.loads(params)
            params_json['host'] = http_config.host
            params_json['port'] = http_config.port
            params_json['access_token'] = http_config.user
            amqp_publisher.send_sync_to_recognize(json.dumps(params_json))

    client.on_connect = on_connect
    client.on_message = on_message

    # client.will_set(config.topic_prefix+'/available', payload='offline', qos=1, retain=True)
    client.will_set(config.topic_prefix+'/telemetry', payload='{\'status\': \'offline\'}', qos=1, retain=True)

    if not config.user is None:
        client.username_pw_set(config.user, password=config.password)
    try:
        client.connect(config.host, config.port, 60)
    except Exception as e:
        logger.error(f"Unable to connect to MQTT server: {e}")
        raise
    client.loop_start()

    return client
