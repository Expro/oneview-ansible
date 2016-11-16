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

from copy import deepcopy
from mock import patch
from test.utils import create_ansible_mock

from hpOneView.oneview_client import OneViewClient
from hpOneView.exceptions import HPOneViewTaskError
from oneview_server_profile import ServerProfileModule
from oneview_server_profile import MAKE_COMPLIANT_NOT_SUPPORTED, SERVER_PROFILE_CREATED, REMEDIATED_COMPLIANCE, \
    ALREADY_COMPLIANT, SERVER_PROFILE_DELETED, SERVER_PROFILE_UPDATED, SERVER_ALREADY_UPDATED, \
    ERROR_ALLOCATE_SERVER_HARDWARE

SERVER_PROFILE_NAME = "Profile101"
SERVER_PROFILE_URI = "/rest/server-profiles/94B55683-173F-4B36-8FA6-EC250BA2328B"
SHT_URI = "/rest/server-hardware-types/94B55683-173F-4B36-8FA6-EC250BA2328B"
ENCLOSURE_GROUP_URI = "/rest/enclosure-groups/ad5e9e88-b858-4935-ba58-017d60a17c89"
TEMPLATE_URI = '/rest/server-profile-templates/9a156b04-fce8-40b0-b0cd-92ced1311dda'
FAKE_SERVER_HARDWARE = {'uri': '/rest/server-hardware/31393736-3831-4753-567h-30335837524E'}

MESSAGE_COMPLIANT_ERROR = MAKE_COMPLIANT_NOT_SUPPORTED.format(SERVER_PROFILE_NAME)
FAKE_MSG_ERROR = 'Fake message error'

TASK_ERROR = HPOneViewTaskError(msg=FAKE_MSG_ERROR, error_code='AssignProfileToDeviceBayError')

BASIC_PROFILE = dict(
    name=SERVER_PROFILE_NAME,
    serverHardwareTypeUri=SHT_URI,
    enclosureGroupUri=ENCLOSURE_GROUP_URI,
    uri=SERVER_PROFILE_URI
)

BASIC_TEMPLATE = dict(
    name="Server-Template-7000",
    serverHardwareTypeUri=SHT_URI,
    enclosureGroupUri=ENCLOSURE_GROUP_URI,
    uri='/rest/server-profile-templates/9a156b04-fce8-40b0-b0cd-92ced1311dda'
)

PARAMS_FOR_PRESENT = dict(
    config='config.json',
    state='present',
    data=BASIC_PROFILE
)

PARAMS_FOR_COMPLIANT = dict(
    config='config.json',
    state='compliant',
    data=dict(name="Server-Template-7000")
)

PARAMS_FOR_ABSENT = dict(
    config='config.json',
    state='absent',
    data=dict(name="Server-Template-7000")
)

CREATED_BASIC_PROFILE = dict(
    affinity="Bay",
    bios=dict(manageBios=False, overriddenSettings=[]),
    boot=dict(manageBoot=False, order=[]),
    bootMode=dict(manageMode=False, mode=None, pxeBootPolicy=None),
    category="server-profile-templates",
    enclosureGroupUri="/rest/enclosure-groups/ad5e9e88-b858-4935-ba58-017d60a17c89",
    name=SERVER_PROFILE_NAME,
    serialNumber='VCGGU8800W',
    serialNumberType="Virtual",
    serverHardwareTypeUri="/rest/server-hardware-types/94B55683-173F-4B36-8FA6-EC250BA2328B",
    serverHardwareUri='/rest/server-hardware/37333036-3831-76jh-4831-303658389766',
    status="OK",
    type="ServerProfileV5",
    uri="/rest/server-profiles/57d3af2a-b6d2-4446-8645-f38dd808ea490",
    serverProfileTemplateUri='/rest/server-profile-templates/9a156b04-fce8-40b0-b0cd-92ced1311dda',
    templateCompliance='Compliant',
    wwnType="Virtual"
)

AVAILABLE_TARGETS = dict(
    category='available-targets',
    targets=[
        dict(enclosureBay=2, serverHardwareUri=''),
        dict(enclosureBay=3, serverHardwareUri='/rest/server-hardware/31393736-3831-4753-567h-30335837524E'),
        dict(enclosureBay=4, serverHardwareUri='/rest/server-hardware/37333036-3831-6776-gdfd-3037583rewr0'),
        dict(enclosureBay=8, serverHardwareUri='/rest/server-hardware/37333036-3831-4753-4831-303158sdf458'),
    ]
)


def gather_facts(mock_ov_instance, created=False, online_update=True):
    compliance_preview = {
        'automaticUpdates': ['fake change.'],
        'isOnlineUpdate': online_update,
        'manualUpdates': [],
        'type': 'ServerProfileCompliancePreviewV1'
    }

    mock_ov_instance.server_profiles.get_compliance_preview.return_value = compliance_preview
    mock_ov_instance.server_hardware.get.return_value = {}
    facts = {
        'serial_number': CREATED_BASIC_PROFILE.get('serialNumber'),
        'server_profile': CREATED_BASIC_PROFILE,
        'server_hardware': {},
        'compliance_preview': compliance_preview,
        'created': created
    }

    return facts


class ServerProfileClientConfigurationSpec(unittest.TestCase):
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch.object(OneViewClient, 'from_environment_variables')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_load_config_from_file(self, mock_ansible_module, mock_ov_client_from_env_vars,
                                          mock_ov_client_from_json_file):
        mock_ov_instance = mock.Mock()
        mock_ov_client_from_json_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock({'config': 'config.json'})
        mock_ansible_module.return_value = mock_ansible_instance

        ServerProfileModule()

        mock_ov_client_from_json_file.assert_called_once_with('config.json')
        mock_ov_client_from_env_vars.not_been_called()

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch.object(OneViewClient, 'from_environment_variables')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_load_config_from_environment(self, mock_ansible_module, mock_ov_client_from_env_vars,
                                                 mock_ov_client_from_json_file):
        mock_ov_instance = mock.Mock()

        mock_ov_client_from_env_vars.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock({'config': None})
        mock_ansible_module.return_value = mock_ansible_instance

        ServerProfileModule()

        mock_ov_client_from_env_vars.assert_called_once()
        mock_ov_client_from_json_file.not_been_called()


