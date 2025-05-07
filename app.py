import logging
import os
from pathlib import Path

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi.responses import PlainTextResponse, RedirectResponse, Response
from logiclayer import LogicLayer
from logiclayer_complexity import EconomicComplexityModule
from tesseract_olap import OlapServer
from tesseract_olap.logiclayer import TesseractModule

import project
from project.logging import RequestUrlMiddleware

logger = logging.getLogger(__name__)

# PARAMETERS ===================================================================

# These parameters are required and will prevent execution if not set
olap_backend = os.environ["TESSERACT_BACKEND"]

# These parameters are optional
olap_schema = os.environ.get("TESSERACT_SCHEMA", "/app/etc/schema")
olap_cache = os.environ.get("TESSERACT_CACHE", "")
app_debug = os.environ.get("TESSERACT_DEBUG", None)

app_debug = bool(app_debug)


# LogicLayer modules ===========================================================
layer = LogicLayer(
    debug=app_debug,
    title=project.__title__,
    terms_of_service="https://oec.world/en/resources/terms",
    contact={
        "name": "Support Center",
        "email": "support@oec.world",
    },
)

olap = OlapServer(backend=olap_backend, schema=olap_schema, cache=olap_cache)

mod_tesseract = TesseractModule(olap, debug=app_debug)
layer.add_module("/tesseract", mod_tesseract)

mod_ecomplexity = EconomicComplexityModule(olap, debug=app_debug)
layer.add_module("/complexity", mod_ecomplexity)

dir_explorer = Path("./etc/explorer/").resolve()
if not os.access(dir_explorer, os.R_OK):
    msg = f"Can't access DataExplorer at {dir_explorer}"
    raise OSError(msg)
layer.add_static("/ui", dir_explorer, html=True)

# ASGI Middlewares =============================================================

# Adds the persistent Request ID to trace request logs
layer.app.add_middleware(CorrelationIdMiddleware)

# Adds the Request URL to avoid storing uvicorn.access
layer.app.add_middleware(RequestUrlMiddleware)

# Adds CORS handling
# layer.app.add_middleware(
#    CORSMiddleware,
#    allow_origins=["*"] if app_debug else [],
#    allow_origin_regex=r"https://.*\.oec\.world",
#    allow_credentials=True,
#    allow_methods=["GET", "POST"],
#    allow_headers=["*"],
#    expose_headers=[
#        "X-Tesseract-Columns",
#        "X-Tesseract-QueryRows",
#        "X-Tesseract-TotalRows",
#    ],
#    max_age=1800,
# )

# Extra individual routes ======================================================


@layer.route("/", response_class=RedirectResponse, status_code=302)
def route_index() -> str:
    """Define a redirection of the domain root to the Tesseract UI static page."""
    return "/ui/"


@layer.route("/robots.txt", include_in_schema=False)
def route_robots() -> Response:
    """Define the robots.txt directive for the root."""
    return PlainTextResponse("User-agent: *\nDisallow: /\n")


logger.info("App is ready to accept connections")
