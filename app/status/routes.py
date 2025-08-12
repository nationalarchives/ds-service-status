import os

from app.lib.api import JSONAPIClient, ResourceNotFound
from app.lib.cache import cache, cache_key_prefix
from app.status import bp
from flask import current_app, render_template


@bp.route("/")
@cache.cached(
    key_prefix=cache_key_prefix,
    timeout=int(os.environ.get("STATUS_PAGE_CACHE_DURATION", "15")),
)
def index():
    uptime_kuma_api_url = current_app.config.get("UPTIME_KUMA_API_URL")
    uptime_kuma_status_page_slug = current_app.config.get(
        "UPTIME_KUMA_STATUS_PAGE_SLUG"
    )
    if not uptime_kuma_api_url:
        current_app.logger.critical("UPTIME_KUMA_API_URL not set")
        raise Exception("UPTIME_KUMA_API_URL not set")
    if not uptime_kuma_status_page_slug:
        current_app.logger.critical("UPTIME_KUMA_STATUS_PAGE_SLUG not set")
        raise Exception("UPTIME_KUMA_STATUS_PAGE_SLUG not set")
    client = JSONAPIClient(uptime_kuma_api_url)
    try:
        data = client.get(f"status-page/{uptime_kuma_status_page_slug}")
        heartbeats = client.get(f"status-page/heartbeat/{uptime_kuma_status_page_slug}")
        return render_template("status/index.html", data=data, heartbeats=heartbeats)
    except ResourceNotFound as e:
        current_app.logger.error(f"Failed to render status page: {e}")
        return render_template("errors/api.html"), 502
