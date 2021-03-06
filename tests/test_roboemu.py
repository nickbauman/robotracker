import env_setup

env_setup.setup_tests()
env_setup.setup_django()

import requests, json
from mock import Mock, patch
from agar.test import BaseTest
from utils import web
from utils.geolocation import haversine_distance

from scripts import roboemu as robot
from scripts.roboemu import HOST, PORT


class RoboEmuTest(BaseTest):
    def test_gen_steps_from_math(self):
        steps = robot.gen_steps_from_map(robot.SPYHOUSE_COFFEE, robot.MAP1)
        self.assertIsNotNone(steps)
        self.assertLength(28, steps)

    def test_robo_walkabout(self):
        with patch.object(requests, 'post', return_value=Mock(status_code=200)) as requests_mock:
            robot.robo_walkabout(sample_rate_per_minute=60)
            for call in requests_mock.mock_calls:
                url = call[1][0]
                expected_url = 'http://{}:{}{}'.format(HOST, PORT, web.build_uri('robot-event-post'))
                self.assertEqual(expected_url, url)
                json_str = call[2]['json']
                data = json.loads(json_str)
                self.assertIsNotNone(data)
                self.assertEqual(1234, data['robot_id'])
                self.assertTrue(data.has_key('loc'))
                self.assertTrue(data.has_key('luxes'))
                self.assertTrue(data.has_key('temps'))