class ServerProfileCompliantStateSpec(unittest.TestCase):
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_fail_when_server_not_associated_with_template(
            self, mock_ansible_module, mock_ov_from_file):
        mock_server = deepcopy(CREATED_BASIC_PROFILE)
        mock_server['templateCompliance'] = 'Unknown'
        mock_server['serverProfileTemplateUri'] = ''

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = mock_server
        mock_ov_from_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(PARAMS_FOR_COMPLIANT)
        mock_ansible_module.return_value = mock_ansible_instance

        ServerProfileModule().run()

        mock_ansible_instance.fail_json.assert_called_once_with(msg=MESSAGE_COMPLIANT_ERROR)

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_not_update_when_already_compliant(self, mock_ansible_module, mock_ov_from_file):
        mock_server = deepcopy(CREATED_BASIC_PROFILE)

        params_compliant = deepcopy(PARAMS_FOR_COMPLIANT)

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = mock_server
        mock_ov_from_file.return_value = mock_ov_instance
        mock_facts = gather_facts(mock_ov_instance)
        mock_ansible_instance = create_ansible_mock(params_compliant)
        mock_ansible_module.return_value = mock_ansible_instance

        ServerProfileModule().run()

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=False, msg=ALREADY_COMPLIANT, ansible_facts=mock_facts)

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_update_when_not_compliant(self, mock_ansible_module, mock_ov_from_file):
        mock_server = deepcopy(CREATED_BASIC_PROFILE)
        mock_server['templateCompliance'] = 'NonCompliant'

        params_compliant = deepcopy(PARAMS_FOR_COMPLIANT)

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = mock_server
        mock_ov_instance.server_profiles.patch.return_value = CREATED_BASIC_PROFILE
        mock_ov_from_file.return_value = mock_ov_instance
        mock_facts = gather_facts(mock_ov_instance)
        mock_ansible_instance = create_ansible_mock(params_compliant)
        mock_ansible_module.return_value = mock_ansible_instance

        ServerProfileModule().run()

        mock_ov_instance.server_profiles.patch.assert_called_once_with(
            CREATED_BASIC_PROFILE['uri'], 'replace', '/templateCompliance', 'Compliant')

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=True, msg=REMEDIATED_COMPLIANCE, ansible_facts=mock_facts)

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_power_off_when_is_offline_update(self, mock_ansible_module, mock_ov_from_file):
        mock_server = deepcopy(CREATED_BASIC_PROFILE)
        mock_server['templateCompliance'] = 'NonCompliant'

        params_compliant = deepcopy(PARAMS_FOR_COMPLIANT)

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = mock_server
        mock_ov_instance.server_profiles.patch.return_value = CREATED_BASIC_PROFILE
        mock_ov_instance.server_hardware.update_power_state.return_value = {}
        mock_ov_from_file.return_value = mock_ov_instance

        # shoud power off server to update
        mock_facts = gather_facts(mock_ov_instance, online_update=False)

        mock_ansible_instance = create_ansible_mock(params_compliant)
        mock_ansible_module.return_value = mock_ansible_instance

        ServerProfileModule().run()

        mock_ov_instance.server_profiles.patch.assert_called_once_with(
            CREATED_BASIC_PROFILE['uri'], 'replace', '/templateCompliance', 'Compliant')

        power_set_calls = [
            mock.call(dict(powerState='Off', powerControl='PressAndHold'), mock_server['serverHardwareUri']),
            mock.call(dict(powerState='On', powerControl='MomentaryPress'), mock_server['serverHardwareUri'])]
        mock_ov_instance.server_hardware.update_power_state.assert_has_calls(power_set_calls)

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=True, msg=REMEDIATED_COMPLIANCE, ansible_facts=mock_facts)

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_fail_when_oneview_client_raises_exception(self, mock_ansible_module, mock_ov_from_file):
        mock_server = deepcopy(CREATED_BASIC_PROFILE)
        mock_server['templateCompliance'] = 'NonCompliant'

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = mock_server
        mock_ov_instance.server_profiles.patch.side_effect = Exception(FAKE_MSG_ERROR)
        mock_ov_from_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(PARAMS_FOR_COMPLIANT)
        mock_ansible_module.return_value = mock_ansible_instance

        self.assertRaises(Exception, ServerProfileModule().run())

        mock_ansible_instance.fail_json.assert_called_once_with(msg=FAKE_MSG_ERROR)


