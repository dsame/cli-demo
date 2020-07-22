from oml.hooks.appinsights import AppInsightsHook
from unittest import mock, TestCase


class AppInsightsTest(TestCase):

    @mock.patch('applicationinsights.TelemetryClient.flush')
    @mock.patch('applicationinsights.TelemetryClient.track_event')
    def test_appinsights_track_event(self, mock_track, mock_flush):
        hook = AppInsightsHook()
        hook.track_event('test_event', 'test_command')
        self.assertEqual(mock_track.call_count, 1)
        self.assertEqual(mock_flush.call_count, 1)
