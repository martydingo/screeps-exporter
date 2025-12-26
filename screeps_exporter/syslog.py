from screepsapi import Socket
from rfc5424logging import Rfc5424SysLogHandler
import logging, re, json

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
                address=(config["syslog"]["address"], config["syslog"]["port"]),
                appname="screeps-syslog",
            )
        )
        self.log.setLevel(logging.DEBUG)

    def process_log(self, ws, message, shard=None):
        logSeverities = {
            0: "emergency",
            1: "alert",
            2: "critical",
            3: "error",
            4: "warning",
            5: "notice",
            6: "informational",
            7: "debug",
        }
        regexSearch = re.search(
            '<font color="(.*)" severity="(.*) module=(.*)">.* - (.*)</font>', message
        ).groups()
        color = regexSearch[0]
        severity = logSeverities[int(regexSearch[1])]
        module = regexSearch[2]
        msg = regexSearch[3]

        # extraData = {"structured_data": {"severity": severity, "module": module}}
        payload = json.dumps(
            {"color": color, "severity": severity, "module": module, "message": msg}
        )

        print(payload)

        match severity:
            case "emergency":
                self.log.critical(payload)
            case "alert":
                self.log.critical(payload)
            case "critical":
                self.log.critical(payload)
            case "error":
                self.log.error(payload)
            case "warning":
                self.log.warning(payload)
            case "notice":
                self.log.info(payload)
            case "informational":
                self.log.info(payload)
                # self.log.info(f"severity={severity} name={name} message={msg}")
            case "debug":
                self.log.debug(payload)

    def set_subscriptions(self):
        self.subscribe_user("console")
        return
