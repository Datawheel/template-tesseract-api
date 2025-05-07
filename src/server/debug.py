import getpass
import html
import os
import pathlib
import platform
import socket
import sys
from pathlib import Path

import logiclayer as ll
from fastapi.responses import StreamingResponse


class DebugModule(ll.LogicLayerModule):
    @ll.route("GET", "/logs")
    def route_logs(self):
        return StreamingResponse(log_generator())

    @ll.route("GET", "/env")
    def route_resources(self):
        return {
            "Python version": sys.version,
            "Platform": platform.platform(),
            "Processor": platform.processor(),
            "Architecture": platform.architecture(),
            "Hostname": socket.gethostname(),
            "IP Address": socket.gethostbyname(socket.gethostname()),
            "Current Working Directory": os.getcwd(),
        }

    @ll.route("GET", "/permissions")
    def route_state(self):
        cwd = Path.cwd()
        stat = cwd.stat()

        return {
            "user": getpass.getuser(),
            "path": cwd,
            "chmod": oct(stat.st_mode),
            "chown": [stat.st_uid, stat.st_gid],
        }


def log_generator():
    yield "<!DOCTYPE html><html><body>\n<details hidden>"
    with pathlib.Path("/tmp/debug.log").open() as fp:
        for line in fp:
            escaped = html.escape(line.strip())
            if "oec.auth" in line or "tesseract_olap.server" in line:
                yield f"</details>\n<details><summary>{escaped}</summary>"
            else:
                yield f"<p>{escaped}</p>"
    yield "</details></body></html>"
