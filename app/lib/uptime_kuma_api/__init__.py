# https://github.com/mmeyer/uptime-kuma-api/tree/v2-support


from .__version__ import __author__, __copyright__, __title__, __version__
from .api import UptimeKumaApi
from .auth_method import AuthMethod
from .docker_type import DockerType
from .dto import MonitorBuilder
from .event import Event
from .exceptions import Timeout, UptimeKumaException
from .incident_style import IncidentStyle
from .maintenance_strategy import MaintenanceStrategy
from .monitor_status import MonitorStatus
from .monitor_type import MonitorType
from .notification_providers import (
    NotificationType,
    notification_provider_conditions,
    notification_provider_options,
)
from .proxy_protocol import ProxyProtocol
