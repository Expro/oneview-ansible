#!/usr/bin/python

###
# (C) Copyright (2016) Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
###

from ansible.module_utils.basic import *
from hpOneView.oneview_client import OneViewClient


DOCUMENTATION = '''
---
module: fc_network_facts
short_description: Retrieve facts about one or more One View Fibre Channel
    Networks.
description:
    - Retrieve facts about one or more Fibre Channel Networks from One View.
requirements:
    - "python >= 2.7.11"
    - "hpOneView"
author: "Mariana Kreisig (@marikrg)"
options:
    config:
      description:
        - Path to a .json configuration file. The file must contains a OneView client configuration like:
            {
              "ip": "your_oneview_ip",
              "credentials": {
                "config": "/path/config.json",
                "password": "your_oneview_password"
              }
            }
      required: true
    name:
      description:
        - Fibre Channel Network name
      required: false

'''

EXAMPLES = '''
# Gather facts about all Fibre Channel networks
- oneview_fc_network_facts:
    oneview_host: hostname
    username: username
    password: password
  register: result
- debug: var=result

# Gather facts about a Fibre Channel by name
- oneview_fc_network_facts:
    oneview_host: hostname
    username: username
    password: password
    name: network name
  register: result
- debug: var=result
'''

RETURN = '''
fc_networks:
    description: Has all the One View facts about the Fibre Channel Networks.
    returned: always, but can be null
    type: complex
'''


class FcNetworkFactsModule(object):

    argument_spec = dict(
        config=dict(required=True, type='str'),
        name=dict(required=False, type='str')
    )

    def __init__(self):
        self.module = AnsibleModule(argument_spec=self.argument_spec,
                                    supports_check_mode=False)
        self.oneview_client = OneViewClient.from_json(self.module.params['config'])

    def __get_config(self):
        return dict(
            ip=self.module.params['oneview_host'],
            credentials=dict(
                userName=self.module.params['username'],
                password=self.module.params['password']
            )
        )

    def run(self):
        try:
            if self.module.params['name']:
                self.__get_by_name(self.module.params['name'])
            else:
                self.__get_all()

        except Exception as exception:
            self.module.fail_json(msg=exception.message)

    def __get_by_name(self, name):
        fc_network = self.oneview_client.fc_networks.get_by('name', name)

        self.module.exit_json(changed=False,
                              ansible_facts=dict(fc_networks=fc_network))

    def __get_all(self):
        fc_networks = self.oneview_client.fc_networks.get_all()

        self.module.exit_json(changed=False,
                              ansible_facts=dict(fc_networks=fc_networks))


def main():
    FcNetworkFactsModule().run()


if __name__ == '__main__':
    main()