class ServerProfileCreateSpec(unittest.TestCase):
    @mock.patch('time.sleep', return_value=None)
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_create_with_automatically_selected_hardware_when_not_exists(
            self, mock_module, mock_ov_from_file, mock_sleep):
        profile_data = deepcopy(BASIC_PROFILE)
        profile_data['serverHardwareUri'] = '/rest/server-hardware/31393736-3831-4753-567h-30335837524E'

        params_for_present = deepcopy(PARAMS_FOR_PRESENT)

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = None
        mock_ov_instance.server_profiles.create.return_value = CREATED_BASIC_PROFILE
        mock_ov_instance.server_profiles.get_available_targets.return_value = AVAILABLE_TARGETS
        mock_ov_from_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(params_for_present)
        mock_module.return_value = mock_ansible_instance
        mock_facts = gather_facts(mock_ov_instance, created=True)

        ServerProfileModule().run()

        mock_ov_instance.server_profiles.create.assert_called_once_with(profile_data)

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=True,
            msg=SERVER_PROFILE_CREATED,
            ansible_facts=mock_facts
        )

    @mock.patch('time.sleep', return_value=None)
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_create_from_template_with_automatically_selected_hardware_when_not_exists(
            self, mock_ansible_module, mock_ov_from_file, mock_sleep):
        template = deepcopy(BASIC_TEMPLATE)

        profile_from_template = deepcopy(BASIC_PROFILE)

        profile_data = deepcopy(BASIC_PROFILE)
        profile_data['serverHardwareUri'] = '/rest/server-hardware/31393736-3831-4753-567h-30335837524E'

        param_for_present = deepcopy(PARAMS_FOR_PRESENT)
        param_for_present['data']['server_template'] = 'Server-Template-7000'

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = None
        mock_ov_instance.server_profiles.create.return_value = CREATED_BASIC_PROFILE
        mock_ov_instance.server_profiles.get_available_targets.return_value = AVAILABLE_TARGETS
        mock_ov_instance.server_profile_templates.get_by_name.return_value = template
        mock_ov_instance.server_profile_templates.get_new_profile.return_value = profile_from_template
        mock_ov_instance.server_hardware.update_power_state.return_value = {}
        mock_ov_from_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(param_for_present)
        mock_ansible_module.return_value = mock_ansible_instance
        mock_facts = gather_facts(mock_ov_instance, created=True)

        ServerProfileModule().run()

        mock_ov_instance.server_profiles.create.assert_called_once_with(profile_data)

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=True,
            msg=SERVER_PROFILE_CREATED,
            ansible_facts=mock_facts
        )

    @mock.patch('time.sleep', return_value=None)
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_create_from_template_uri_with_automatically_selected_hardware_when_not_exists(
            self, mock_ansible_module, mock_ov_from_file, mock_sleep):
        template = deepcopy(BASIC_TEMPLATE)

        profile_from_template = deepcopy(BASIC_PROFILE)

        profile_data = deepcopy(BASIC_PROFILE)
        profile_data['serverHardwareUri'] = '/rest/server-hardware/31393736-3831-4753-567h-30335837524E'

        param_for_present = deepcopy(PARAMS_FOR_PRESENT)
        param_for_present['data']['serverProfileTemplateUri'] \
            = '/rest/server-profile-templates/31393736-3831-4753-567h-30335837524E'

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = None
        mock_ov_instance.server_profiles.create.return_value = CREATED_BASIC_PROFILE
        mock_ov_instance.server_profiles.get_available_targets.return_value = AVAILABLE_TARGETS
        mock_ov_instance.server_profile_templates.get.return_value = template
        mock_ov_instance.server_profile_templates.get_new_profile.return_value = profile_from_template
        mock_ov_instance.server_hardware.update_power_state.return_value = {}
        mock_ov_from_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(param_for_present)
        mock_ansible_module.return_value = mock_ansible_instance
        mock_facts = gather_facts(mock_ov_instance, created=True)

        ServerProfileModule().run()

        mock_ov_instance.server_profiles.create.assert_called_once_with(profile_data)

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=True,
            msg=SERVER_PROFILE_CREATED,
            ansible_facts=mock_facts
        )

    @mock.patch('time.sleep', return_value=None)
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_create_with_informed_hardware_when_not_exists(self, mock_module, mock_ov_from_file, mock_sleep):
        profile_data = deepcopy(BASIC_PROFILE)
        profile_data['serverHardwareUri'] = '/rest/server-hardware/31393736-3831-4753-567h-30335837524E'

        present = deepcopy(PARAMS_FOR_PRESENT)
        present['data']['server_hardware'] = "ServerHardwareName"

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = None
        mock_ov_instance.server_profiles.create.return_value = CREATED_BASIC_PROFILE
        mock_ov_instance.server_hardware.get_by.return_value = [FAKE_SERVER_HARDWARE]
        mock_ov_from_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(present)
        mock_module.return_value = mock_ansible_instance
        mock_facts = gather_facts(mock_ov_instance, created=True)

        ServerProfileModule().run()

        mock_ov_instance.server_profiles.create.assert_called_once_with(profile_data)

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=True,
            msg=SERVER_PROFILE_CREATED,
            ansible_facts=mock_facts
        )

    @mock.patch('time.sleep', return_value=None)
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_create_with_informed_hardware_and_template_when_not_exists(
            self, mock_module, mock_ov_from_file, mock_sleep):
        profile_data = deepcopy(BASIC_PROFILE)
        profile_data['serverHardwareUri'] = '/rest/server-hardware/31393736-3831-4753-567h-30335837524E'

        template = deepcopy(BASIC_TEMPLATE)

        profile_from_template = deepcopy(BASIC_PROFILE)

        present = deepcopy(PARAMS_FOR_PRESENT)
        present['data']['server_hardware'] = "ServerHardwareName"
        present['data']['server_template'] = "TemplateA200"

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = None
        mock_ov_instance.server_profiles.create.return_value = CREATED_BASIC_PROFILE
        mock_ov_instance.server_hardware.get_by.return_value = [FAKE_SERVER_HARDWARE]
        mock_ov_instance.server_profile_templates.get_by_name.return_value = template
        mock_ov_instance.server_profile_templates.get_new_profile.return_value = profile_from_template
        mock_ov_from_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(present)
        mock_module.return_value = mock_ansible_instance
        mock_facts = gather_facts(mock_ov_instance, created=True)

        ServerProfileModule().run()

        mock_ov_instance.server_profiles.create.assert_called_once_with(profile_data)

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=True,
            msg=SERVER_PROFILE_CREATED,
            ansible_facts=mock_facts
        )

    @mock.patch('time.sleep', return_value=None)
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_try_create_with_informed_hardware_25_times_when_not_exists(
            self, mock_module, mock_ov_from_file, mock_sleep):
        present = deepcopy(PARAMS_FOR_PRESENT)
        present['data']['server_hardware'] = "ServerHardwareName"

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = None
        mock_ov_instance.server_profiles.create.side_effect = TASK_ERROR
        mock_ov_instance.server_hardware.get_by.return_value = [FAKE_SERVER_HARDWARE]
        mock_ov_from_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(present)
        mock_module.return_value = mock_ansible_instance

        ServerProfileModule().run()

        times_get_targets_called = mock_ov_instance.server_profiles.get_available_targets.call_count
        self.assertEqual(0, times_get_targets_called)

        times_create_called = mock_ov_instance.server_profiles.create.call_count
        self.assertEqual(25, times_create_called)

        mock_ansible_instance.fail_json.assert_called_once_with(
            msg=ERROR_ALLOCATE_SERVER_HARDWARE

        )

    @mock.patch('time.sleep', return_value=None)
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_try_create_with_informed_hardware_2_times_when_not_exists(
            self, mock_module, mock_ov_from_file, mock_sleep):
        profile_data = deepcopy(BASIC_PROFILE)
        profile_data['serverHardwareUri'] = '/rest/server-hardware/31393736-3831-4753-567h-30335837524E'

        present = deepcopy(PARAMS_FOR_PRESENT)
        present['data']['server_hardware'] = "ServerHardwareName"

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = None
        mock_ov_instance.server_profiles.create.side_effect = [TASK_ERROR, CREATED_BASIC_PROFILE]
        mock_ov_instance.server_hardware.get_by.return_value = [FAKE_SERVER_HARDWARE]
        mock_ov_from_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(present)
        mock_module.return_value = mock_ansible_instance
        mock_facts = gather_facts(mock_ov_instance, created=True)

        ServerProfileModule().run()

        times_get_targets_called = mock_ov_instance.server_profiles.get_available_targets.call_count
        self.assertEqual(0, times_get_targets_called)

        create_calls = [mock.call(profile_data), mock.call(profile_data)]
        mock_ov_instance.server_profiles.create.assert_has_calls(create_calls)

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=True,
            msg=SERVER_PROFILE_CREATED,
            ansible_facts=mock_facts
        )

    @mock.patch('time.sleep', return_value=None)
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_try_create_with_automatically_selected_hardware_25_times_when_not_exists(
            self, mock_module, mock_ov_from_file, mock_sleep):
        present = deepcopy(PARAMS_FOR_PRESENT)

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = None
        mock_ov_instance.server_profiles.create.side_effect = TASK_ERROR
        mock_ov_instance.server_profiles.get_available_targets.return_value = AVAILABLE_TARGETS
        mock_ov_instance.server_hardware.get_by.return_value = [FAKE_SERVER_HARDWARE]
        mock_ov_from_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(present)
        mock_module.return_value = mock_ansible_instance

        ServerProfileModule().run()

        times_get_targets_called = mock_ov_instance.server_profiles.get_available_targets.call_count
        self.assertEqual(25, times_get_targets_called)

        times_create_called = mock_ov_instance.server_profiles.create.call_count
        self.assertEqual(25, times_create_called)

        mock_ansible_instance.fail_json.assert_called_once_with(
            msg=ERROR_ALLOCATE_SERVER_HARDWARE

        )

    @mock.patch('time.sleep', return_value=None)
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_fail_when_exception_is_not_related_with_server_hardware(
            self, mock_module, mock_ov_from_file, mock_sleep):
        present = deepcopy(PARAMS_FOR_PRESENT)

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = None
        mock_ov_instance.server_profiles.create.side_effect = Exception(FAKE_MSG_ERROR)
        mock_ov_instance.server_profiles.get_available_targets.return_value = AVAILABLE_TARGETS
        mock_ov_instance.server_hardware.get_by.return_value = [FAKE_SERVER_HARDWARE]
        mock_ov_from_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(present)
        mock_module.return_value = mock_ansible_instance

        ServerProfileModule().run()

        times_get_targets_called = mock_ov_instance.server_profiles.get_available_targets.call_count
        self.assertEqual(1, times_get_targets_called)

        times_create_called = mock_ov_instance.server_profiles.create.call_count
        self.assertEqual(1, times_create_called)

        mock_ansible_instance.fail_json.assert_called_once_with(
            msg=FAKE_MSG_ERROR

        )

    @mock.patch('time.sleep', return_value=None)
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_fail_when_informed_template_not_exist(self, mock_module, mock_ov_from_file, mock_sleep):
        present = deepcopy(PARAMS_FOR_PRESENT)
        present['data']['server_hardware'] = "ServerHardwareName"
        present['data']['server_template'] = "TemplateA200"

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = None
        mock_ov_instance.server_hardware.get_by.return_value = [FAKE_SERVER_HARDWARE]
        mock_ov_instance.server_profile_templates.get_by_name.return_value = None

        mock_ov_from_file.return_value = mock_ov_instance

        mock_ansible_instance = create_ansible_mock(present)
        mock_module.return_value = mock_ansible_instance

        ServerProfileModule().run()

        mock_ansible_instance.fail_json.assert_called_once_with(
            msg="Informed Server Profile Template 'TemplateA200' not found")

    @mock.patch('time.sleep', return_value=None)
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_fail_when_informed_hardware_not_exist(self, mock_module, mock_ov_from_file, mock_sleep):
        present = deepcopy(PARAMS_FOR_PRESENT)
        present['data']['server_hardware'] = "ServerHardwareName"
        present['data']['server_template'] = "TemplateA200"

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = None
        mock_ov_instance.server_hardware.get_by.return_value = None
        mock_ov_instance.server_profile_templates.get_by_name.return_value = BASIC_TEMPLATE

        mock_ov_from_file.return_value = mock_ov_instance

        mock_ansible_instance = create_ansible_mock(present)
        mock_module.return_value = mock_ansible_instance

        ServerProfileModule().run()

        mock_ansible_instance.fail_json.assert_called_once_with(
            msg="Informed Server Hardware 'ServerHardwareName' not found")

    @mock.patch('time.sleep', return_value=None)
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_create_without_hardware_when_there_are_any_available(
            self, mock_ansible_module, mock_ov_from_file, mock_sleep):
        available_targets = deepcopy(AVAILABLE_TARGETS)
        available_targets['targets'] = []

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = None
        mock_ov_instance.server_profiles.create.return_value = CREATED_BASIC_PROFILE
        mock_ov_instance.server_profiles.get_available_targets.return_value = available_targets
        mock_ov_instance.server_hardware.update_power_state.return_value = {}
        mock_ov_from_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(deepcopy(PARAMS_FOR_PRESENT))
        mock_ansible_module.return_value = mock_ansible_instance
        mock_facts = gather_facts(mock_ov_instance, created=True)

        ServerProfileModule().run()

        mock_ov_instance.server_profiles.create.assert_called_once_with(deepcopy(BASIC_PROFILE))
        power_set_calls = mock_ov_instance.server_hardware.update_power_state.call_count
        self.assertEqual(0, power_set_calls)

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=True,
            msg=SERVER_PROFILE_CREATED,
            ansible_facts=mock_facts
        )


