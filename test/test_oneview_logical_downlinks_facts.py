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

from utils import create_ansible_mock

from hpOneView.oneview_client import OneViewClient
from oneview_logical_downlinks_facts import LogicalDownlinksFactsModule


ERROR_MSG = 'Fake message error'

LOGICAL_DOWNLINK_URI = "/rest/logical-downlinks/97cb2d39-55a0-47b0-83b2-7feaefcd720d"
LOGICAL_DOWNLINK_NAME = "LD415a472f-ed77-42cc-9a5e-b9bd5d096923 (HP VC FlexFabric-20/40 F8 Module)"

LOGICAL_DOWNLINK = dict(name=LOGICAL_DOWNLINK_NAME, uri=LOGICAL_DOWNLINK_URI)

PARAMS_FOR_GET_ALL = dict(
    config='config.json',
    name=None,
    excludeEthernet=False
)

PARAMS_FOR_GET_BY_NAME = dict(
    config='config.json',
    name=LOGICAL_DOWNLINK_NAME,
    excludeEthernet=False
)

PARAMS_FOR_GET_ALL_WITHOUT_ETHERNET = dict(
    config='config.json',
    name=None,
    excludeEthernet=True
)

PARAMS_FOR_GET_WITHOUT_ETHERNET = dict(
    config='config.json',
    name=LOGICAL_DOWNLINK_NAME,
    excludeEthernet=True
)


class LogicalDownlinksFactsSpec(unittest.TestCase):

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_logical_downlinks_facts.AnsibleModule')
    def test_should_get_all_logical_downlinks(self, mock_ansible_module, mock_ov_from_file):
        logical_downlinks = [
            dict(name="test1"),
            dict(name="test2")
        ]

        mock_ov_instance = mock.Mock()
        mock_ov_instance.logical_downlinks.get_all.return_value = logical_downlinks

        mock_ov_from_file.return_value = mock_ov_instance

        mock_ansible_instance = create_ansible_mock(PARAMS_FOR_GET_ALL)
        mock_ansible_module.return_value = mock_ansible_instance

        LogicalDownlinksFactsModule().run()

        mock_ov_instance.logical_downlinks.get_all.assert_called_once()

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=False,
            ansible_facts=dict(logical_downlinks=logical_downlinks)
        )

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_logical_downlinks_facts.AnsibleModule')
    def test_should_fail_when_get_all_raises_exception(self, mock_ansible_module, mock_ov_from_file):
        mock_ov_instance = mock.Mock()
        mock_ov_instance.logical_downlinks.get_all.side_effect = Exception(ERROR_MSG)

        mock_ov_from_file.return_value = mock_ov_instance

        mock_ansible_instance = create_ansible_mock(PARAMS_FOR_GET_ALL)
        mock_ansible_module.return_value = mock_ansible_instance

        LogicalDownlinksFactsModule().run()

        mock_ansible_instance.fail_json.assert_called_once_with(msg=ERROR_MSG)

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_logical_downlinks_facts.AnsibleModule')
    def test_should_get_by_name(self, mock_ansible_module, mock_ov_from_file):
        logical_downlinks = [LOGICAL_DOWNLINK]

        mock_ov_instance = mock.Mock()
        mock_ov_instance.logical_downlinks.get_by.return_value = logical_downlinks

        mock_ov_from_file.return_value = mock_ov_instance

        mock_ansible_instance = create_ansible_mock(PARAMS_FOR_GET_BY_NAME)
        mock_ansible_module.return_value = mock_ansible_instance

        LogicalDownlinksFactsModule().run()

        mock_ov_instance.logical_downlinks.get_by.assert_called_once_with("name", LOGICAL_DOWNLINK_NAME)

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=False,
            ansible_facts=dict(logical_downlinks=logical_downlinks)
        )

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_logical_downlinks_facts.AnsibleModule')
    def test_should_fail_when_get_by_raises_exception(self, mock_ansible_module, mock_ov_from_file):
        mock_ov_instance = mock.Mock()
        mock_ov_instance.logical_downlinks.get_by.side_effect = Exception(ERROR_MSG)

        mock_ov_from_file.return_value = mock_ov_instance

        mock_ansible_instance = create_ansible_mock(PARAMS_FOR_GET_BY_NAME)
        mock_ansible_module.return_value = mock_ansible_instance

        LogicalDownlinksFactsModule().run()

        mock_ansible_instance.fail_json.assert_called_once_with(msg=ERROR_MSG)

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_logical_downlinks_facts.AnsibleModule')
    def test_should_get_all_without_ethernet(self, mock_ansible_module, mock_ov_from_file):
        logical_downlinks = [LOGICAL_DOWNLINK]

        mock_ov_instance = mock.Mock()
        mock_ov_instance.logical_downlinks.get_all_without_ethernet.return_value = logical_downlinks

        mock_ov_from_file.return_value = mock_ov_instance

        mock_ansible_instance = create_ansible_mock(PARAMS_FOR_GET_ALL_WITHOUT_ETHERNET)
        mock_ansible_module.return_value = mock_ansible_instance

        LogicalDownlinksFactsModule().run()

        mock_ov_instance.logical_downlinks.get_all_without_ethernet.assert_called_once()

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=False,
            ansible_facts=dict(logical_downlinks=logical_downlinks)
        )

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_logical_downlinks_facts.AnsibleModule')
    def test_should_get_without_ethernet(self, mock_ansible_module, mock_ov_from_file):
        logical_downlinks = [LOGICAL_DOWNLINK]
        logical_downlinks_without_ethernet = []

        mock_ov_instance = mock.Mock()
        mock_ov_instance.logical_downlinks.get_by.return_value = logical_downlinks
        mock_ov_instance.logical_downlinks.get_without_ethernet.return_value = logical_downlinks_without_ethernet

        mock_ov_from_file.return_value = mock_ov_instance

        mock_ansible_instance = create_ansible_mock(PARAMS_FOR_GET_WITHOUT_ETHERNET)
        mock_ansible_module.return_value = mock_ansible_instance

        LogicalDownlinksFactsModule().run()

        mock_ov_instance.logical_downlinks.get_by.assert_called_once_with('name', LOGICAL_DOWNLINK_NAME)
        mock_ov_instance.logical_downlinks.get_without_ethernet.assert_called_once_with(id_or_uri=LOGICAL_DOWNLINK_URI)

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=False,
            ansible_facts=dict(logical_downlinks=logical_downlinks_without_ethernet)
        )


if __name__ == '__main__':
    unittest.main()
