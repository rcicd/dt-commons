import io
import json
from abc import abstractmethod

import lcm
import copy
import time
import socket
import inspect
import logging
import threading
from hashlib import sha256
from ipaddress import IPv4Address
from typing import Callable, Union, Optional, Any
from dataclasses import dataclass
from genpy import Message as GenericROSMessage

from .dt_communication_msg_t import dt_communication_msg_t

logging.basicConfig()

HOSTNAME = socket.gethostname()
ANYBODY = "*"


@dataclass
class DTRawCommunicationMessageHeader(object):
    timestamp: int
    origin: str
    destination: Optional[str]
    txt: Optional[str]


class DTRawCommunicationGroup(object):

    IP_NETWORK = "239.255.0.0/20"
    DEFAULT_PORT = "7667"
    DEFAULT_CHANNEL = "/__default__"
    LCM_HEARTBEAT_HZ = 1

    def __init__(self, name: str, ttl: int = 1, loglevel: int = logging.WARNING):
        self._name = name
        self._ttl = ttl
        self._id = self._get_group_id()
        self._url = self._get_url(self.DEFAULT_PORT)
        self._is_shutdown = False
        self._logger = logging.getLogger(f'CommGroup[#{self._id}]')
        self._logger.setLevel(loglevel)
        self._publishers = set()
        self._subscribers = set()
        self._metadata = {}
        # create LCM handler
        self._logger.debug(f'Creating LCM handler on URL: `{self._url}`')
        self._lcm = lcm.LCM(self._url)
        self._mailman = threading.Thread(target=self._spin)
        self._mailman.start()

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def ttl(self):
        return self._ttl

    @property
    def handler(self):
        return self._lcm

    @property
    def is_shutdown(self):
        return self._is_shutdown

    @property
    def logger(self):
        return self._logger

    @property
    def metadata(self):
        return self._metadata

    def Subgroup(self, name: str, loglevel: int = None):
        if loglevel is None:
            loglevel = self._logger.level
        return DTRawCommunicationSubGroup(self, name, loglevel)

    def Publisher(self):
        pub = DTRawCommunicationGroupPublisher(self, self.DEFAULT_CHANNEL)
        self.add_publisher(pub)
        return pub

    def Subscriber(self, callback: Callable):
        sub = DTRawCommunicationGroupSubscriber(self, self.DEFAULT_CHANNEL, callback)
        self.add_subscriber(sub)
        return sub

    def add_publisher(self, publisher: 'DTRawCommunicationGroupPublisher'):
        self._publishers.add(publisher)

    def add_subscriber(self, subscriber: 'DTRawCommunicationGroupSubscriber'):
        self._subscribers.add(subscriber)

    def remove_publisher(self, publisher: 'DTRawCommunicationGroupPublisher'):
        self._publishers.remove(publisher)

    def remove_subscriber(self, subscriber: 'DTRawCommunicationGroupSubscriber'):
        self._subscribers.remove(subscriber)

    @staticmethod
    def encode(msg: bytes) -> bytes:
        return msg

    @staticmethod
    def decode(data: bytes, _: dict) -> bytes:
        return data

    def shutdown(self):
        # shutdown all publishers
        for pub in copy.copy(self._publishers):
            pub.shutdown()
        # shutdown all subscribers
        for sub in copy.copy(self._subscribers):
            sub.shutdown()
        # ---
        self._is_shutdown = True

    def _get_url(self, port):
        return f"udpm://{self._get_group_ip()}:{port}?ttl={self.ttl}"

    def _get_group_id(self):
        _, masklen = self.IP_NETWORK.split('/')
        range_len = 2 ** (32 - int(masklen))
        return int(sha256(self.name.encode('utf-8')).hexdigest(), 16) % range_len

    def _get_group_ip(self):
        base_ip, _ = self.IP_NETWORK.split('/')
        base_ip = IPv4Address(base_ip)
        ip_id = self._get_group_id()
        group_ip = base_ip + ip_id
        return group_ip

    def _spin(self):
        period = (1.0 / self.LCM_HEARTBEAT_HZ) * 1000
        try:
            while not self.is_shutdown:
                self._lcm.handle_timeout(period)
        except KeyboardInterrupt:
            pass


