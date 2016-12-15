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

try:
    from hpOneView.oneview_client import OneViewClient
    from hpOneView.common import transform_list_to_dict

    HAS_HPE_ONEVIEW = True
except ImportError:
    HAS_HPE_ONEVIEW = False

DOCUMENTATION = '''
---
module: image_streamer_golden_image_facts
short_description: Retrieve facts about one or more of the Image Streamer Golden Image.
description:
    - Retrieve facts about one or more of the Image Streamer Golden Image.
requirements:
    - "python >= 2.7.9"
    - "hpOneView >= 3.0.1"
author:
    - "Gustavo Hennig (@GustavoHennig)"
options:
    config:
      description:
        - Path to a .json configuration file containing the OneView client configuration.
          The configuration file is optional. If the file path is not provided, the configuration will be loaded from
          environment variables.
      required: false
    name:
      description:
        - Golden Image name.
      required: false
    options:
      description:
        - "List with options to gather additional facts about Golden Image.
          Options allowed:
          'archive' get the details of the Golden Image captured logs.
        - These options are valid just when a 'name' is provided. Otherwise it will be ignored."
      required: false
notes:
    - "A sample configuration file for the config parameter can be found at:
       https://github.com/HewlettPackard/oneview-ansible/blob/master/examples/oneview_config-rename.json"
    - "Check how to use environment variables for configuration at:
       https://github.com/HewlettPackard/oneview-ansible#environment-variables"
    - This resource is only available on HPE Synergy
'''

EXAMPLES = '''
- name: Gather facts about all Golden Images
  image_streamer_golden_image_facts:
    config: "{{ config }}"
  delegate_to: localhost
- debug: var=golden_images

- name: Gather facts about a Golden Image by name
  image_streamer_golden_image_facts:
    config: "{{ config }}"
    name: "{{ name }}"
  delegate_to: localhost
- debug: var=golden_images

- name: Gather facts about the details of the golden image capture logs
  image_streamer_golden_image_facts:
    config: "{{ config }}"
    name: "{{ name }}"
    options:
      - archive
  delegate_to: localhost
- debug: var=golden_image_archive
'''

RETURN = '''
golden_images:
    description: The list of Golden Images.
    returned: Always, but can be null.
    type: list

golden_image_archive:
    description: The installed firmware for a Golden Image.
    returned: When requested, but can be null.
    type: complex
'''

HPE_ONEVIEW_SDK_REQUIRED = 'HPE OneView Python SDK is required for this module.'


class GoldenImageFactsModule(object):
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

        self.i3s_client = oneview_client.create_image_streamer_client()

    def run(self):
        try:
            name = self.module.params.get("name")

            ansible_facts = {}

            if name:
                golden_images = self.i3s_client.golden_images.get_by("name", name)

                if golden_images:
                    options = self.module.params.get("options")

                    if options:
                        options_facts = self.__gather_option_facts(options, golden_images[0])
                        ansible_facts.update(options_facts)
            else:
                golden_images = self.i3s_client.golden_images.get_all()

            ansible_facts['golden_images'] = golden_images

            self.module.exit_json(changed=False, ansible_facts=ansible_facts)

        except Exception as exception:
            self.module.fail_json(msg='; '.join(str(e) for e in exception.args))

    def __gather_option_facts(self, options, resource):
        ansible_facts = {}

        options = transform_list_to_dict(options)

        if options.get('archive'):
            ansible_facts['golden_image_archive'] = self.i3s_client.golden_images.get_archive(resource['uri'])

        return ansible_facts


def main():
    GoldenImageFactsModule().run()


if __name__ == '__main__':
    main()
