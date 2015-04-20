import env_setup; env_setup.setup_tests(); env_setup.setup_django()

from agar.test import BaseTest
from scripts import roboemu as robot


class RoboEmuTest(BaseTest):

    def test_gen_steps_from_math(self):
        steps = robot.gen_steps_from_map(robot.SPYHOUSE_COFFEE, robot.MAP)
        self.assertIsNotNone(steps)
        self.assertLength(25, steps)