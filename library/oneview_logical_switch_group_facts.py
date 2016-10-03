#!/usr/bin/python
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
module: oneview_logical_switch_group_facts
short_description: Retrieve facts about OneView Logical Switch Groups.
description:
    - Retrieve facts about the Logical Switch Groups of the OneView.
requirements:
    - "python >= 2.7.9"
    - "hpOneView >= 2.0.1"
author: "Gustavo Hennig (@GustavoHennig)"
options:
    config:
      description:
        - Path to a .json configuration file containing the OneView client configuration.
      required: true
    name:
      description:
        - Logical Switch Group name.
      required: false
notes:
    - "A sample configuration file for the config parameter can be found at:
       https://github.com/HewlettPackard/oneview-ansible/blob/master/examples/oneview_config-rename.json"
'''

EXAMPLES = '''
- name: Gather facts about all Logical Switch Groups
  oneview_logical_switch_group_facts:
    config: "{{ config }}"
  delegate_to: localhost

- debug: var=logical_switch_groups

- name: Gather facts about a Logical Switch Group by name
  oneview_logical_switch_group_facts:
    config: "{{ config }}"
    name: "LogicalSwitchGroupDemo"
  delegate_to: localhost

- debug: var=logical_switch_groups
'''

RETURN = '''
logical_switch_groups:
    description: Has all the OneView facts about the Logical Switch Groups.
    returned: Always, but can be null.
    type: complex
'''


class LogicalSwitchGroupFactsModule(object):
    argument_spec = {
        "config": {
            "required": True,
            "type": 'str'
        },
        "name": {
            "required": False,
            "type": 'str'
        }}

    def __init__(self):
        self.module = AnsibleModule(argument_spec=self.argument_spec, supports_check_mode=False)
        self.oneview_client = OneViewClient.from_json_file(self.module.params['config'])

    def run(self):
        try:
            client = self.oneview_client.logical_switch_groups

            if self.module.params.get('name'):
                logical_switch_groups = client.get_by('name', self.module.params['name'])
            else:
                logical_switch_groups = client.get_all()

            self.module.exit_json(changed=False,
                                  ansible_facts=dict(logical_switch_groups=logical_switch_groups))

        except Exception as exception:
            self.module.fail_json(msg=exception.message)


def main():
    LogicalSwitchGroupFactsModule().run()


if __name__ == '__main__':
    main()