class DTRawCommunicationSubGroup(object):

    def __init__(self, group: DTRawCommunicationGroup, name: str, loglevel: int = logging.WARNING):
        self._group = group
        self._name = name.strip()
        self._topic = '/' + self._name.strip('/')
        self._is_shutdown = False
        self._logger = logging.getLogger(f'CommSubGroup[#{self._group.id}{self._topic}]')
        self._logger.setLevel(loglevel)
        self._publishers = set()
        self._subscribers = set()

    @property
    def name(self):
        return self._name

    @property
    def handler(self):
        return self._group.handler

    @property
    def is_shutdown(self):
        return self._is_shutdown

    @property
    def logger(self):
        return self._logger

    @property
    def metadata(self):
        return self._group.metadata

    def Publisher(self):
        pub = DTRawCommunicationGroupPublisher(self, self._topic)
        self.add_publisher(pub)
        return pub

    def Subscriber(self, callback: Callable):
        sub = DTRawCommunicationGroupSubscriber(self, self._topic, callback)
        self.add_subscriber(sub)
        return sub

    def add_publisher(self, publisher: 'DTRawCommunicationGroupPublisher'):
        self._publishers.add(publisher)
        self._group.add_publisher(publisher)

    def add_subscriber(self, subscriber: 'DTRawCommunicationGroupSubscriber'):
        self._subscribers.add(subscriber)
        self._group.add_subscriber(subscriber)

    def remove_publisher(self, publisher: 'DTRawCommunicationGroupPublisher'):
        self._publishers.remove(publisher)
        self._group.remove_publisher(publisher)

    def remove_subscriber(self, subscriber: 'DTRawCommunicationGroupSubscriber'):
        self._subscribers.remove(subscriber)
        self._group.remove_subscriber(subscriber)

    def encode(self, msg: bytes) -> bytes:
        return self._group.encode(msg)

    def decode(self, data: bytes, metadata: dict) -> bytes:
        return self._group.decode(data, metadata)

    def shutdown(self):
        # shutdown all publishers
        for pub in copy.copy(self._publishers):
            pub.shutdown()
        # shutdown all subscribers
        for sub in copy.copy(self._subscribers):
            sub.shutdown()
        # ---
        self._is_shutdown = True


class DTRawCommunicationGroupPublisher(object):

    def __init__(self, group: Union[DTRawCommunicationGroup, DTRawCommunicationSubGroup],
                 topic: str):
        self._group = group
        self._topic = topic

    def publish(self, data: Any, destination: str = None, txt: str = None):
        # let the group encode the data first
        data = self._group.encode(data)
        if data is None:
            return
        # check input (data)
        if not isinstance(data, bytes):
            raise ValueError(f'Field `data` must be of type `bytes`, '
                             f'given `{str(type(data))}` instead.')
        # check input (destination)
        if destination is not None and not isinstance(destination, str):
            raise ValueError(f'Field `destination` must be of type `str`, '
                             f'given `{str(type(destination))}` instead.')
        # check input (txt)
        if txt is not None and not isinstance(txt, str):
            raise ValueError(f'Field `txt` must be of type `str`, '
                             f'given `{str(type(txt))}` instead.')
        # create empty message
        msg = dt_communication_msg_t()
        # populate message
        msg.timestamp = time.time_ns() // 1000
        msg.group = self._group.name
        msg.origin = HOSTNAME
        msg.destination = (destination or ANYBODY).strip()
        msg.metadata = json.dumps(self._group.metadata)
        msg.txt = txt or ""
        msg.length = len(data)
        msg.payload = data
        # publish message
        msg = msg.encode()
        self._group.handler.publish(self._topic, msg)

    def shutdown(self):
        self._group.remove_publisher(self)


