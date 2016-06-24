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
module: oneview_enclosure
short_description: Manage OneView Enclosure resources.
description:
    - Provides an interface to manage Enclosure resources. Can add, update, or remove.
requirements:
    - "python >= 2.7.9"
    - "hpOneView"
author: "Mariana Kreisig (@marikrg)"
options:
    config:
      description:
        - Path to a .json configuration file containing the OneView client configuration.
      required: true
    state:
        description:
            - Indicates the desired state for the Enclosure resource.
              'present' will ensure data properties are compliant to OneView.
              'absent' will remove the resource from OneView, if it exists.
        choices: ['present', 'absent']
    data:
      description:
        - List with the Enclosure properties.
      required: true
notes:
    - A sample configuration file for the config parameter can be found at&colon;
      https://github.hpe.com/Rainforest/oneview-ansible/blob/master/examples/oneview_config.json
'''

EXAMPLES = '''
- name: Ensure that an Enclosure is present using the default configuration
  oneview_enclosure:
    config: "{{ config_file_path }}"
    state: present
    data:
      enclosureGroupUri : {{ enclosure_group_uri }},
      hostname : {{ enclosure_hostname }},
      username : {{ enclosure_username }},
      password : {{ enclosure_password }},
      name: 'Test-Enclosure'
      licensingIntent : "OneView"

- name: Updates the enclosure to have a name of "Test-Enclosure-Renamed".
  oneview_enclosure:
    config: "{{ config_file_path }}"
    state: present
    data:
      name: 'Test-Enclosure'
      newName : "Test-Enclosure-Renamed

- name: Ensure that enclosure is absent
  oneview_enclosure:
    config: "{{ config_file_path }}"
    state: absent
    data:
      name: 'Test-Enclosure'
'''


ENCLOSURE_ADDED = 'Enclosure added sucessfully.'
ENCLOSURE_REMOVED = 'Enclosure removed sucessfully.'
ENCLOSURE_UPDATED = 'Enclosure updated sucessfully.'
ENCLOSURE_ALREADY_EXIST = 'Enclosure already exists.'
ENCLOSURE_ALREADY_ABSENT = 'Nothing to do.'


class EnclosureModule(object):

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
        self.oneview_client = OneViewClient.from_json_file(self.module.params['config'])

    def run(self):
        state = self.module.params['state']
        data = self.module.params['data']

        try:
            if state == 'present':
                self.__present(data)
            elif state == 'absent':
                self.__absent(data)

        except Exception as e:
            self.module.fail_json(msg=e.message)

    def __present(self, data):
        resource = self.__get_by_name(data)

        resource_added = False
        resource_updated = False

        data_without_names = data.copy()

        name = data_without_names.pop('newName', None)
        rack_name = data_without_names.pop('rackName', None)

        if not resource:
            if not name:
                name = data_without_names.pop('name', None)
            resource = self.__add(data_without_names)
            resource_added = True

        if self.__name_has_changes(resource, name):
            resource = self.__replace_enclosure_name(resource, name)
            resource_updated = True
        if self.__rack_name_has_changes(resource, rack_name):
            resource = self.__replace_enclosure_rack_name(resource, rack_name)
            resource_updated = True

        self.__exit_status_present(resource, added=resource_added, updated=resource_updated)

    def __absent(self, data):
        resource = self.__get_by_name(data)

        if resource:
            self.oneview_client.enclosures.remove(resource)
            self.module.exit_json(changed=True,
                                  msg=ENCLOSURE_REMOVED)
        else:
            self.module.exit_json(changed=False, msg=ENCLOSURE_ALREADY_ABSENT)

    def __add(self, data):
        new_enclosure = self.oneview_client.enclosures.add(data)
        return new_enclosure

    def __name_has_changes(self, resource, name):
        return name and resource.get('name', None) != name

    def __rack_name_has_changes(self, resource, rack_name):
        return rack_name and resource.get('rackName', None) != rack_name

    def __replace_enclosure_name(self, resource, name):
        updated_resource = self.oneview_client.enclosures.patch(resource['uri'], 'replace', '/name', name)
        return updated_resource

    def __replace_enclosure_rack_name(self, resource, rack_name):
        updated_resource = self.oneview_client.enclosures.patch(resource['uri'], 'replace', '/rackName', rack_name)
        return updated_resource

    def __exit_status_present(self, resource, added, updated):
        if added:
            message = ENCLOSURE_ADDED
        elif updated:
            message = ENCLOSURE_UPDATED
        else:
            message = ENCLOSURE_ALREADY_EXIST

        self.module.exit_json(changed=added or updated,
                              msg=message,
                              ansible_facts=dict(enclosure=resource))

    def __get_by_name(self, data):
        result = self.oneview_client.enclosures.get_by('name', data['name'])
        return result[0] if result else None


def main():
    EnclosureModule().run()


if __name__ == '__main__':
    main()
