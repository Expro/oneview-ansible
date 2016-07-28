#!/usr/bin/python
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
from ansible.module_utils.basic import *
from hpOneView.oneview_client import OneViewClient

DOCUMENTATION = '''
---
module: oneview_server_hardware
short_description: Manage OneView Server Hardware resources.
description:
    - Provides an interface to manage Server Hardware resources. Can add, update, remove and change power state.
requirements:
    - "python >= 2.7.9"
    - "hpOneView"
author: "Gustavo Hennig (@GustavoHennig)"
options:
    config:
        description:
            - Path to a .json configuration file containing the OneView client configuration.
        required: true
    state:
        description:
            - Indicates the desired state for the Server Hardware resource.
              'present' will ensure data properties are compliant to OneView.
              'absent' will remove the resource from OneView, if it exists.
              'set_power_state' will set the power state of the Server Hardware.
        choices: ['present', 'absent', 'set_power_state']
        required: true
    data:
        description:
            - List with Server Hardware properties and its associated states
        required: true
notes:
    - "A sample configuration file for the config parameter can be found at:
      https://github.hpe.com/Rainforest/oneview-ansible/blob/master/examples/oneview_config.json"
'''

EXAMPLES = '''
- name: Add a Server Hardware
  oneview_server_hardware:
    config: "{{ config }}"
    state: present
    data:
         hostname : "172.18.6.15"
         username : "dcs"
         password : "dcs"
         force : false
         licensingIntent: "OneView"
         configurationState: "Managed"
  delegate_to: localhost

- name: Power Off the server hardware
  oneview_server_hardware:
    config: "{{ config }}"
    state: set_power_state
    data:
        hostname : "172.18.6.15"
        powerStateData:
            powerState: "Off"
            powerControl: "MomentaryPress"
  delegate_to: localhost

- name: Remove the server hardware by its IP
  oneview_server_hardware:
    config: "{{ config }}"
    state: absent
    data:
        hostname : "172.18.6.15"
  delegate_to: localhost
'''

SERVER_HARDWARE_ADDED = 'Server Hardware added successfully.'
SERVER_HARDWARE_ALREADY_ADDED = 'Server Hardware is already present.'
SERVER_HARDWARE_DELETED = 'Server Hardware deleted successfully.'
SERVER_HARDWARE_ALREADY_ABSENT = 'Server Hardware is already absent.'
SERVER_HARDWARE_MANDATORY_FIELD_MISSING = "Mandatory field was not informed: data.hostname"
SERVER_HARDWARE_POWER_STATE_UPDATED = 'Server Hardware power state changed successfully.'
SERVER_HARDWARE_NOT_FOUND = 'Server Hardware is required for this operation.'


class ServerHardwareModule(object):
    argument_spec = dict(
        config=dict(required=True, type='str'),
        state=dict(
            required=True,
            choices=['present', 'absent', 'set_power_state']
        ),
        data=dict(required=True, type='dict')
    )

    def __init__(self):
        self.module = AnsibleModule(argument_spec=self.argument_spec, supports_check_mode=False)
        self.oneview_client = OneViewClient.from_json_file(self.module.params['config'])

    def run(self):
        try:
            state = self.module.params['state']
            data = self.module.params['data']
            changed, msg, ansible_facts = False, '', {}

            if not data.get('hostname'):
                raise Exception(SERVER_HARDWARE_MANDATORY_FIELD_MISSING)

            resource = (self.oneview_client.server_hardware.get_by("name", data['hostname']) or [None])[0]

            if state == 'present':
                changed, msg, ansible_facts = self.__present(data, resource)
            elif state == 'absent':
                changed, msg, ansible_facts = self.__absent(resource)
            elif state == 'set_power_state':
                changed, msg, ansible_facts = self.__set_power_state(data, resource)

            self.module.exit_json(changed=changed,
                                  msg=msg,
                                  ansible_facts=ansible_facts)

        except Exception as exception:
            self.module.fail_json(msg=exception.args[0])

    def __present(self, data, resource):

        changed = False
        msg = ''

        if not resource:
            resource = self.oneview_client.server_hardware.add(data)
            changed = True
            msg = SERVER_HARDWARE_ADDED
        else:
            msg = SERVER_HARDWARE_ALREADY_ADDED

        return changed, msg, dict(oneview_server_hardware=resource)

    def __absent(self, resource):
        if resource:
            self.oneview_client.server_hardware.remove(resource)
            return True, SERVER_HARDWARE_DELETED, {}
        else:
            return False, SERVER_HARDWARE_ALREADY_ABSENT, {}

    def __set_power_state(self, data, resource):
        if not resource:
            raise Exception(SERVER_HARDWARE_NOT_FOUND)

        resource = self.oneview_client.server_hardware.update_power_state(data['powerStateData'], resource['uri'])

        return True, SERVER_HARDWARE_POWER_STATE_UPDATED, dict(oneview_server_hardware=resource)


def main():
    ServerHardwareModule().run()


if __name__ == '__main__':
    main()
