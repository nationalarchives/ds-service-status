import os

from app.lib.api import JSONAPIClient
from app.lib.cache import cache, cache_key_prefix
from app.status import bp
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
    timeout=int(os.environ.get("STATUS_PAGE_CACHE_DURATION", "15")),
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

    jwt_set_up = current_app.config.get("UPTIME_KUMA_JWT", "") is not ""

    return render_template(
        "status/index.html", data=data, heartbeats=heartbeats, jwt_set_up=jwt_set_up
    )


@bp.route("/<int:monitor_id>")
@cache.cached(key_prefix=cache_key_prefix)
def details(monitor_id):
    uptime_kuma_url, uptime_kuma_status_page_slug = get_settings()
    heartbeat_hours_to_show = 720  # 30 days

    if jwt := current_app.config.get("UPTIME_KUMA_JWT"):
        with UptimeKumaApi(uptime_kuma_url) as api:
            api.login_by_token(jwt)

            status_page = api.get_status_page(uptime_kuma_status_page_slug)
            id_in_list = False
            groups = status_page.get("publicGroupList", [])
            for list in groups:
                monitorList = list.get("monitorList", [])
                for monitor in monitorList:
                    if monitor["id"] == monitor_id:
                        status_page_monitor_details = monitor
                        id_in_list = True
                        break
            if not id_in_list:
                return render_template("errors/page_not_found.html"), 404

            monitors = api.get_monitors()
            monitor = next((m for m in monitors if m["id"] == monitor_id), None)
            monitor_children = []
            for child in monitor.get("childrenIDs", []):
                child = next((m for m in monitors if m["id"] == child), None)
                if child:
                    monitor_children.append(child)
            for child in monitor_children:
                child["heartbeats"] = api.get_monitor_beats(
                    child["id"], heartbeat_hours_to_show
                )

            uptimes = api.uptime().get(monitor_id, {})
            heartbeats = api.get_monitor_beats(monitor_id, heartbeat_hours_to_show)

            return render_template(
                "status/details.html",
                status_page_monitor_details=status_page_monitor_details,
                monitor=monitor,
                monitor_children=monitor_children,
                MonitorType=MonitorType,
                uptimes=uptimes,
                heartbeats=heartbeats,
                heartbeat_hours_to_show=heartbeat_hours_to_show,
            )

    return redirect(url_for("status.index"))
