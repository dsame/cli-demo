import pkg_resources
import platform

from applicationinsights import TelemetryClient
from datetime import datetime
from oml.settings import APP_INSIGHTS_KEY, APP_INSIGHTS_EVENT_TITLE, USER_ID


class AppInsightsHook:

    def __init__(self):
        self.tc = TelemetryClient(APP_INSIGHTS_KEY)
        self.user_id = USER_ID
        self.app_version = pkg_resources.require('oml')[0].version
        self.python_version = platform.python_version()
        self.platform = platform.platform()
        self.timestamp = str(datetime.utcnow())

    def track_event(self, event_type, action):
        """Sends Custom Event to Application Insights"""

        event_data = {
            'user_id': self.user_id,
            'action': action,
            'app_version': self.app_version,
            'event_type': event_type,
            'python_version': self.python_version,
            'platform': self.platform,
            'timestamp': self.timestamp
        }

        self.tc.track_event(APP_INSIGHTS_EVENT_TITLE, event_data)
        self.tc.flush()
