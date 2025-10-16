import os

from app.lib.api import JSONAPIClient
from app.lib.cache import cache, cache_key_prefix
from app.lib.template_filters import slugify
from app.status import bp
from config import DEFAULT_STATUS_PAGE_CACHE_DURATION
from flask import current_app, redirect, render_template, url_for
from uptime_kuma_api import MonitorType, UptimeKumaApi


def get_settings():
    uptime_kuma_url = current_app.config.get("UPTIME_KUMA_URL").strip("/")
    if not uptime_kuma_url:
        current_app.logger.critical("UPTIME_KUMA_URL not set")
        raise Exception("UPTIME_KUMA_URL not set")

    uptime_kuma_status_page_slug = current_app.config.get(
        "UPTIME_KUMA_STATUS_PAGE_SLUG"
    )
    if not uptime_kuma_status_page_slug:
        current_app.logger.critical("UPTIME_KUMA_STATUS_PAGE_SLUG not set")
        raise Exception("UPTIME_KUMA_STATUS_PAGE_SLUG not set")

    return uptime_kuma_url, uptime_kuma_status_page_slug


@bp.route("/")
@cache.cached(
    key_prefix=cache_key_prefix,
    timeout=int(
        os.environ.get("STATUS_PAGE_CACHE_DURATION", DEFAULT_STATUS_PAGE_CACHE_DURATION)
    ),
)
def index():
    uptime_kuma_url, uptime_kuma_status_page_slug = get_settings()

    client = JSONAPIClient(f"{uptime_kuma_url}/api")
    try:
        data = client.get(f"status-page/{uptime_kuma_status_page_slug}")
        heartbeats = client.get(f"status-page/heartbeat/{uptime_kuma_status_page_slug}")
    except Exception as e:
        current_app.logger.error(f"Failed to render status page: {e}")
        return render_template("errors/api.html"), 502

    jwt_set_up = current_app.config.get("UPTIME_KUMA_JWT", "") != ""

    return render_template(
        "status/index.html", data=data, heartbeats=heartbeats, jwt_set_up=jwt_set_up
    )


@bp.route("/<string:monitor_slug>/")
@cache.cached(key_prefix=cache_key_prefix)
def details(monitor_slug):
    uptime_kuma_url, uptime_kuma_status_page_slug = get_settings()

    if jwt := current_app.config.get("UPTIME_KUMA_JWT"):
        try:
            with UptimeKumaApi(uptime_kuma_url) as api:
                api.login_by_token(jwt)

                status_page = api.get_status_page(uptime_kuma_status_page_slug)
                monitor_id = None
                groups = status_page.get("publicGroupList", [])
                for list in groups:
                    monitorList = list.get("monitorList", [])
                    for monitor in monitorList:
                        if slugify(monitor["name"]) == monitor_slug:
                            status_page_monitor_details = monitor
                            monitor_id = monitor["id"]
                            break
                if not monitor_id:
                    return render_template("errors/page_not_found.html"), 404

                monitors = api.get_monitors()
                pings = api.avg_ping()
                uptimes = api.uptime()
                monitor = next((m for m in monitors if m["id"] == monitor_id), None)
                monitor_children = []
                for child in monitor.get("childrenIDs", []):
                    child = next((m for m in monitors if m["id"] == child), None)
                    if child:
                        monitor_children.append(child)
                for child in monitor_children:
                    child["heartbeats"] = api.get_monitor_beats(
                        child["id"],
                        current_app.config.get("DETAILED_SERVICE_REPORT_HOURS"),
                    )
                    child["average_ping"] = pings.get(child["id"], None)
                    child["uptime"] = uptimes.get(child["id"], None)

                uptime = uptimes.get(monitor_id, {})
                heartbeats = api.get_monitor_beats(
                    monitor_id, current_app.config.get("DETAILED_SERVICE_REPORT_HOURS")
                )
                average_ping = pings.get(monitor_id, None)

                return render_template(
                    "status/details.html",
                    status_page_monitor_details=status_page_monitor_details,
                    monitor=monitor,
                    monitor_children=monitor_children,
                    MonitorType=MonitorType,
                    uptime=uptime,
                    heartbeats=heartbeats,
                    heartbeat_hours_to_show=current_app.config.get(
                        "DETAILED_SERVICE_REPORT_HOURS"
                    ),
                    average_ping=average_ping,
                )
        except Exception as e:
            current_app.logger.error(
                f"Failed to render detailed status page for '{monitor_slug}': {e}"
            )
            return render_template("errors/api.html"), 502

    return redirect(url_for("status.index"))
