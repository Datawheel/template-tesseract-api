import logging.config
import os

from fastapi.responses import RedirectResponse
from logiclayer import LogicLayer
from logiclayer_complexity import EconomicComplexityModule
from tesseract_olap import OlapServer
from tesseract_olap.logiclayer import TesseractModule

from server.debug import DebugModule

# PARAMETERS ===================================================================

# These parameters are required and will prevent execution if not set
olap_backend = os.environ["TESSERACT_BACKEND"]

# These parameters are optional
olap_schema = os.environ.get("TESSERACT_SCHEMA", "etc/schema")
olap_cache = os.environ.get("TESSERACT_CACHE", "")
app_debug = os.environ.get("TESSERACT_DEBUG", None)
log_filepath = os.environ.get("TESSERACT_LOGGING_CONFIG", "etc/logging.ini")

app_debug = bool(app_debug)


# LOGGING ======================================================================
# To learn how logging works in python
# - https://docs.python.org/3.7/howto/logging.html
# To learn about best practices and the logging.ini file
# - https://www.datadoghq.com/blog/python-logging-best-practices/
# - https://guicommits.com/how-to-log-in-python-like-a-pro/

logging.config.fileConfig(log_filepath, disable_existing_loggers=False)


# ASGI app =====================================================================
olap = OlapServer(backend=olap_backend, schema=olap_schema, cache=olap_cache)

mod_tsrc = TesseractModule(olap, debug=app_debug)

mod_cmplx = EconomicComplexityModule(olap, debug=app_debug)

layer = LogicLayer(debug=app_debug)

if app_debug:
    mod_debug = DebugModule()
    layer.add_module("/debug", mod_debug)

layer.add_module("/tesseract", mod_tsrc)
layer.add_module("/complexity", mod_cmplx)
layer.add_static("/ui", "./etc/static/", html=True)


@layer.route("/", response_class=RedirectResponse, status_code=302)
def route_index():
    return "/ui/"
