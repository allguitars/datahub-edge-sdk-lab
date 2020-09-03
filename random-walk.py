from wisepaasdatahubedgesdk.EdgeAgent import EdgeAgent
import wisepaasdatahubedgesdk.Common.Constants as constant
from wisepaasdatahubedgesdk.Model.Edge import EdgeAgentOptions, MQTTOptions, DCCSOptions, EdgeData, EdgeTag, EdgeStatus, EdgeDeviceStatus, EdgeConfig, NodeConfig, DeviceConfig, AnalogTagConfig, DiscreteTagConfig, TextTagConfig
from wisepaasdatahubedgesdk.Common.Utils import RepeatedTimer
import time
import random
import datetime

# **
# Datahub Connection Settings
# **
options = EdgeAgentOptions(
    # MQTT reconnect interval seconds
    reconnectInterval=1,
    # nodeId='bd7610ba-e787-4131-b23e-cfa452185e08',
    nodeId='71b52ec1-2e0f-437a-8f79-32be8d45ecff',
    # If type is Device, DeviceId must be filled
    deviceId='deviceId',
    # Choice your edge is Gateway or Device, Default is Gateway
    type=constant.EdgeType['Gateway'],
    heartbeat=60,                                       # Default is 60 seconds
    # Need to recover data or not when disconnected
    dataRecover=True,
    # Connection type (DCCS, MQTT), default is DCCS
    connectType=constant.ConnectType['DCCS'],
    MQTT=MQTTOptions(                                   # If connectType is MQTT, must fill this options
        hostName="127.0.0.1",
        port=1883,
        userName="admin",
        password="admin",
        # MQTT protocal (TCP, Websocket), default is TCP
        protocalType=constant.Protocol['TCP']
    ),
    DCCS=DCCSOptions(
        apiUrl="https://api-dccs-ensaas.sa.wise-paas.com/",         # DCCS API Url
        # credentialKey="c49fe0af415c5b79d6ab10d1b13acfp1"  # Creadential key
        credentialKey="fce6538e82e18a85a0560315652e03ti"  # Creadential key
    )
)

edge_agent = EdgeAgent(options=options)


def generate_data(data, device_id, tag_name, value):
    tag = EdgeTag(device_id, tag_name, value)
    data.tagList.append(tag)


def send_data(data):
    edge_agent.sendData(data=data)


def handler_on_connected(agent, isConnected):
    # Connected: when EdgeAgent is connected to IoTHub.
    print("Connected successfully")

    # TODO: Put data sending here


def handler_on_disconnected(agent, isDisconnected):
    # Disconnected: when EdgeAgent is disconnected to IoTHub.
    print("Disconnected")


def handler_on_message(agent, messageReceivedEventArgs):
    '''
    MessageReceived: when EdgeAgent receives MQTT message FROM CLOUD. The message type is as follows:
        - WriteValue: Change tag value from cloud.
        - WriteConfig: Change config from cloud.
        - TimeSync: Returns the current time from cloud.
        - ConfigAck: The response of uploading config from edge to cloud.
    '''
    # messageReceivedEventArgs format: Model.Event.MessageReceivedEventArgs
    type = messageReceivedEventArgs.type
    message = messageReceivedEventArgs.message
    if type == constant.MessageType['WriteValue']:
        # message format: Model.Edge.WriteValueCommand
        for device in message.deviceList:
            print(f'deviceId: {device.id}')
            for tag in device.tagList:
                print(f'tagName: {tag.name}, Value: {tag.value}')
    elif type == constant.MessageType['WriteConfig']:
        print('WriteConfig')
    elif type == constant.MessageType['TimeSync']:
        # message format: Model.Edge.TimeSyncCommand
        print(str(message.UTCTime))
    elif type == constant.MessageType['ConfigAck']:
        # message format: Model.Edge.ConfigAck
        print(f'Upload Config Result: {str(message.result)}')


# Bind event handlers
edge_agent.on_connected = handler_on_connected
edge_agent.on_disconnected = handler_on_disconnected
edge_agent.on_message = handler_on_message

# Simulate random walk


def random_walk(previous, lower, upper):
    up = 3
    down = -3
    toss = random.randint(0, 100)
    move = up if toss > 50 else down
    value = previous + move

    while value < lower or value > upper:
        toss = random.randint(0, 100)
        move = up if toss > 50 else down
        value = previous + move

    print(value)
    return value


# Connect to the cloud
edge_agent.connect()
time.sleep(2)

# Initial value
random_tag1 = random.randint(0, 300)

# Sending data
while True:
    data = EdgeData()
    # Append the new tag value to the data
    # generate_data(data, 'Device1', 'ATag1', 200)
    # generate_data(data, 'Device1', 'BTag1', 300)
    # generate_data(data, 'Device1', 'DTag1', random.randint(0, 1))
    # generate_data(data, 'Device1', 'OEETag1', random.randint(0, 4))
    # generate_data(data, 'Device1', 'RandomTag1', random.randint(0, 300))
    random_tag1 = random_walk(random_tag1, 0, 300)
    generate_data(data, 'Device1', 'RandomTag1', random_tag1)

    # data.timestamp = datetime.datetime.now()

    send_data(data)
    time.sleep(1)

# Drop the connection
edge_agent.disconnect()