class ServerProfileUpdateSpec(unittest.TestCase):
    @mock.patch('oneview_server_profile.resource_compare')
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_update_when_data_changed(self, mock_module, mock_ov_from_file, mock_resource_compare):
        profile_data = deepcopy(BASIC_PROFILE)

        params_for_present = deepcopy(PARAMS_FOR_PRESENT)

        mock_resource_compare.return_value = False

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = profile_data
        mock_ov_instance.server_profiles.update.return_value = CREATED_BASIC_PROFILE
        mock_ov_instance.server_hardware.update_power_state.return_value = {}

        mock_ov_from_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(params_for_present)
        mock_module.return_value = mock_ansible_instance

        mock_facts = gather_facts(mock_ov_instance)

        ServerProfileModule().run()

        mock_ov_instance.server_profiles.update.assert_called_once_with(profile_data, SERVER_PROFILE_URI)

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=True,
            msg=SERVER_PROFILE_UPDATED,
            ansible_facts=mock_facts
        )

    @mock.patch('oneview_server_profile.resource_compare')
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_power_off_before_update_when_data_changed(self, mock_module, mock_ov_from_file,
                                                              mock_resource_compare):
        mock_profile_data = deepcopy(BASIC_PROFILE)
        mock_profile_data['serverHardwareUri'] = SHT_URI

        params_for_present = deepcopy(PARAMS_FOR_PRESENT)

        mock_resource_compare.return_value = False

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = mock_profile_data
        mock_ov_instance.server_profiles.update.return_value = CREATED_BASIC_PROFILE
        mock_ov_instance.server_hardware.update_power_state.return_value = {}
        mock_ov_from_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(params_for_present)
        mock_module.return_value = mock_ansible_instance
        mock_facts = gather_facts(mock_ov_instance)

        ServerProfileModule().run()

        power_set_calls = [
            mock.call(dict(powerState='Off', powerControl='PressAndHold'), SHT_URI),
            mock.call(dict(powerState='On', powerControl='MomentaryPress'), SHT_URI)]
        mock_ov_instance.server_hardware.update_power_state.assert_has_calls(power_set_calls)

        mock_ov_instance.server_profiles.update.assert_called_once_with(mock_profile_data, SERVER_PROFILE_URI)

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=True,
            msg=SERVER_PROFILE_UPDATED,
            ansible_facts=mock_facts
        )

    @mock.patch('oneview_server_profile.resource_compare')
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_not_update_when_data_is_equals(self, mock_module, mock_ov_from_file, mock_resource_compare):
        profile_data = deepcopy(CREATED_BASIC_PROFILE)
        params_for_present = deepcopy(PARAMS_FOR_PRESENT)

        mock_ov_instance = mock.Mock()

        mock_ov_from_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(params_for_present)
        mock_module.return_value = mock_ansible_instance
        mock_resource_compare.return_value = True

        mock_facts = gather_facts(mock_ov_instance)
        mock_ov_instance.server_profiles.get_by_name.return_value = profile_data

        ServerProfileModule().run()

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=False,
            msg=SERVER_ALREADY_UPDATED,
            ansible_facts=mock_facts
        )

    @mock.patch('oneview_server_profile.resource_compare')
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_fail_when_informed_template_not_exist(self, mock_module, mock_ov_from_file, mock_resource_compare):
        profile_data = deepcopy(CREATED_BASIC_PROFILE)

        present = deepcopy(PARAMS_FOR_PRESENT)
        present['data']['server_hardware'] = "ServerHardwareName"
        present['data']['server_template'] = "TemplateA200"

        mock_resource_compare.return_value = False

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = profile_data
        mock_ov_instance.server_hardware.get_by.return_value = [FAKE_SERVER_HARDWARE]
        mock_ov_instance.server_profile_templates.get_by_name.return_value = None

        mock_ov_from_file.return_value = mock_ov_instance

        mock_ansible_instance = create_ansible_mock(present)
        mock_module.return_value = mock_ansible_instance

        ServerProfileModule().run()

        mock_ansible_instance.fail_json.assert_called_once_with(
            msg="Informed Server Profile Template 'TemplateA200' not found")

    @mock.patch('oneview_server_profile.resource_compare')
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_fail_when_informed_hardware_not_exist(self, mock_module, mock_ov_from_file, mock_resource_compare):
        profile_data = deepcopy(CREATED_BASIC_PROFILE)

        present = deepcopy(PARAMS_FOR_PRESENT)
        present['data']['server_hardware'] = "ServerHardwareName"
        present['data']['server_template'] = "TemplateA200"

        mock_resource_compare.return_value = False

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = profile_data
        mock_ov_instance.server_hardware.get_by.return_value = None
        mock_ov_instance.server_profile_templates.get_by_name.return_value = BASIC_TEMPLATE

        mock_ov_from_file.return_value = mock_ov_instance

        mock_ansible_instance = create_ansible_mock(present)
        mock_module.return_value = mock_ansible_instance

        ServerProfileModule().run()

        mock_ansible_instance.fail_json.assert_called_once_with(
            msg="Informed Server Hardware 'ServerHardwareName' not found")


