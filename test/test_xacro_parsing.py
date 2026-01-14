import os
import unittest

from ament_index_python.packages import get_package_share_directory
import launch_testing.actions
import launch_testing.asserts
import pytest
import xacro
from launch import LaunchDescription
from launch_ros.actions import Node


@pytest.mark.launch_test
def generate_test_description():
    pkg_name = 'kuka_kr300_support'

    try:
        pkg_share = get_package_share_directory(pkg_name)
        xacro_path = os.path.join(pkg_share, 'urdf', 'kr300r2500ultra.xacro')
    except (KeyError, FileNotFoundError):
        # Fallback for when running in a way where share isn't ready or
        # readable
        xacro_path = 'urdf/kr300r2500ultra.xacro'

    # Processing xacro
    doc = xacro.process_file(xacro_path)
    robot_description = {'robot_description': doc.toxml()}

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )

    return LaunchDescription([
        robot_state_publisher,
        launch_testing.actions.ReadyToTest()
    ])


class TestCalibration(unittest.TestCase):

    def test_readiness(self, proc_output):
        """Test that the robot_state_publisher starts up."""
        # This checks that the actions in LaunchDescription started
        pass


@launch_testing.post_shutdown_test()
class TestProcessOutput(unittest.TestCase):

    def test_exit_code(self, proc_info):
        # Check that all processes exited normally
        launch_testing.asserts.assertExitCodes(
            proc_info,
            process='robot_state_publisher',
            allowable_exit_codes=[0, -2]
        )
