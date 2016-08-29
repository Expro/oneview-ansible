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
import yaml

from hpOneView.oneview_client import OneViewClient
from oneview_logical_switch_group import LogicalSwitchGroupModule, LOGICAL_SWITCH_GROUP_CREATED, \
    LOGICAL_SWITCH_GROUP_DELETED, LOGICAL_SWITCH_GROUP_ALREADY_ABSENT, \
    SWITCH_TYPE_NOT_FOUND, \
    LOGICAL_SWITCH_GROUP_ALREADY_UPDATED, LOGICAL_SWITCH_GROUP_UPDATED

FAKE_MSG_ERROR = 'Fake message error'

SWITCH_TYPE_URI = '/rest/switch-types/2f36bc8f-65d8-4ea2-9300-750180402a5e'

YAML_LOGICAL_SWITCH_GROUP = """
        config: "{{ config }}"
        state: present
        data:
            type: "logical-switch-group"
            name: "OneView Test Logical Switch Group"
            switchMapTemplate:
                switchMapEntryTemplates:
                    - logicalLocation:
                        locationEntries:
                           - relativeValue: 1
                             type: "StackingMemberId"
                      permittedSwitchTypeName: 'Switch Type Name'
                      permittedSwitchTypeUri: '/rest/switch-types/2f36bc8f-65d8-4ea2-9300-750180402a5e'
          """

YAML_LOGICAL_SWITCH_GROUP_CHANGE = """
        config: "{{ config }}"
        state: present
        data:
            type: "logical-switch-group"
            name: "OneView Test Logical Switch Group"
            newName: "OneView Test Logical Switch Group (Changed)"
            switchMapTemplate:
                switchMapEntryTemplates:
                    - logicalLocation:
                        locationEntries:
                           - relativeValue: 1
                             type: "StackingMemberId"
                      permittedSwitchTypeUri: '/rest/switch-types/2f36bc8f-65d8-4ea2-9300-750180402a5e'
      """

YAML_LOGICAL_SWITCH_GROUP_ABSENT = """
        config: "{{ config }}"
        state: absent
        data:
            name: '{{storage_vol_templ_name}}'
        """

DICT_DEFAULT_LOGICAL_SWITCH_GROUP = yaml.load(YAML_LOGICAL_SWITCH_GROUP)["data"]
DICT_DEFAULT_LOGICAL_SWITCH_GROUP_CHANGED = yaml.load(YAML_LOGICAL_SWITCH_GROUP_CHANGE)["data"]


def create_ansible_mock(yaml_config):
    mock_ansible = mock.Mock()
    mock_ansible.params = yaml.load(yaml_config)
    return mock_ansible


class LogicalSwitchGroupPresentStateSpec(unittest.TestCase):
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_logical_switch_group.AnsibleModule')
    def test_should_create_new_logical_switch_group(self, mock_ansible_module, mock_ov_client_from_json_file):
        mock_ov_instance = mock.Mock()
        mock_ov_instance.logical_switch_groups.get_by.return_value = []
        mock_ov_instance.logical_switch_groups.create.return_value = {"name": "name"}
        mock_ov_instance.switch_types.get_by.return_value = [{'uri': SWITCH_TYPE_URI}]

        mock_ov_client_from_json_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(YAML_LOGICAL_SWITCH_GROUP)
        mock_ansible_module.return_value = mock_ansible_instance

        LogicalSwitchGroupModule().run()

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=True,
            msg=LOGICAL_SWITCH_GROUP_CREATED,
            ansible_facts=dict(logical_switch_group={"name": "name"})
        )

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_logical_switch_group.AnsibleModule')
    def test_should_update_the_logical_switch_group(self, mock_ansible_module, mock_ov_client_from_json_file):
        mock_ov_instance = mock.Mock()
        mock_ov_instance.logical_switch_groups.get_by.return_value = [DICT_DEFAULT_LOGICAL_SWITCH_GROUP]
        mock_ov_instance.logical_switch_groups.update.return_value = {"name": "name"}

        mock_ov_client_from_json_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(YAML_LOGICAL_SWITCH_GROUP_CHANGE)
        mock_ansible_module.return_value = mock_ansible_instance

        LogicalSwitchGroupModule().run()

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=True,
            msg=LOGICAL_SWITCH_GROUP_UPDATED,
            ansible_facts=dict(logical_switch_group={"name": "name"})
        )

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_logical_switch_group.AnsibleModule')
    def test_should_not_update_when_data_is_equals(self, mock_ansible_module, mock_ov_client_from_json_file):
        switch_type_replaced = DICT_DEFAULT_LOGICAL_SWITCH_GROUP.copy()
        del switch_type_replaced['switchMapTemplate']['switchMapEntryTemplates'][0]['permittedSwitchTypeName']

        mock_ov_instance = mock.Mock()
        mock_ov_instance.logical_switch_groups.get_by.return_value = [DICT_DEFAULT_LOGICAL_SWITCH_GROUP]
        mock_ov_instance.switch_types.get_by.return_value = [{'uri': SWITCH_TYPE_URI}]

        mock_ov_client_from_json_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(YAML_LOGICAL_SWITCH_GROUP)
        mock_ansible_module.return_value = mock_ansible_instance

        LogicalSwitchGroupModule().run()

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=False,
            msg=LOGICAL_SWITCH_GROUP_ALREADY_UPDATED,
            ansible_facts=dict(logical_switch_group=DICT_DEFAULT_LOGICAL_SWITCH_GROUP)
        )


