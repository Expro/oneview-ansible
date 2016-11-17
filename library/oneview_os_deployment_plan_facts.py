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
---
module: oneview_os_deployment_plan_facts
short_description: Retrieve facts about one or more Os Deployment Plans.
description:
    - Retrieve facts about one or more of the Os Deployment Plans from OneView.
requirements:
    - "python >= 2.7.9"
    - "hpOneView >= 3.0.0"
author: "Abilio Parada (@abiliogp)"
options:
    config:
      description:
        - Path to a .json configuration file containing the OneView client configuration.
          The configuration file is optional. If the file path is not provided, the configuration will be loaded from
          environment variables.
      required: false
    name:
      description:
        - Os Deployment Plan name.
      required: false
notes:
    - "A sample configuration file for the config parameter can be found at:
       https://github.com/HewlettPackard/oneview-ansible/blob/master/examples/oneview_config-rename.json"
    - "Check how to use environment variables for configuration at:
       https://github.com/HewlettPackard/oneview-ansible#environment-variables"
'''

EXAMPLES = '''
- name: Gather facts about all Os Deployment Plans
  oneview_os_deployment_plan_facts:
    config: "{{ config }}"
  delegate_to: localhost

- debug: var=os_deployment_plans

- name: Gather facts about an Os Deployment Plan by name
  oneview_os_deployment_plan_facts:
    config: "{{ config }}"
    name: "Deployment Plan"
  delegate_to: localhost

- debug: var=os_deployment_plans
'''

RETURN = '''
os_deployment_plans:
    description: Has all the OneView facts about the Os Deployment Plans.
    returned: Always, but can be null.
    type: complex
'''
HPE_ONEVIEW_SDK_REQUIRED = 'HPE OneView Python SDK is required for this module.'


class OsDeploymentPlanFactsModule(object):
    argument_spec = {
        "config": {
            "required": False,
            "type": 'str'},
        "name": {
            "required": False,
            "type": 'str'
        }}

    def __init__(self):
        self.module = AnsibleModule(argument_spec=self.argument_spec, supports_check_mode=False)
        if not HAS_HPE_ONEVIEW:
            self.module.fail_json(msg=HPE_ONEVIEW_SDK_REQUIRED)

        if not self.module.params['config']:
            self.oneview_client = OneViewClient.from_environment_variables()
        else:
            self.oneview_client = OneViewClient.from_json_file(self.module.params['config'])

    def run(self):
        try:
            if self.module.params.get('name'):
                os_deployment_plans = self.oneview_client.os_deployment_plans.get_by('name', self.module.params['name'])
            else:
                os_deployment_plans = self.oneview_client.os_deployment_plans.get_all()

            self.module.exit_json(changed=False,
                                  ansible_facts=dict(os_deployment_plans=os_deployment_plans))

        except Exception as exception:
            self.module.fail_json(msg='; '.join(str(e) for e in exception.args))


def main():
    OsDeploymentPlanFactsModule().run()


if __name__ == '__main__':
    main()
