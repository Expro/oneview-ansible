# -*- coding: utf-8 -*-
###
# Copyright (2016) Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

import yaml
import mock

from mock import patch
from hpOneView.oneview_client import OneViewClient


def create_ansible_mock(params):
    mock_ansible = mock.Mock()
    mock_ansible.params = params
    return mock_ansible


def create_ansible_mock_yaml(yaml_config):
    mock_ansible = mock.Mock()
    mock_ansible.params = yaml.load(yaml_config)
    return mock_ansible


class PreloadedMocksBaseTestCase(object):
    _testing_class = None
    _testing_module = None
    mock_ov_client_from_json_file = None
    mock_ov_client_from_env_vars = None
    mock_ansible_module = None
    mock_ov_client = None

    def configure_mocks(self, test_case, testing_class):
        """
        Preload mocked OneViewClient instance and AnsibleModule
        Args:
            test_case (object): class instance (self) that are inheriting from ModuleContructorTestCase
            testing_class (object): class being tested
        """
        self._testing_class = testing_class
        self._testing_module = testing_class.__module__

        # Define OneView Client Mock (FILE)
        patcher_json_file = patch.object(OneViewClient, 'from_json_file')
        test_case.addCleanup(patcher_json_file.stop)
        self.mock_ov_client_from_json_file = patcher_json_file.start()

        # Define OneView Client Mock
        self.mock_ov_client = self.mock_ov_client_from_json_file.return_value

        # Define OneView Client Mock (ENV)
        patcher_env = patch.object(OneViewClient, 'from_environment_variables')
        test_case.addCleanup(patcher_env.stop)
        self.mock_ov_client_from_env_vars = patcher_env.start()

        # Define Ansible Module Mock
        patcher_ansible = patch(self._testing_module + '.AnsibleModule')
        test_case.addCleanup(patcher_ansible.stop)
        mock_ansible_module = patcher_ansible.start()
        self.mock_ansible_module = mock.Mock()
        mock_ansible_module.return_value = self.mock_ansible_module


class ModuleContructorTestCase(PreloadedMocksBaseTestCase):
    """
    ModuleContructorTestCase has common tests for class constructor and main function

    When inheriting this class, the class and main function tests are added to your test case.
    """

    def __validations(self):
        if not self._testing_class:
            raise Exception("Mocks are not configured, you must call 'configure_mocks' before running this test.")

    def test_should_load_config_from_file(self):
        self.__validations()

        self.mock_ansible_module.params = {'config': 'config.json'}

        # Call the constructor
        self._testing_class()

        self.mock_ov_client_from_json_file.assert_called_once_with('config.json')
        self.mock_ov_client_from_env_vars.not_been_called()

    def test_should_load_config_from_environment(self):
        self.__validations()

        self.mock_ansible_module.params = {'config': None}

        # Call the constructor
        self._testing_class()

        self.mock_ov_client_from_env_vars.assert_called_once()
        self.mock_ov_client_from_json_file.not_been_called()

    def test_should_call_fail_json_when_not_have_oneview(self):
        self.__validations()
        self.mock_ansible_module.params = {'config': 'config.json'}

        with mock.patch(self._testing_module + ".HAS_HPE_ONEVIEW", False):
            self._testing_class()

        self.mock_ansible_module.fail_json.assert_called_once_with(
            msg='HPE OneView Python SDK is required for this module.')

    def test_main_function_should_call_run_method(self):
        self.__validations()
        self.mock_ansible_module.params = {'config': 'config.json'}

        module = __import__(self._testing_module)
        main_func = getattr(module, 'main')

        with mock.patch.object(self._testing_class, "run") as mock_run:
            main_func()
            mock_run.assert_called_once()
