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
module: oneview_interconnect_statistics_facts
short_description: Retrieve statistics facts about one interconnect from OneView.
description:
    - Retrieve statistics facts about one interconnect from OneView.
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
        - Interconnect name
      required: True
notes:
    - "A sample configuration file for the config parameter can be found at:
      https://github.hpe.com/Rainforest/oneview-ansible/blob/master/examples/oneview_config.json"
'''

EXAMPLES = '''
- name: Gather facts about statistics for the Interconnect named '0000A66102, interconnect 2'
  oneview_interconnect_statistics_facts:
    config: "{{ config }}"
    name: '0000A66102, interconnect 2'
    delegate_to: localhost

- debug: interconnect_statistics
'''

RETURN = '''
interconnect_statistics:
    description: Has all the OneView facts about the Interconnect Statistics.
    returned: always, but can be null
    type: complex
'''


class InterconnectStatisticsFactsModule(object):
    argument_spec = dict(
        config=dict(required=True, type='str'),
        name=dict(required=True, type='str')
    )

    def __init__(self):
        self.module = AnsibleModule(argument_spec=self.argument_spec, supports_check_mode=False)
        self.oneview_client = OneViewClient.from_json_file(self.module.params['config'])

    def run(self):
        try:
            interconnect = self.__get_interconnect()
            interconnect_statistics = self.oneview_client.interconnects.get_statistics(interconnect["uri"])

            self.module.exit_json(
                changed=False,
                ansible_facts=dict(interconnect_statistics=interconnect_statistics)
            )
        except Exception as exception:
            self.module.fail_json(msg=exception.message)

    def __get_interconnect(self):
        name = self.module.params["name"]
        interconnect = self.oneview_client.interconnects.get_by_name(name)

        if not interconnect:
            raise Exception("There is no interconnect named {}".format(name))

        return interconnect


def main():
    InterconnectStatisticsFactsModule().run()


if __name__ == '__main__':
    main()
