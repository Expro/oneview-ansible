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

import unittest
import mock

from hpOneView.oneview_client import OneViewClient
from oneview_network_set_facts import NetworkSetFactsModule
from test.utils import create_ansible_mock

ERROR_MSG = 'Fake message error'

PARAMS_GET_ALL = dict(
    config='config.json',
    name=None
)

PARAMS_GET_ALL_WITHOUT_ETHERNET = dict(
    config='config.json',
    name=None,
    options=['withoutEthernet']
)

PARAMS_GET_BY_NAME = dict(
    config='config.json',
    name='Network Set 1'
)

PARAMS_GET_BY_NAME_WITHOUT_ETHERNET = dict(
    config='config.json',
    name='Network Set 1',
    options=['withoutEthernet']
)


class NetworkSetFactsSpec(unittest.TestCase):
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_network_set_facts.AnsibleModule')
    def test_should_get_all_network_sets(self, mock_ansible_module, mock_ov_client_from_json_file):
        network_sets = [{
            "name": "Network Set 1",
            "networkUris": ['/rest/ethernet-networks/aaa-bbb-ccc']
        }, {
            "name": "Network Set 2",
            "networkUris": ['/rest/ethernet-networks/ddd-eee-fff', '/rest/ethernet-networks/ggg-hhh-fff']
        }]
        mock_ov_instance = mock.Mock()
        mock_ov_instance.network_sets.get_all.return_value = network_sets

        mock_ov_client_from_json_file.return_value = mock_ov_instance

        mock_ansible_instance = create_ansible_mock(PARAMS_GET_ALL)
        mock_ansible_module.return_value = mock_ansible_instance

        NetworkSetFactsModule().run()

        mock_ov_instance.network_sets.get_all.assert_called_once_with()

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=False,
            ansible_facts=dict(network_sets=network_sets))

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_network_set_facts.AnsibleModule')
    def test_should_get_all_network_sets_without_ethernet(self, mock_ansible_module, mock_ov_client_from_json_file):
        network_sets = [{
            "name": "Network Set 1",
            "networkUris": []
        }, {
            "name": "Network Set 2",
            "networkUris": []
        }]
        mock_ov_instance = mock.Mock()
        mock_ov_instance.network_sets.get_all.return_value = network_sets

        mock_ov_client_from_json_file.return_value = mock_ov_instance

        mock_ansible_instance = create_ansible_mock(PARAMS_GET_ALL)
        mock_ansible_module.return_value = mock_ansible_instance

        NetworkSetFactsModule().run()

        mock_ov_instance.network_sets.get_all.assert_called_once_with()

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=False,
            ansible_facts=dict(network_sets=network_sets))

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_network_set_facts.AnsibleModule')
    def test_should_get_network_set_by_name(self, mock_ansible_module, mock_ov_client_from_json_file):
        network_sets = [{
            "name": "Network Set 1",
            "networkUris": ['/rest/ethernet-networks/aaa-bbb-ccc']
        }]
        mock_ov_instance = mock.Mock()
        mock_ov_instance.network_sets.get_by.return_value = network_sets

        mock_ov_client_from_json_file.return_value = mock_ov_instance

        mock_ansible_instance = create_ansible_mock(PARAMS_GET_BY_NAME)
        mock_ansible_module.return_value = mock_ansible_instance

        NetworkSetFactsModule().run()

        mock_ov_instance.network_sets.get_by.assert_called_once_with('name', 'Network Set 1')

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=False,
            ansible_facts=dict(network_sets=network_sets))

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_network_set_facts.AnsibleModule')
    def test_should_get_network_set_by_name_without_ethernet(self, mock_ansible_module, mock_ov_client_from_json_file):
        network_sets = [{
            "name": "Network Set 1",
            "networkUris": []
        }]
        mock_ov_instance = mock.Mock()
        mock_ov_instance.network_sets.get_all_without_ethernet.return_value = network_sets

        mock_ov_client_from_json_file.return_value = mock_ov_instance

        mock_ansible_instance = create_ansible_mock(PARAMS_GET_BY_NAME_WITHOUT_ETHERNET)
        mock_ansible_module.return_value = mock_ansible_instance

        NetworkSetFactsModule().run()

        expected_filter = "\"'name'='Network Set 1'\""
        mock_ov_instance.network_sets.get_all_without_ethernet.assert_called_once_with(filter=expected_filter)

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=False,
            ansible_facts=dict(network_sets=network_sets))

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_network_set_facts.AnsibleModule')
    def test_should_fail_when_get_all_raises_exception(self, mock_ansible_module, mock_ov_client_from_json_file):
        mock_ov_instance = mock.Mock()
        mock_ov_instance.network_sets.get_all.side_effect = Exception(ERROR_MSG)

        mock_ov_client_from_json_file.return_value = mock_ov_instance

        mock_ansible_instance = create_ansible_mock(PARAMS_GET_ALL)
        mock_ansible_module.return_value = mock_ansible_instance

        NetworkSetFactsModule().run()

        mock_ansible_instance.fail_json.assert_called_once()

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_network_set_facts.AnsibleModule')
    def test_should_fail_when_get_by_raises_exception(self, mock_ansible_module, mock_ov_client_from_json_file):
        mock_ov_instance = mock.Mock()
        mock_ov_instance.network_sets.get_by.side_effect = Exception(ERROR_MSG)

        mock_ov_client_from_json_file.return_value = mock_ov_instance

        mock_ansible_instance = create_ansible_mock(PARAMS_GET_BY_NAME)
        mock_ansible_module.return_value = mock_ansible_instance

        NetworkSetFactsModule().run()

        mock_ansible_instance.fail_json.assert_called_once()

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_network_set_facts.AnsibleModule')
    def test_should_fail_when_get_all_without_ethernet_raises_exception(self, mock_ansible_module,
                                                                        mock_ov_client_from_json_file):
        mock_ov_instance = mock.Mock()
        mock_ov_instance.network_sets.get_all_without_ethernet.side_effect = Exception(ERROR_MSG)

        mock_ov_client_from_json_file.return_value = mock_ov_instance

        mock_ansible_instance = create_ansible_mock(PARAMS_GET_BY_NAME_WITHOUT_ETHERNET)
        mock_ansible_module.return_value = mock_ansible_instance

        NetworkSetFactsModule().run()

        mock_ansible_instance.fail_json.assert_called_once()