class ServerProfileDeepMergeSpec(unittest.TestCase):

    boot_conn = dict(priority="NotBootable", chapLevel="none")

    connection_1 = dict(id=1, name="connection-1", mac="E2:4B:0D:30:00:29", boot=boot_conn)
    connection_2 = dict(id=2, name="connection-2", mac="E2:4B:0D:30:00:2A", boot=boot_conn)

    connection_1_no_mac_basic_boot = dict(id=1, name="connection-1", boot=dict(priority="NotBootable"))
    connection_2_no_mac_basic_boot = dict(id=2, name="connection-2", boot=dict(priority="NotBootable"))

    path_1 = dict(isEnabled=True, connectionId=1, storageTargets=["20:00:00:02:AC:00:08:D6"])
    path_2 = dict(isEnabled=True, connectionId=2, storageTargetType="Auto")

    volume_1 = dict(id=1, volumeUri='/rest/volume/id1', lunType='Auto', storagePaths=[path_1, path_2])
    volume_2 = dict(id=2, volumeUri='/rest/volume/id2', lunType='Auto', storagePaths=[])

    san_storage = dict(hostOSType="Windows 2012 / WS2012 R2",
                       volumeAttachments=[volume_1, volume_2])

    profile_with_san_storage = CREATED_BASIC_PROFILE.copy()
    profile_with_san_storage['connections'] = [connection_1, connection_2]
    profile_with_san_storage['sanStorage'] = san_storage

    def setUp(self):
        self.patcher_ov_client_from_json_file = patch.object(OneViewClient, 'from_json_file')
        mock_from_json_file = self.patcher_ov_client_from_json_file.start()

        self.mock_ov_client = mock.Mock()
        mock_from_json_file.return_value = self.mock_ov_client

        self.patcher_ansible_module = patch('oneview_server_profile.AnsibleModule')
        mock_ansible_module = self.patcher_ansible_module.start()

        self.mock_ansible_instance = mock.Mock()
        mock_ansible_module.return_value = self.mock_ansible_instance

        self.mock_ov_client.server_hardware.get_by.return_value = [FAKE_SERVER_HARDWARE]
        self.mock_ov_client.server_hardware.update_power_state.return_value = {}
        self.mock_ov_client.server_profiles.update.return_value = deepcopy(self.profile_with_san_storage)

    def tearDown(self):
        self.patcher_ov_client_from_json_file.stop()
        self.patcher_ansible_module.stop()

    def test_merge_when_data_is_equals(self):
        self.mock_ov_client.server_profiles.get_by_name.return_value = deepcopy(self.profile_with_san_storage)
        self.mock_ansible_instance.params = deepcopy(PARAMS_FOR_PRESENT)
        data = dict(name="Profile101",
                    connections=[self.connection_1.copy(), self.connection_2.copy()])
        self.mock_ansible_instance.params['data'] = data

        ServerProfileModule().run()

        self.mock_ov_client.server_profiles.update.assert_not_called()

    def test_merge_connections_when_item_added(self):
        self.mock_ov_client.server_profiles.get_by_name.return_value = deepcopy(self.profile_with_san_storage)
        connection_added = dict(id=3, name="new-connection")

        self.mock_ansible_instance.params = deepcopy(PARAMS_FOR_PRESENT)
        data = dict(name="Profile101",
                    connections=[self.connection_1_no_mac_basic_boot.copy(),
                                 self.connection_2_no_mac_basic_boot.copy(),
                                 connection_added.copy()])
        self.mock_ansible_instance.params['data'] = data

        ServerProfileModule().run()
        actual_connections = self.mock_ov_client.server_profiles.update.call_args[0][0]['connections']
        expected_connections = [self.connection_1.copy(), self.connection_2.copy(), connection_added]

        self.assertEqual(expected_connections, actual_connections)

    def test_merge_connections_when_item_removed(self):
        self.mock_ov_client.server_profiles.get_by_name.return_value = deepcopy(self.profile_with_san_storage)
        self.mock_ansible_instance.params = deepcopy(PARAMS_FOR_PRESENT)
        data = dict(name="Profile101",
                    connections=[self.connection_1.copy()])
        self.mock_ansible_instance.params['data'] = data

        ServerProfileModule().run()
        actual_connections = self.mock_ov_client.server_profiles.update.call_args[0][0]['connections']
        expected_connections = [self.connection_1]

        self.assertEqual(expected_connections, actual_connections)

    def test_merge_connections_when_item_renamed(self):
        self.mock_ov_client.server_profiles.get_by_name.return_value = deepcopy(self.profile_with_san_storage)
        connection_2_renamed = dict(id=2, name="connection-2-renamed", boot=dict(priority="NotBootable"))

        self.mock_ansible_instance.params = deepcopy(PARAMS_FOR_PRESENT)
        data = dict(name="Profile101",
                    connections=[self.connection_1.copy(), connection_2_renamed.copy()])
        self.mock_ansible_instance.params['data'] = data

        ServerProfileModule().run()
        actual_connections = self.mock_ov_client.server_profiles.update.call_args[0][0]['connections']
        connection_2_merged = dict(id=2, name="connection-2-renamed", mac="E2:4B:0D:30:00:2A", boot=self.boot_conn)
        expected_connections = [self.connection_1.copy(), connection_2_merged.copy()]

        self.assertEqual(expected_connections, actual_connections)

    def test_merge_connections_when_connection_list_removed(self):
        self.mock_ov_client.server_profiles.get_by_name.return_value = deepcopy(self.profile_with_san_storage)
        self.mock_ansible_instance.params = deepcopy(PARAMS_FOR_PRESENT)
        data = dict(name="Profile101",
                    connections=[])
        self.mock_ansible_instance.params['data'] = data

        ServerProfileModule().run()
        actual_merged_data = self.mock_ov_client.server_profiles.update.call_args[0][0]

        self.assertFalse(actual_merged_data['connections'])

    def test_merge_san_storage_when_values_changed(self):
        self.mock_ov_client.server_profiles.get_by_name.return_value = deepcopy(self.profile_with_san_storage)
        self.mock_ansible_instance.params = deepcopy(PARAMS_FOR_PRESENT)
        data = dict(name="Profile101",
                    sanStorage=deepcopy(self.san_storage))
        data['sanStorage'].pop('hostOSType')
        data['sanStorage']['newField'] = "123"
        self.mock_ansible_instance.params['data'] = data

        ServerProfileModule().run()
        actual_san_storage = self.mock_ov_client.server_profiles.update.call_args[0][0]['sanStorage']
        expected_san_storage = deepcopy(self.san_storage)
        expected_san_storage['newField'] = "123"

        self.assertEqual(expected_san_storage, actual_san_storage)

    def test_merge_san_storage_when_san_removed_from_profile_with_san(self):
        self.mock_ov_client.server_profiles.get_by_name.return_value = deepcopy(self.profile_with_san_storage)
        self.mock_ansible_instance.params = deepcopy(PARAMS_FOR_PRESENT)
        data = dict(name="Profile101",
                    sanStorage=None)
        self.mock_ansible_instance.params['data'] = data

        ServerProfileModule().run()
        actual_merged_data = self.mock_ov_client.server_profiles.update.call_args[0][0]

        expected_san_storage = dict(manageSanStorage=False,
                                    volumeAttachments=[])
        self.assertEqual(expected_san_storage, actual_merged_data['sanStorage'])

    def test_merge_san_storage_when_san_removed_from_basic_profile(self):
        self.mock_ov_client.server_profiles.get_by_name.return_value = deepcopy(CREATED_BASIC_PROFILE)
        self.mock_ansible_instance.params = deepcopy(PARAMS_FOR_PRESENT)
        data = dict(name="Profile101",
                    sanStorage=None,
                    newField="123")
        self.mock_ansible_instance.params['data'] = data

        ServerProfileModule().run()
        actual_merged_data = self.mock_ov_client.server_profiles.update.call_args[0][0]

        self.assertFalse(actual_merged_data['sanStorage'])

    def test_merge_volume_attachments_removed(self):
        self.mock_ov_client.server_profiles.get_by_name.return_value = deepcopy(self.profile_with_san_storage)
        self.mock_ansible_instance.params = deepcopy(PARAMS_FOR_PRESENT)
        data = dict(name="Profile101",
                    sanStorage=deepcopy(self.san_storage))
        data['sanStorage']['volumeAttachments'] = None
        self.mock_ansible_instance.params['data'] = data

        ServerProfileModule().run()
        actual_volumes = self.mock_ov_client.server_profiles.update.call_args[0][0]['sanStorage']['volumeAttachments']

        self.assertFalse(actual_volumes)

    def test_merge_volume_attachments_when_item_changed(self):
        self.mock_ov_client.server_profiles.get_by_name.return_value = deepcopy(self.profile_with_san_storage)
        self.mock_ansible_instance.params = deepcopy(PARAMS_FOR_PRESENT)
        data = dict(name="Profile101",
                    sanStorage=deepcopy(self.san_storage))
        data['sanStorage']['volumeAttachments'][0]['newField'] = "123"
        self.mock_ansible_instance.params['data'] = data

        expected_volumes = [deepcopy(self.volume_1), deepcopy(self.volume_2)]
        expected_volumes[0]['newField'] = "123"

        ServerProfileModule().run()
        actual_volumes = self.mock_ov_client.server_profiles.update.call_args[0][0]['sanStorage']['volumeAttachments']

        self.assertEqual(expected_volumes, actual_volumes)

    def test_merge_storage_paths_when_item_changed(self):
        self.mock_ov_client.server_profiles.get_by_name.return_value = deepcopy(self.profile_with_san_storage)
        self.mock_ansible_instance.params = deepcopy(PARAMS_FOR_PRESENT)
        data = dict(name="Profile101",
                    sanStorage=deepcopy(self.san_storage))
        data['sanStorage']['volumeAttachments'][0]['storagePaths'][1]['newField'] = "123"
        self.mock_ansible_instance.params['data'] = data

        expected_paths_storage_1 = [deepcopy(self.path_1), deepcopy(self.path_2)]
        expected_paths_storage_1[1]['newField'] = "123"

        ServerProfileModule().run()
        actual_volumes = self.mock_ov_client.server_profiles.update.call_args[0][0]['sanStorage']['volumeAttachments']

        self.assertEqual(expected_paths_storage_1, actual_volumes[0]['storagePaths'])
        self.assertEqual([], actual_volumes[1]['storagePaths'])

    def test_merge_storage_paths_when_order_differs(self):
        """
        When a resource is retrieved by OneView, the order of the storage paths sometimes differs from the order of the
        storage paths saved.
        """
        profile = deepcopy(self.profile_with_san_storage)
        profile['sanStorage']['volumeAttachments'][0]['storagePaths'][0] = deepcopy(self.path_2)  # connectionId = 2
        profile['sanStorage']['volumeAttachments'][0]['storagePaths'][1] = deepcopy(self.path_1)  # connectionId = 1

        self.mock_ov_client.server_profiles.get_by_name.return_value = deepcopy(self.profile_with_san_storage)
        self.mock_ansible_instance.params = deepcopy(PARAMS_FOR_PRESENT)
        data = dict(name="Profile101",
                    sanStorage=deepcopy(self.san_storage))
        data['sanStorage']['volumeAttachments'][0]['storagePaths'][0]['newField'] = "123"  # connectionId = 1

        self.mock_ansible_instance.params['data'] = data

        path_1_changed = deepcopy(self.path_1)
        path_1_changed['newField'] = "123"

        expected_paths = [deepcopy(path_1_changed),  # connectionId = 1, with field added
                          deepcopy(self.path_2)]     # connectionId = 2

        ServerProfileModule().run()
        actual_volumes = self.mock_ov_client.server_profiles.update.call_args[0][0]['sanStorage']['volumeAttachments']

        self.assertEqual(expected_paths, actual_volumes[0]['storagePaths'])
        self.assertEqual([], actual_volumes[1]['storagePaths'])

    def test_merge_storage_paths_removed(self):
        self.mock_ov_client.server_profiles.get_by_name.return_value = deepcopy(self.profile_with_san_storage)
        self.mock_ansible_instance.params = deepcopy(PARAMS_FOR_PRESENT)
        data = dict(name="Profile101",
                    sanStorage=deepcopy(self.san_storage))
        data['sanStorage']['volumeAttachments'][0]['storagePaths'] = []
        self.mock_ansible_instance.params['data'] = data

        ServerProfileModule().run()
        actual_volumes = self.mock_ov_client.server_profiles.update.call_args[0][0]['sanStorage']['volumeAttachments']

        self.assertEqual([], actual_volumes[1]['storagePaths'])
        self.assertEqual([], actual_volumes[1]['storagePaths'])

    def test_merge_bios(self):
        self.mock_ov_client.server_profiles.get_by_name.return_value = deepcopy(self.profile_with_san_storage)
        self.mock_ansible_instance.params = deepcopy(PARAMS_FOR_PRESENT)
        data = dict(name="Profile101",
                    sanStorage=deepcopy(self.san_storage))
        data['bios'] = dict(newField="123")
        self.mock_ansible_instance.params['data'] = data

        ServerProfileModule().run()
        actual_bios = self.mock_ov_client.server_profiles.update.call_args[0][0]['bios']

        expected_bios = dict(manageBios=False, overriddenSettings=[], newField="123")
        self.assertEqual(expected_bios, actual_bios)

    def test_merge_boot(self):
        self.mock_ov_client.server_profiles.get_by_name.return_value = deepcopy(self.profile_with_san_storage)
        self.mock_ansible_instance.params = deepcopy(PARAMS_FOR_PRESENT)
        data = dict(name="Profile101",
                    sanStorage=deepcopy(self.san_storage))
        data['boot'] = dict(newField="123")
        self.mock_ansible_instance.params['data'] = data

        ServerProfileModule().run()
        actual_boot = self.mock_ov_client.server_profiles.update.call_args[0][0]['boot']

        expected_boot = dict(manageBoot=False, order=[], newField="123")
        self.assertEqual(expected_boot, actual_boot)

    def test_merge_boot_mode(self):
        self.mock_ov_client.server_profiles.get_by_name.return_value = deepcopy(self.profile_with_san_storage)
        self.mock_ansible_instance.params = deepcopy(PARAMS_FOR_PRESENT)
        data = dict(name="Profile101",
                    sanStorage=deepcopy(self.san_storage))
        data['bootMode'] = dict(newField="123")
        self.mock_ansible_instance.params['data'] = data

        ServerProfileModule().run()
        actual_boot_mode = self.mock_ov_client.server_profiles.update.call_args[0][0]['bootMode']

        expected_boot_mode = dict(manageMode=False, mode=None, pxeBootPolicy=None, newField="123")
        self.assertEqual(expected_boot_mode, actual_boot_mode)