class DTRawCommunicationGroupSubscriber(object):

    def __init__(self, group: Union[DTRawCommunicationGroup, DTRawCommunicationSubGroup],
                 topic: str, callback: Callable):
        self._group = group
        self._topic = topic
        self._callback = callback
        self._subscription_handler = \
            self._group.handler.subscribe(self._topic, self.__inner_callback__)
        self._collisions = set()

    def shutdown(self):
        self._group.handler.unsubscribe(self._subscription_handler)
        self._group.remove_subscriber(self)

    def __inner_callback__(self, _, data):
        msg = None
        try:
            msg = dt_communication_msg_t.decode(data)
        except ValueError:
            pass
        # check if the message was decoded successfully
        if msg is None:
            self._group.logger.warning("Received invalid message. Ignoring it.")
            return
        # make sure there is no group collision here
        if msg.group != self._group.name:
            if msg.group not in self._collisions:
                self._group.logger.warning(
                    f"Collision detected between the groups `{msg.group}` "
                    f"and `{self._group.name}`. If you are the administrator, "
                    f"we suggest you increase the IP address pool dedicate to "
                    f"UDP Multicast.")
                self._collisions.add(msg.group)
            return
        # make sure we are the intended destination of this message
        if msg.destination not in [ANYBODY, HOSTNAME]:
            return
        # parse metadata
        metadata = json.loads(msg.metadata)
        # expose message metadata as a DTRawCommunicationMessageHeader object
        header = DTRawCommunicationMessageHeader(
            timestamp=msg.timestamp,
            origin=msg.origin,
            destination=msg.destination,
            txt=msg.txt or None
        )
        # let the group decode the data first
        payload = self._group.decode(msg.payload, metadata)
        if payload is None:
            return
        # call user callback
        self._callback(payload, header)


class _TypedCommunicationGroup(object):

    def __init__(self, msg_type: GenericROSMessage):
        # check msg_type
        if not inspect.isclass(msg_type):
            raise ValueError(f"Field `msg_type` expected to be of type `class`, "
                             f"got {msg_type.__class__.__name__} instead.")
        # ---
        self.MsgClass = msg_type

    @property
    @abstractmethod
    def logger(self) -> logging.Logger:
        pass

    def encode(self, msg: Any) -> Optional[bytes]:
        # make sure the message is in the right type
        if not isinstance(msg, self.MsgClass):
            self.logger.warning(f"Expected message of type `{self.MsgClass.__name__}`, "
                                 f"got `{msg.__class__.__name__}` instead.")
            return None
        # ---
        buff = io.BytesIO()
        msg.serialize(buff)
        return buff.getvalue()

    def decode(self, data: bytes, metadata: dict) -> Optional[GenericROSMessage]:
        # make sure the content type matches
        if metadata['msg_type'] != self.MsgClass.__name__:
            self.logger.warning(f"Expected message of type `{self.MsgClass.__name__}`, "
                                 f"got `{metadata['msg_type']}` instead.")
            return None
        # decode
        msg = self.MsgClass()
        msg.deserialize(data)
        return msg


class DTCommunicationGroup(_TypedCommunicationGroup, DTRawCommunicationGroup):

    def __init__(self, name: str, msg_type: GenericROSMessage, ttl: int = 1,
                 loglevel: int = logging.WARNING):
        # call super constructors
        _TypedCommunicationGroup.__init__(self, msg_type)
        DTRawCommunicationGroup.__init__(self, name, ttl, loglevel)
        self._metadata = {
            "msg_type": msg_type.__name__
        }

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    def Subgroup(self, name: str, msg_type: GenericROSMessage, loglevel: int = None):
        if loglevel is None:
            loglevel = self._logger.level
        return DTCommunicationSubGroup(self, name, msg_type, loglevel)


class DTCommunicationSubGroup(_TypedCommunicationGroup, DTRawCommunicationSubGroup):

    def __init__(self, group: DTCommunicationGroup, name: str, msg_type: GenericROSMessage,
                 loglevel: int = logging.WARNING):
        # call super constructors
        _TypedCommunicationGroup.__init__(self, msg_type)
        DTRawCommunicationSubGroup.__init__(self, group, name, loglevel)
        self._metadata = {
            "msg_type": msg_type.__name__
        }

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def metadata(self):
        return self._metadata
