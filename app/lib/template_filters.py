import datetime
import math

from markdown_it import MarkdownIt
from tna_utilities.datetime import get_date_from_string, pretty_age
from uptime_kuma_api import MonitorStatus


def markdown(s):
    """Convert a string to HTML using Markdown."""
    if not s:
        return ""
    md = MarkdownIt()
    return md.render(s)


def pretty_uptime_kuma_status(s):
    if s == MonitorStatus(0):
        return {
            "title": "Issues detected",
            "accent_colour": "tna-accent-pink",
            "fontawesome_icon": "fa-circle-xmark",
            "status_class": "down",
            "status_code": 0,
        }
    if s == MonitorStatus(1):
        return {
            "title": "No issues detected",
            "accent_colour": "tna-accent-green",
            "fontawesome_icon": "fa-circle-check",
            "status_class": "up",
            "status_code": 1,
        }
    if s == MonitorStatus(2):
        return {
            "title": "Pending…",
            "accent_colour": "tna-accent-yellow",
            "fontawesome_icon": "fa-hourglass-half",
            "status_class": "pending",
            "status_code": 2,
        }
    if s == MonitorStatus(3):
        return {
            "title": "Planned maintenance",
            "accent_colour": "tna-accent-blue",
            "fontawesome_icon": "fa-wrench",
            "status_class": "maintenance",
            "status_code": 3,
        }
    return {"title": "Unknown", "accent_colour": "", "fontawesome_icon": "fa-question"}


def previous_incidents(heartbeats):
    if not heartbeats or not any(
        heartbeat.get("status") == MonitorStatus(0)
        or heartbeat.get("status") == MonitorStatus(3)
        for heartbeat in heartbeats
    ):
        return []
    heartbeats = sorted(heartbeats, key=lambda x: x.get("time", ""), reverse=True)
    incidents = []
    start = None
    end = None
    has_start = False
    has_end = False
    is_ongoing_incident = heartbeats[0].get("status") == MonitorStatus(0) or heartbeats[
        0
    ].get("status") == MonitorStatus(3)
    for index, heartbeat in enumerate(heartbeats):
        if index == 0 and is_ongoing_incident:
            end = heartbeat
        elif index == len(heartbeats) - 1 and (
            heartbeat.get("status") == MonitorStatus(0)
            or heartbeat.get("status") == MonitorStatus(3)
        ):
            start = heartbeat
            has_start = True
        if end:
            if heartbeat.get("status") != MonitorStatus(0) and heartbeat.get(
                "status"
            ) != MonitorStatus(3):
                start = heartbeats[index - 1] if index > 0 else heartbeat
                has_start = True
        elif heartbeat.get("status") == MonitorStatus(0) or heartbeat.get(
            "status"
        ) == MonitorStatus(3):
            end = heartbeats[index - 1] if index > 0 else heartbeat
            has_end = True
        if start and end:
            incidents.append(
                {
                    "start": start,
                    "end": end if has_end else None,
                    "has_start": has_start,
                    "has_end": has_end,
                    "duration_seconds": int(
                        (
                            (
                                datetime.datetime.fromisoformat(end.get("time"))
                                if has_end
                                else datetime.datetime.now()
                            )
                            - datetime.datetime.fromisoformat(start.get("time"))
                        ).total_seconds()
                    ),
                    "status": pretty_uptime_kuma_status(
                        MonitorStatus(start.get("status"))
                        if start
                        else (
                            MonitorStatus(heartbeats[-1].get("status"))
                            if index == len(heartbeats) - 1 and not has_start
                            else (MonitorStatus(end.get("status")) if end else None)
                        )
                    ),
                }
            )
            start = None
            end = None
            has_start = False
            has_end = False
    return incidents


def incident_count(incidents):
    incidents = [i for i in incidents if i["status"]["status_code"] == MonitorStatus(0)]
    if not incidents:
        return 0
    return len(incidents)


def average_incident_time(incidents):
    incidents = [i for i in incidents if i["status"]["status_code"] == MonitorStatus(0)]
    if not incidents:
        return 0
    total = sum(i.get("duration_seconds", 0) for i in incidents)
    return total / len(incidents)


def longest_incident_time(incidents):
    incidents = [i for i in incidents if i["status"]["status_code"] == MonitorStatus(0)]
    if not incidents:
        return 0
    return max(i.get("duration_seconds", 0) for i in incidents)


def total_incident_time(incidents):
    incidents = [i for i in incidents if i["status"]["status_code"] == MonitorStatus(0)]
    if not incidents:
        return 0
    return sum(i.get("duration_seconds", 0) for i in incidents)


def total_maintenance_time(incidents):
    if not incidents:
        return 0
    incidents = [i for i in incidents if i["status"]["status_code"] == MonitorStatus(3)]
    return sum(i.get("duration_seconds", 0) for i in incidents)


def seconds_to_time(s):
    if not s:
        return "No time"
    hours_label = "hour"
    minutes_label = "minute"
    seconds_label = "second"
    total_seconds = int(s)
    hours = math.floor(total_seconds / 3600)
    minutes = math.floor((total_seconds - (hours * 3600)) / 60)
    seconds = total_seconds - (hours * 3600) - (minutes * 60)
    hours_label = hours_label if hours == 1 else f"{hours_label}s"
    minutes_label = minutes_label if minutes == 1 else f"{minutes_label}s"
    seconds_label = seconds_label if seconds == 1 else f"{seconds_label}s"
    if hours > 0:
        if seconds == 0 and minutes == 0:
            return f"{hours} {hours_label}"
        if seconds == 0:
            return f"{hours} {hours_label} {minutes} {minutes_label}"
        return (
            f"{hours} {hours_label} {minutes} {minutes_label} {seconds} {seconds_label}"
        )
    if minutes > 0:
        if seconds == 0:
            return f"{minutes} {minutes_label}"
        return f"{minutes} {minutes_label} {seconds} {seconds_label}"
    return f"{seconds} {seconds_label}"


def time_ago(s):
    if not s:
        return ""
    try:
        dt = get_date_from_string(s)
        return pretty_age(dt)
    except ValueError:
        return s


def pretty_percentage(f):
    if f is None:
        return ""
    return f"{(round(f * 10000) / 100):g}%"
