import datetime
import math
import re

from markdown_it import MarkdownIt
from uptime_kuma_api import MonitorStatus


def slugify(s):
    if not s:
        return s
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    s = re.sub(r"^-+|-+$", "", s)
    return s


def markdown(s):
    """Convert a string to HTML using Markdown."""
    if not s:
        return ""
    md = MarkdownIt()
    return md.render(s)


def pretty_date(s):
    """Convert a date string to a human-readable format."""
    if not s:
        return ""
    try:
        dt = datetime.datetime.fromisoformat(s)
        return dt.strftime("%-d %B %Y, %H:%M:%S")
    except ValueError:
        return s


def pretty_uptime_kuma_status(s):
    if s == MonitorStatus(0):
        return {
            "title": "Issues detected",
            "accent_colour": "tna-accent-pink",
            "fontawesome_icon": "fa-circle-xmark",
            "status_class": "down",
        }
    if s == MonitorStatus(1):
        return {
            "title": "No issues detected",
            "accent_colour": "tna-accent-green",
            "fontawesome_icon": "fa-circle-check",
            "status_class": "up",
        }
    if s == MonitorStatus(2):
        return {
            "title": "Pending…",
            "accent_colour": "tna-accent-yellow",
            "fontawesome_icon": "fa-hourglass-half",
            "status_class": "pending",
        }
    if s == MonitorStatus(3):
        return {
            "title": "Planned maintenance",
            "accent_colour": "tna-accent-blue",
            "fontawesome_icon": "fa-wrench",
            "status_class": "maintenance",
        }
    return {"title": "Unknown", "accent_colour": "", "fontawesome_icon": "fa-question"}


def previous_incidents(heartbeats):
    if not heartbeats or not any(
        heartbeat.get("status") == 0 or heartbeat.get("status") == MonitorStatus.DOWN
        for heartbeat in heartbeats
    ):
        return []
    heartbeats = sorted(heartbeats, key=lambda x: x.get("time", ""), reverse=True)
    incidents = []
    start = None
    end = None
    has_start = False
    has_end = False
    is_ongoing_incident = heartbeats[0].get("status") == MonitorStatus(0)
    for index, heartbeat in enumerate(heartbeats):
        if index == 0 and is_ongoing_incident:
            end = heartbeat
        elif index == len(heartbeats) - 1 and heartbeat.get("status") == MonitorStatus(
            0
        ):
            start = heartbeat
        if end:
            if heartbeat.get("status") != MonitorStatus(0):
                start = heartbeats[index - 1] if index > 0 else heartbeat
                has_start = True
        elif heartbeat.get("status") == MonitorStatus(0):
            end = heartbeats[index - 1] if index > 0 else heartbeat
            has_end = True
        if start and end:
            incidents.append(
                {
                    "start": start,
                    "end": end,
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


def average_incident_time(incidents):
    if not incidents:
        return 0
    total = sum(incident.get("duration_seconds", 0) for incident in incidents)
    return total / len(incidents)


def longest_incident_time(incidents):
    if not incidents:
        return 0
    return max(incident.get("duration_seconds", 0) for incident in incidents)


def seconds_to_time(s):
    hours_label = "hour"
    minutes_label = "minute"
    seconds_label = "second"
    if not s:
        return f"00{hours_label} 00{minutes_label} 00{seconds_label}"
    total_seconds = int(s)
    hours = math.floor(total_seconds / 3600)
    # hours_padded = str(hours).rjust(2, "0")
    minutes = math.floor((total_seconds - (hours * 3600)) / 60)
    # minutes_padded = str(minutes).rjust(2, "0")
    seconds = total_seconds - (hours * 3600) - (minutes * 60)
    # seconds_padded = str(seconds).rjust(2, "0")
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


def relative_time(date):
    """Take a datetime and return its "age" as a string.
    The age can be in second, minute, hour, day, month or year. Only the
    biggest unit is considered, e.g. if it's 2 days and 3 hours, "2 days" will
    be returned.
    Make sure date is not in the future, or else it won't work.
    Original Gist by 'zhangsen' @ https://gist.github.com/zhangsen/1199964
    """

    def formatn(n, s):
        """Add "s" if it's plural"""
        int_n = int(round(n))
        if int_n == 1:
            return "1 %s" % s
        return "%d %ss" % (int_n, s)

    def qnr(a, b):
        """Return quotient and remaining"""

        return a / b, a % b

    class FormatDelta:

        def __init__(self, dt):
            now = datetime.datetime.now()
            delta = now - dt
            self.day = delta.days
            self.second = delta.seconds
            self.year, self.day = qnr(self.day, 365)
            self.month, self.day = qnr(self.day, 30)
            self.hour, self.second = qnr(self.second, 3600)
            self.minute, self.second = qnr(self.second, 60)

        def format(self):
            for period in ["year", "month", "day", "hour", "minute", "second"]:
                n = getattr(self, period)
                if n >= 1:
                    return "{0} ago".format(formatn(n, period))
            return "just now"

    return FormatDelta(date).format()


def time_ago(s):
    if not s:
        return ""
    try:
        dt = datetime.datetime.fromisoformat(s)
        return relative_time(dt)
    except ValueError:
        return s


def pretty_percentage(f):
    if f is None:
        return ""
    return f"{(round(f * 10000) / 100):g}%"
