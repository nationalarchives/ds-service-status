# https://github.com/mmeyer/uptime-kuma-api/tree/v2-support


from .__version__ import __author__, __copyright__, __title__, __version__  # noqa: F401
from .api import UptimeKumaApi  # noqa: F401
from .auth_method import AuthMethod  # noqa: F401
from .docker_type import DockerType  # noqa: F401
from .dto import MonitorBuilder  # noqa: F401
from .event import Event  # noqa: F401
from .exceptions import Timeout, UptimeKumaException  # noqa: F401
from .incident_style import IncidentStyle  # noqa: F401
from .maintenance_strategy import MaintenanceStrategy  # noqa: F401
from .monitor_status import MonitorStatus  # noqa: F401
from .monitor_type import MonitorType  # noqa: F401
from .notification_providers import (  # noqa: F401
    NotificationType,
    notification_provider_conditions,
    notification_provider_options,
)
from .proxy_protocol import ProxyProtocol  # noqa: F401
