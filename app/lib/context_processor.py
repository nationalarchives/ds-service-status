import datetime
import json
from urllib.parse import unquote

from app.lib.uptime_kuma_api.monitor_status import MonitorStatus
from flask import request
from tna_utilities.datetime import pretty_date, pretty_datetime


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
    now_date = pretty_datetime(now)
    return now_date


def cookie_preference(policy):
    if "cookies_policy" in request.cookies:
        cookies_policy = request.cookies["cookies_policy"]
        preferences = json.loads(unquote(cookies_policy))
        return preferences[policy] if policy in preferences else None
    return None


def incident_calendar_count(days, incidents):
    calendar = []
    for i in range(days + 1):
        day = datetime.datetime.now() + datetime.timedelta(days=-i)
        calendar.append(
            {
                "date": day.date().isoformat(),
                "short_date": day.date().strftime("%-d %b"),
                "pretty_date": pretty_date(day),
                "count": len(
                    [
                        incident
                        for incident in incidents
                        if incident.get("start")
                        and incident["start"].get("status", None) != MonitorStatus(3)
                        and incident["start"].get("time")
                        and datetime.datetime.fromisoformat(
                            incident["start"]["time"]
                        ).date()
                        == day.date()
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


def incident_calendar_heartbeats(incidents, days):
    calendar = []
    for i in range(days + 1):
        day = datetime.datetime.now() + datetime.timedelta(days=-i)
        day_incidents = [
            incident
            for incident in incidents
            if (
                incident.get("start")
                and incident["start"].get("time")
                and datetime.datetime.fromisoformat(incident["start"]["time"])
                .replace(hour=0, minute=0, second=0, microsecond=0)
                .date()
                == day.date()
            )
            or (
                incident.get("end")
                and incident["end"].get("time")
                and datetime.datetime.fromisoformat(incident["end"]["time"])
                .replace(hour=23, minute=59, second=59, microsecond=999999)
                .date()
                == day.date()
            )
            or (
                incident.get("start")
                and incident.get("end")
                and incident["start"].get("time")
                and incident["end"].get("time")
                and datetime.datetime.fromisoformat(incident["start"]["time"])
                .replace(hour=0, minute=0, second=0, microsecond=0)
                .date()
                < day.date()
                and datetime.datetime.fromisoformat(incident["end"]["time"])
                .replace(hour=23, minute=59, second=59, microsecond=999999)
                .date()
                > day.date()
            )
        ]
        calendar.append(
            {
                "time": day.replace(
                    hour=0, minute=0, second=0, microsecond=0
                ).isoformat(),
                "title": pretty_date(day),
                "status": (
                    MonitorStatus(0)
                    if any(
                        [
                            incident
                            for incident in day_incidents
                            if incident["start"].get("status", None) == MonitorStatus(0)
                        ]
                    )
                    else (
                        MonitorStatus(3)
                        if any(
                            [
                                incident
                                for incident in day_incidents
                                if incident["start"].get("status", None)
                                == MonitorStatus(3)
                            ]
                        )
                        else (
                            MonitorStatus(2) if len(day_incidents) else MonitorStatus(1)
                        )
                    )
                ),
            }
        )
    calendar.sort(key=lambda x: x["time"], reverse=False)
    return calendar


def incident_calendar_duration(days, incidents):
    calendar = []
    for i in range(days + 1):
        day = datetime.datetime.now() + datetime.timedelta(days=-i)
        calendar.append(
            {
                "date": day.date().isoformat(),
                "short_date": day.date().strftime("%-d %b"),
                "pretty_date": pretty_date(day),
                "duration": sum(
                    [
                        incident.get("duration_seconds", 0)
                        for incident in incidents
                        if incident.get("start")
                        and incident["start"].get("status", None) != MonitorStatus(3)
                        and incident["start"].get("time")
                        and datetime.datetime.fromisoformat(
                            incident["start"]["time"]
                        ).date()
                        == day.date()
                    ]
                ),
            }
        )
    calendar.sort(key=lambda x: x["date"], reverse=False)
    start_day_offset = (
        datetime.datetime.now() + datetime.timedelta(days=-days)
    ).weekday()
    max_duration = max(item["duration"] for item in calendar) if calendar else 0
    return {
        "calendar": calendar,
        "max_duration": max_duration,
        "start_day_offset": start_day_offset,
    }
