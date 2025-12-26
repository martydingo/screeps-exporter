from screepsapi import Socket
import logging, logging.handlers
from rfc5424logging import Rfc5424SysLogHandler
import sys

DEFAULT_SHARD = "shard3"


class Syslog(Socket):
    def __init__(
        self,
        config,
        user=None,
        password=None,
        ptr=False,
        loggingArg=None,
        host=None,
        secure=True,
        token=None,
    ):
        super().__init__(user, password, ptr, loggingArg, host, secure, token)
        self.log = logging.getLogger("screeps-syslog")
        self.log.addHandler(
            Rfc5424SysLogHandler(
                address=(config["syslog"]["address"], config["syslog"]["port"])
            )
        )
        self.log.setLevel(logging.DEBUG)

    def process_log(self, ws, message, shard=None):
        self.log.info(message)

    def set_subscriptions(self):
        self.subscribe_user("console")
        return
