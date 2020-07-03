from wisepaasdatahubedgesdk.EdgeAgent import EdgeAgent
import wisepaasdatahubedgesdk.Common.Constants as constant
from wisepaasdatahubedgesdk.Model.Edge import EdgeAgentOptions, MQTTOptions, DCCSOptions, EdgeData, EdgeTag, EdgeStatus, EdgeDeviceStatus, EdgeConfig, NodeConfig, DeviceConfig, AnalogTagConfig, DiscreteTagConfig, TextTagConfig
from wisepaasdatahubedgesdk.Common.Utils import RepeatedTimer
import time

# **
# Datahub Connection Settings
# **
options = EdgeAgentOptions(
    # MQTT reconnect interval seconds
    reconnectInterval=1,
    nodeId='bd7610ba-e787-4131-b23e-cfa452185e08',      # Get from portal
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
        credentialKey="45bab44e7971402abd179103aec8e5al"  # Creadential key
    )
)

edge_agent = EdgeAgent(options=options)


def handler_on_connected(agent, isConnected):
    # Connected: when EdgeAgent is connected to IoTHub.
    print("Connected successfully")


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

# **
# * Uploads Node/Device/Tag Configs with Action Type (Create/Update/Delete).
# **
config = EdgeConfig()  # Create an EdgeConfig object

# Node config setting
nodeConfig = NodeConfig(nodeType=constant.EdgeType['Gateway'])
config.node = nodeConfig

# Device config setting
deviceConfig = DeviceConfig(
    id='Device1',
    name='Device1',
    deviceType='Smart Device',
    description='Device1'
)

config.node.deviceList.append(deviceConfig)

# ****** Analog tag config settings ******

analogTag = AnalogTagConfig(
    name='ATag1',
    description='ATag 1',
    readOnly=False,
    arraySize=0,
    spanHigh=1000,
    spanLow=0,
    engineerUnit='',
    integerDisplayFormat=4,
    fractionDisplayFormat=2
)

config.node.deviceList[0].analogTagList.append(analogTag)

analogTag = AnalogTagConfig(
    name='BTag1',
    description='BTag 1',
    readOnly=False,
    arraySize=0,
    spanHigh=1000,
    spanLow=0,
    engineerUnit='',
    integerDisplayFormat=4,
    fractionDisplayFormat=2
)

config.node.deviceList[0].analogTagList.append(analogTag)

analogTag = AnalogTagConfig(
    name='OEETag1',
    description='OEETag 1',
    readOnly=False,
    arraySize=0,
    spanHigh=1000,
    spanLow=0,
    engineerUnit='',
    integerDisplayFormat=4,
    fractionDisplayFormat=2
)

config.node.deviceList[0].analogTagList.append(analogTag)

analogTag = AnalogTagConfig(
    name='RandomTag1',
    description='RandomTag 1',
    readOnly=False,
    arraySize=0,
    spanHigh=1000,
    spanLow=0,
    engineerUnit='',
    integerDisplayFormat=4,
    fractionDisplayFormat=2
)

config.node.deviceList[0].analogTagList.append(analogTag)

# ****** Discrete tag config settings ******

discreteTag = DiscreteTagConfig(
    name='DTag1',
    description='DTag 1',
    readOnly=False,
    arraySize=0,
    state0='1',
    state1='0',
    state2=None,
    state3=None,
    state4=None,
    state5=None,
    state6=None,
    state7=None
)

config.node.deviceList[0].discreteTagList.append(discreteTag)

# Text Tag config setting
# textTag = TextTagConfig(
#     name='TextTag',
#     description='Text Tag',
#     readOnly=False,
#     arraySize=0
# )

# config.node.deviceList[0].textTagList.append(textTag)

# Connect to the cloud
edge_agent.connect()
time.sleep(2)

# ### Apply all settings (Create/Update/Delete)
result = edge_agent.uploadConfig(
    constant.ActionType['Create'], edgeConfig=config)

# Drop the connection
edge_agent.disconnect()
