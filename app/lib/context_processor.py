import datetime
import json
from urllib.parse import unquote

from flask import request

# from uptime_kuma_api import MonitorStatus


def now_iso_8601():
    now = datetime.datetime.now()
    now_date = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return now_date


def now_iso_8601_date():
    now = datetime.datetime.now()
    now_date = now.strftime("%Y-%m-%d")
    return now_date


def now_pretty():
    now = datetime.datetime.now()
    now_date = now.strftime("%-d %B %Y, %H:%M:%S")
    return now_date


def cookie_preference(policy):
    if "cookies_policy" in request.cookies:
        cookies_policy = request.cookies["cookies_policy"]
        preferences = json.loads(unquote(cookies_policy))
        return preferences[policy] if policy in preferences else None
    return None


def incident_calendar(days, incidents):
    calendar = []
    for i in range(days + 1):
        day = (datetime.datetime.now() + datetime.timedelta(days=-i)).date()
        calendar.append(
            {
                "date": day.isoformat(),
                "short_date": day.strftime("%-d %b"),
                "pretty_date": day.strftime("%-d %B %Y"),
                "count": len(
                    [
                        incident
                        for incident in incidents
                        if incident.get("start")
                        # and incident["start"].get("status", None) != MonitorStatus(3)
                        and incident["start"].get("time")
                        and datetime.datetime.fromisoformat(
                            incident["start"]["time"]
                        ).date()
                        == day
                    ]
                ),
            }
        )
    calendar.sort(key=lambda x: x["date"], reverse=False)
    start_day_offset = (
        datetime.datetime.now() + datetime.timedelta(days=-days)
    ).weekday()
    max_indicents = max(item["count"] for item in calendar) if calendar else 0
    return {
        "calendar": calendar,
        "max_incidents": max_indicents,
        "start_day_offset": start_day_offset,
    }
