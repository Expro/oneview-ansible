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
module: oneview_switch_facts
short_description: Retrieve facts about the OneView Switches.
description:
    - Retrieve facts about the OneView Switches.
requirements:
    - "python >= 2.7.9"
    - "hpOneView"
author: "Bruno Souza (@bsouza)"
options:
    config:
      description:
        - Path to a .json configuration file containing the OneView client configuration.
      required: true
    name:
      description:
        - Switch name.
      required: false
    options:
      description:
        - "List with options to gather additional facts about Logical Interconnect.
          Options allowed:
          'environmentalConfiguration' gets the environmental configuration for a switch."
      required: false
notes:
    - "A sample configuration file for the config parameter can be found at:
       https://github.com/HewlettPackard/oneview-ansible/blob/master/examples/oneview_config-rename.json"
'''

EXAMPLES = '''
- name: Gather facts about all switches
  oneview_switch_facts:
    config: "{{ config }}"

- name: Gather facts about the switch that matches the specified switch name
  oneview_switch_facts:
    config: "{{ config }}"
    name: "172.18.20.1"

- name: Gather facts about the environmental configuration for the switch that matches the specified switch name
  oneview_switch_facts:
    config: "{{ config }}"
    name: "172.18.20.1"
  options:
    - environmentalConfiguration
'''

RETURN = '''
switches:
    description: The list of switches.
    returned: Always, but can be null.
    type: list

switch_environmental_configuration:
    description: The environmental configuration for a switch.
    returned: When requested, but can be null.
    type: complex
'''


class SwitchFactsModule(object):
    argument_spec = dict(
        config=dict(required=True, type='str'),
        name=dict(required=False, type='str'),
        options=dict(required=False, type='list')
    )

    def __init__(self):
        self.module = AnsibleModule(argument_spec=self.argument_spec, supports_check_mode=False)
        oneview_client = OneViewClient.from_json_file(self.module.params['config'])
        self.resource_client = oneview_client.switches

    def run(self):
        try:
            facts = dict()
            name = self.module.params["name"]

            if name:
                facts['switches'] = self.resource_client.get_by('name', name)
                options = self.module.params.get('options') or []

                if facts['switches'] and 'environmentalConfiguration' in options:
                    uri = facts['switches'][0]['uri']
                    environmental_configuration = self.resource_client.get_environmental_configuration(id_or_uri=uri)
                    facts['switch_environmental_configuration'] = environmental_configuration
            else:
                facts['switches'] = self.resource_client.get_all()

            self.module.exit_json(changed=False, ansible_facts=facts)
        except Exception as e:
            self.module.fail_json(msg=e.message)


def main():
    SwitchFactsModule().run()


if __name__ == '__main__':
    main()
