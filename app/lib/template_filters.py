import datetime
import re

from markdown_it import MarkdownIt


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
    if s == 0:
        return {
            "title": "Issues detected",
            "accent_colour": "tna-accent-pink",
            "fontawesome_icon": "fa-circle-xmark",
        }
    if s == 1:
        return {
            "title": "No issues detected",
            "accent_colour": "tna-accent-green",
            "fontawesome_icon": "fa-circle-check",
        }
    if s == 2:
        return {
            "title": "Pending",
            "accent_colour": "tna-accent-yellow",
            "fontawesome_icon": "fa-hourglass-half",
        }
    if s == 3:
        return {
            "title": "Planned maintenance",
            "accent_colour": "tna-accent-blue",
            "fontawesome_icon": "fa-wrench",
        }
    return {"title": "Unknown", "accent_colour": "", "fontawesome_icon": "fa-question"}


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