class LogicalSwitchGroupAbsentStateSpec(unittest.TestCase):
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_logical_switch_group.AnsibleModule')
    def test_should_remove_logical_switch_group(self, mock_ansible_module, mock_ov_client_from_json_file):
        mock_ov_instance = mock.Mock()
        mock_ov_instance.logical_switch_groups.get_by.return_value = [DICT_DEFAULT_LOGICAL_SWITCH_GROUP]

        mock_ov_client_from_json_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(YAML_LOGICAL_SWITCH_GROUP_ABSENT)
        mock_ansible_module.return_value = mock_ansible_instance

        LogicalSwitchGroupModule().run()

        mock_ansible_instance.exit_json.assert_called_once_with(
            ansible_facts={},
            changed=True,
            msg=LOGICAL_SWITCH_GROUP_DELETED
        )

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_logical_switch_group.AnsibleModule')
    def test_should_do_nothing_when_logical_switch_group_not_exist(self, mock_ansible_module,
                                                                   mock_ov_client_from_json_file):
        mock_ov_instance = mock.Mock()
        mock_ov_instance.logical_switch_groups.get_by.return_value = []

        mock_ov_client_from_json_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(YAML_LOGICAL_SWITCH_GROUP_ABSENT)
        mock_ansible_module.return_value = mock_ansible_instance

        LogicalSwitchGroupModule().run()

        mock_ansible_instance.exit_json.assert_called_once_with(
            ansible_facts={},
            changed=False,
            msg=LOGICAL_SWITCH_GROUP_ALREADY_ABSENT
        )


class LogicalSwitchGroupErrorHandlingSpec(unittest.TestCase):
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_logical_switch_group.AnsibleModule')
    def test_should_fail_when_create_raises_exception(self, mock_ansible_module, mock_ov_client_from_json_file):
        mock_ov_instance = mock.Mock()
        mock_ov_instance.logical_switch_groups.get_by.return_value = []
        mock_ov_instance.logical_switch_groups.create.side_effect = Exception(FAKE_MSG_ERROR)
        mock_ov_instance.switch_types.get_by.return_value = [{'uri': SWITCH_TYPE_URI}]

        mock_ov_client_from_json_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(YAML_LOGICAL_SWITCH_GROUP)
        mock_ansible_module.return_value = mock_ansible_instance

        self.assertRaises(Exception, LogicalSwitchGroupModule().run())

        mock_ansible_instance.fail_json.assert_called_once_with(
            msg=FAKE_MSG_ERROR
        )

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_logical_switch_group.AnsibleModule')
    def test_should_fail_when_switch_type_was_not_found(self, mock_ansible_module, mock_ov_client_from_json_file):
        mock_ov_instance = mock.Mock()
        mock_ov_instance.logical_switch_groups.get_by.return_value = []
        mock_ov_instance.logical_switch_groups.create.side_effect = Exception(FAKE_MSG_ERROR)
        mock_ov_instance.switch_types.get_by.return_value = []

        mock_ov_client_from_json_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(YAML_LOGICAL_SWITCH_GROUP)
        mock_ansible_module.return_value = mock_ansible_instance

        self.assertRaises(Exception, LogicalSwitchGroupModule().run())

        mock_ansible_instance.fail_json.assert_called_once_with(
            msg=SWITCH_TYPE_NOT_FOUND
        )

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_logical_switch_group.AnsibleModule')
    def test_should_fail_when_delete_raises_exception(self, mock_ansible_module, mock_ov_client_from_json_file):
        mock_ov_instance = mock.Mock()
        mock_ov_instance.logical_switch_groups.get_by.return_value = [DICT_DEFAULT_LOGICAL_SWITCH_GROUP]
        mock_ov_instance.logical_switch_groups.delete.side_effect = Exception(FAKE_MSG_ERROR)

        mock_ov_client_from_json_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(YAML_LOGICAL_SWITCH_GROUP_ABSENT)
        mock_ansible_module.return_value = mock_ansible_instance

        self.assertRaises(Exception, LogicalSwitchGroupModule().run())

        mock_ansible_instance.fail_json.assert_called_once_with(
            msg=FAKE_MSG_ERROR
        )


if __name__ == '__main__':
    unittest.main()
