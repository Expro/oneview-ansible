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
try:
    from hpOneView.oneview_client import OneViewClient

    HAS_HPE_ONEVIEW = True
except ImportError:
    HAS_HPE_ONEVIEW = False

DOCUMENTATION = '''
module: oneview_managed_san_facts
short_description: Retrieve facts about the OneView Managed SANs.
description:
    - Retrieve facts about the OneView Managed SANs.
requirements:
    - "python >= 2.7.9"
    - "hpOneView >= 2.0.1"
author: "Mariana Kreisig (@marikrg)"
options:
    config:
      description:
        - Path to a .json configuration file containing the OneView client configuration.
          The configuration file is optional. If the file path is not provided, the configuration will be loaded from
          environment variables.
      required: false
    name:
      description:
        - Name of the Managed SAN.
      required: false
    options:
      description:
        - "List with options to gather additional facts about Managed SAN.
          Options allowed:
          'endpoints' gets the list of endpoints in the SAN identified by name."
      required: false
notes:
    - "A sample configuration file for the config parameter can be found at:
       https://github.com/HewlettPackard/oneview-ansible/blob/master/examples/oneview_config-rename.json"
    - "Check how to use environment variables for configuration at:
       https://github.com/HewlettPackard/oneview-ansible#environment-variables"
'''

EXAMPLES = '''
- name: Gather facts about all Managed SANs
  oneview_managed_san_facts:
    config: "{{ config }}"
  delegate_to: localhost

- debug: var=managed_sans

- name: Gather facts about a Managed SAN by name
  oneview_managed_san_facts:
    config: "{{ config_path }}"
    name: "SAN1_0"
  delegate_to: localhost

- debug: var=managed_sans

- name: Gather facts about the endpoints in the SAN identified by name
  oneview_managed_san_facts:
    config: "{{ config_path }}"
    name: "SAN1_0"
    options:
      - endpoints
  delegate_to: localhost

- debug: var=managed_sans
- debug: var=managed_san_endpoints
'''

RETURN = '''
managed_sans:
    description: The list of Managed SANs.
    returned: Always, but can be null.
    type: list

managed_san_endpoints:
    description: The list of endpoints in the SAN identified by name.
    returned: When requested, but can be null.
    type: complex
'''
HPE_ONEVIEW_SDK_REQUIRED = 'HPE OneView Python SDK is required for this module.'


class ManagedSanFactsModule(object):
    argument_spec = dict(
        config=dict(required=False, type='str'),
        name=dict(required=False, type='str'),
        options=dict(required=False, type='list')
    )

    def __init__(self):
        self.module = AnsibleModule(argument_spec=self.argument_spec, supports_check_mode=False)
        if not HAS_HPE_ONEVIEW:
            self.module.fail_json(msg=HPE_ONEVIEW_SDK_REQUIRED)

        if not self.module.params['config']:
            oneview_client = OneViewClient.from_environment_variables()
        else:
            oneview_client = OneViewClient.from_json_file(self.module.params['config'])

        self.resource_client = oneview_client.managed_sans

    def run(self):
        try:
            facts = dict()
            name = self.module.params["name"]

            if name:
                facts['managed_sans'] = [self.resource_client.get_by_name(name)]
                options = self.module.params.get('options') or []

                if facts['managed_sans'] and 'endpoints' in options:
                    managed_san = facts['managed_sans'][0]
                    if managed_san:
                        environmental_configuration = self.resource_client.get_endpoints(managed_san['uri'])
                        facts['managed_san_endpoints'] = environmental_configuration
            else:
                facts['managed_sans'] = self.resource_client.get_all()

            self.module.exit_json(changed=False, ansible_facts=facts)

        except Exception as exception:
            self.module.fail_json(msg='; '.join(str(e) for e in exception.args))


def main():
    ManagedSanFactsModule().run()


if __name__ == '__main__':
    main()
