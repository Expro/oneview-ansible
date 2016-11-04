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
from oneview_sas_interconnect_facts import SasInterconnectFactsModule
from utils import create_ansible_mock


SAS_INTERCONNECT_1_NAME = '0000A66103, interconnect 1'

SAS_INTERCONNECT_1 = dict(
    name=SAS_INTERCONNECT_1_NAME,
    uri='/rest/sas-interconnects/2M220104SL'
)

SAS_INTERCONNECT_4 = dict(
    name='0000A66102, interconnect 4',
    uri='/rest/sas-interconnects/2M220103SL'
)

PARAMS_GET_ALL = dict(
    config='config.json',
    name=None
)

PARAMS_GET_BY_NAME = dict(
    config='config.json',
    name=SAS_INTERCONNECT_1_NAME
)


class SasInterconnectFactsSpec(unittest.TestCase):

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_sas_interconnect_facts.AnsibleModule')
    def test_get_all_sas_interconnects(self, mock_ansible_module, mock_ov_from_file):
        all_sas_interconnects = [SAS_INTERCONNECT_1, SAS_INTERCONNECT_4]

        mock_ov_instance = mock.Mock()
        mock_ov_from_file.return_value = mock_ov_instance

        mock_ov_instance.sas_interconnects.get_all.return_value = all_sas_interconnects

        mock_ansible_instance = create_ansible_mock(PARAMS_GET_ALL)
        mock_ansible_module.return_value = mock_ansible_instance

        SasInterconnectFactsModule().run()

        mock_ansible_instance.exit_json.assert_called_once_with(
            ansible_facts=dict(sas_interconnects=all_sas_interconnects)
        )

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_sas_interconnect_facts.AnsibleModule')
    def test_get_sas_interconnects_by_name(self, mock_ansible_module, mock_ov_from_file):
        mock_ov_instance = mock.Mock()
        mock_ov_from_file.return_value = mock_ov_instance

        mock_ov_instance.sas_interconnects.get_by.return_value = [SAS_INTERCONNECT_1]

        mock_ansible_instance = create_ansible_mock(PARAMS_GET_BY_NAME)
        mock_ansible_module.return_value = mock_ansible_instance

        SasInterconnectFactsModule().run()

        mock_ov_instance.sas_interconnects.get_by.assert_called_once_with('name', SAS_INTERCONNECT_1_NAME)

        mock_ansible_instance.exit_json.assert_called_once_with(
            ansible_facts=dict(sas_interconnects=[SAS_INTERCONNECT_1])
        )

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_sas_interconnect_facts.AnsibleModule')
    def test_error_handling(self, mock_ansible_module, mock_ov_from_file):
        mock_ov_instance = mock.Mock()
        mock_ov_from_file.return_value = mock_ov_instance

        error_msg = "Fake Error"
        mock_ov_instance.sas_interconnects.get_by.side_effect = Exception(error_msg)

        mock_ansible_instance = create_ansible_mock(PARAMS_GET_BY_NAME)
        mock_ansible_module.return_value = mock_ansible_instance

        SasInterconnectFactsModule().run()

        mock_ansible_instance.fail_json.assert_called_once_with(msg=error_msg)


class SasInterconnectsFactsClientConfigurationSpec(unittest.TestCase):

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch.object(OneViewClient, 'from_environment_variables')
    @mock.patch('oneview_sas_interconnect_facts.AnsibleModule')
    def test_should_load_config_from_file(self, mock_ansible_module, mock_ov_client_from_env_vars,
                                          mock_ov_client_from_json_file):
        mock_ov_instance = mock.Mock()
        mock_ov_client_from_json_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock({'config': 'config.json'})
        mock_ansible_module.return_value = mock_ansible_instance

        SasInterconnectFactsModule()

        mock_ov_client_from_json_file.assert_called_once_with('config.json')
        mock_ov_client_from_env_vars.not_been_called()

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch.object(OneViewClient, 'from_environment_variables')
    @mock.patch('oneview_sas_interconnect_facts.AnsibleModule')
    def test_should_load_config_from_environment(self, mock_ansible_module, mock_ov_client_from_env_vars,
                                                 mock_ov_client_from_json_file):
        mock_ov_instance = mock.Mock()

        mock_ov_client_from_env_vars.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock({'config': None})
        mock_ansible_module.return_value = mock_ansible_instance

        SasInterconnectFactsModule()

        mock_ov_client_from_env_vars.assert_called_once()
        mock_ov_client_from_json_file.not_been_called()

if __name__ == '__main__':
    unittest.main()
