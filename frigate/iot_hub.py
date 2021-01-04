import asyncio
from azure.iot.device import IoTHubModuleClient, Message


class IoTHubClient():
    def __init__(self):
        try:
            # The client object is used to interact with your Azure IoT hub.
            module_client = IoTHubModuleClient.create_from_edge_environment()
            # connect the client.
            module_client.connect()

            # define behavior for receiving an input message on input1
            def input1_listener(module_client):
                while True:
                    # blocking call
                    input_message = module_client.receive_message_on_input("input1")
                    process_input_message(input_message)
        
            # Schedule task for C2D Listener
            listeners = asyncio.gather(input1_listener(module_client))

        except Exception as e:
            print("Unexpected error %s " % e)
            raise

        self.listeners = listeners
        self.module_client = module_client

    def send_to_hub(self, message, output_name):
        self.module_client.send_message_to_output(message, output_name)

    def stop(self):
        # Cancel listening
        self.listeners.cancel()
        self.module_client.disconnect()

def process_input_message(input_message):
    print("the data in the message received on input1 was ")
    print(input_message.data)
    print("custom properties are")
    print(input_message.custom_properties)
    print("forwarding mesage to output1")
        