class ServerProfileAbsentStateSpec(unittest.TestCase):
    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_fail_when_delete_raises_exception(
            self, mock_ansible_module, mock_ov_from_file):
        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.side_effect = Exception(FAKE_MSG_ERROR)

        mock_ov_from_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(PARAMS_FOR_ABSENT)
        mock_ansible_module.return_value = mock_ansible_instance

        self.assertRaises(Exception, ServerProfileModule().run())

        mock_ansible_instance.fail_json.assert_called_once_with(msg=FAKE_MSG_ERROR)

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_turn_off_hardware_before_delete(
            self, mock_ansible_module, mock_ov_from_file):
        sh_uri = '/rest/server-hardware/37333036-3831-76jh-4831-303658389766'
        profile_data = deepcopy(BASIC_PROFILE)
        profile_data['serverHardwareUri'] = sh_uri

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = profile_data
        mock_ov_instance.server_hardware.update_power_state.return_value = {}

        mock_ov_from_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(PARAMS_FOR_ABSENT)
        mock_ansible_module.return_value = mock_ansible_instance

        self.assertRaises(Exception, ServerProfileModule().run())

        mock_ov_instance.server_hardware.update_power_state.assert_called_once_with(
            {'powerControl': 'PressAndHold', 'powerState': 'Off'}, sh_uri)

        mock_ov_instance.server_profiles.delete.assert_called_once_with(profile_data)

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=True,
            msg=SERVER_PROFILE_DELETED
        )

    @mock.patch.object(OneViewClient, 'from_json_file')
    @mock.patch('oneview_server_profile.AnsibleModule')
    def test_should_not_turn_off_hardware_if_not_associated_before_delete(
            self, mock_ansible_module, mock_ov_from_file):
        profile_data = deepcopy(BASIC_PROFILE)

        mock_ov_instance = mock.Mock()
        mock_ov_instance.server_profiles.get_by_name.return_value = profile_data

        mock_ov_from_file.return_value = mock_ov_instance
        mock_ansible_instance = create_ansible_mock(PARAMS_FOR_ABSENT)
        mock_ansible_module.return_value = mock_ansible_instance

        self.assertRaises(Exception, ServerProfileModule().run())

        times_power_off_was_called = mock_ov_instance.server_hardware.update_power_state.call_count
        self.assertEqual(0, times_power_off_was_called)

        mock_ov_instance.server_profiles.delete.assert_called_once_with(profile_data)

        mock_ansible_instance.exit_json.assert_called_once_with(
            changed=True,
            msg=SERVER_PROFILE_DELETED
        )


if __name__ == '__main__':
    unittest.main()
