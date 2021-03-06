from unittest.mock import Mock

from app.master.slave import Slave
from app.util.conf.configuration import Configuration
from app.util.secret import Secret
from test.framework.base_unit_test_case import BaseUnitTestCase


class TestSlave(BaseUnitTestCase):

    _FAKE_SLAVE_URL = 'splinter.sensei.net:43001'
    _FAKE_NUM_EXECUTORS = 10

    def setUp(self):
        super().setUp()
        self.mock_network = self.patch('app.master.slave.Network').return_value

    def test_disconnect_command_is_sent_during_teardown_when_slave_is_still_connected(self):
        slave = self._create_slave()
        slave.current_build_id = 3
        slave.is_alive = True

        slave.teardown()

        expected_teardown_url = 'http://splinter.sensei.net:43001/v1/build/3/teardown'
        self.mock_network.post.assert_called_once_with(expected_teardown_url)

    def test_disconnect_command_is_not_sent_during_teardown_when_slave_has_disconnected(self):
        slave = self._create_slave()
        slave.current_build_id = 3
        slave.is_alive = False

        slave.teardown()

        self.assertEqual(self.mock_network.post.call_count, 0,
                         'Master should not send teardown command to slave when slave has disconnected.')

    def test_git_project_params_are_modified_for_slave(self):
        remote_path = 'central.sourcecode.example.com/company/project'
        base_directory = '/home/cr_user/.clusterrunner'
        Configuration['repo_directory'] = '{}/repos/master'.format(base_directory)
        slave = self._create_slave()
        slave._network.post_with_digest = Mock()

        slave.setup(1, {'type': 'git', 'url': 'http://{}'.format(remote_path)})

        slave._network.post_with_digest.assert_called_with('http://{}/v1/build/1/setup'.format(self._FAKE_SLAVE_URL),
                                                           {'project_type_params': {
                                                               'url': 'ssh://{}{}/repos/master/{}'.format(
                                                                   self._fake_hostname,
                                                                   base_directory,
                                                                   remote_path),
                                                               'type': 'git'}}, Secret.get())

    def _create_slave(self, **kwargs):
        """
        Create a slave for testing.
        :param kwargs: Any constructor parameters for the slave; if none are specified, test defaults will be used.
        :rtype: Slave
        """
        kwargs.setdefault('slave_url', self._FAKE_SLAVE_URL)
        kwargs.setdefault('num_executors', self._FAKE_NUM_EXECUTORS)
        return Slave(**kwargs)
