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


FC_NETWORK_CREATED = 'FC Network created sucessfully.'
FC_NETWORK_UPDATED = 'FC Network updated sucessfully.'
FC_NETWORK_DELETED = 'FC Network deleted sucessfully.'
FC_NETWORK_ALREADY_EXIST = 'FC Network already exists.'
FC_NETWORK_ALREADY_ABSENT = 'Nothing to do.'


class FcNetworkModule(object):

    argument_spec = dict(
        config=dict(required=True, type='str'),
        state=dict(
            required=True,
            choices=['present', 'absent']
        ),
        data=dict(required=True, type='dict')
    )

    def __init__(self):
        self.module = AnsibleModule(argument_spec=self.argument_spec, supports_check_mode=False)
        self.oneview_client = OneViewClient.from_json(self.module.params['config'])

    def run(self):
        state = self.module.params['state']
        data = self.module.params['data']

        try:
            if state == 'present':
                self.__present(data)
            elif state == 'absent':
                self.__absent(data)

        except Exception as exception:
            self.module.fail_json(msg=exception.message)

    def __present(self, data):
        resource = self.__get_by_name(data)

        if not resource:
            self.__create(data)
        else:
            self.__update(data, resource)

    def __absent(self, data):
        resource = self.__get_by_name(data)

        if resource:
            task = self.oneview_client.fc_networks.delete(resource)
            self.module.exit_json(changed=True,
                                  msg=FC_NETWORK_DELETED,
                                  ansible_facts=task)
        else:
            self.module.exit_json(changed=False, msg=FC_NETWORK_ALREADY_ABSENT)

    def __create(self, data):
        new_fc_network = self.oneview_client.fc_networks.create(data)

        self.module.exit_json(changed=True,
                              msg=FC_NETWORK_CREATED,
                              ansible_facts=dict(fc_network=new_fc_network))

    def __update(self, data, resource):
        merged_data = resource.copy()
        merged_data.update(data)

        if cmp(resource, merged_data) == 0:

            self.module.exit_json(changed=False,
                                  msg=FC_NETWORK_ALREADY_EXIST,
                                  ansible_facts=dict(fc_network=resource))

        else:
            updated_fc_network = self.oneview_client.fc_networks.update(merged_data)

            self.module.exit_json(changed=True,
                                  msg=FC_NETWORK_UPDATED,
                                  ansible_facts=dict(fc_network=updated_fc_network))

    def __get_by_name(self, data):
        result = self.oneview_client.fc_networks.get_by('name', data['name'])
        return result[0] if result else None


def main():
    FcNetworkModule().run()


if __name__ == '__main__':
    main()
