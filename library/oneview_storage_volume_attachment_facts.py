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
from hpOneView.common import transform_list_to_dict

DOCUMENTATION = '''
---
module: oneview_storage_volume_attachment_facts
short_description: Retrieve facts about Storage Volume Attachments of the OneView.
description:
    - "Retrieve facts about Storage Volume Attachments of the OneView. To gather facts about a specific Storage Volume
      Attachment is required inform the param 'storageVolumeAttachmentUri'. It is also possible retrieve a specific
      Storage Volume Attachment by the Server Profile and the Volume. For this option is required inform the param
      'serverProfileName' and the param 'storageVolumeName' or 'storageVolumeUri'."
requirements:
    - "python >= 2.7.9"
    - "hpOneView >= 2.0.1"
author: "Camila Balestrin (@balestrinc)"
options:
    config:
      description:
        - Path to a .json configuration file containing the OneView client configuration.
      required: true
    storageVolumeAttachmentUri:
      description:
        - Storage Volume Attachment uri.
      required: false
    storageVolumeUri:
      description:
        - Storage Volume uri.
      required: false
    storageVolumeName:
      description:
        - Storage Volume name.
      required: false
    serverProfileName:
      description:
        - Server Profile name.
      required: false
    options:
      description:
        - "Retrieve additional facts. Options available:
          'extraUnmanagedStorageVolumes' retrieve the list of extra unmanaged storage volumes.
          'paths' retrieve all paths or a specific attachment path for the specified volume attachment. To retrieve a
           specific path a 'pathUri' or a 'pathId' must be informed"
      required: false
notes:
    - "A sample configuration file for the config parameter can be found at:
       https://github.com/HewlettPackard/oneview-ansible/blob/master/examples/oneview_config-rename.json"
'''

EXAMPLES = '''
- name: Gather facts about all Storage Volume Attachments
  oneview_storage_volume_attachment_facts:
    config: "{{ config }}"
  delegate_to: localhost

- debug: var=storage_volume_attachments


- name: Gather facts about a Storage Volume Attachment by Server Profile and Volume
  oneview_storage_volume_attachment_facts:
    config: "{{ config }}"
    serverProfileName: "sp-web"
    storageVolumeName: "volume-test" # You could inform either the volume name or the volume uri
    # storageVolumeUri: "volume-test"
  delegate_to: localhost

- debug: var=storage_volume_attachments


- name: Gather facts about extra unmanaged storage volumes
  oneview_storage_volume_attachment_facts:
    config: "{{ config }}"
    options:
      - extraUnmanagedStorageVolumes:
            start: 0     # optional
            count: '-1'  # optional
            filter: ''   # optional
            sort: ''     # optional
  delegate_to: localhost

- debug: var=storage_volume_attachments
- debug: var=extra_unmanaged_storage_volumes

- name: Gather facts about all paths for the specified volume attachment
  oneview_storage_volume_attachment_facts:
    config: "{{ config }}"
    serverProfileName: "sp-web"
    storageVolumeUri: "/rest/storage-volumes/12345-AAA-BBBB-CCCC-121212AA"
    options:
      - paths
  delegate_to: localhost

- debug: var=storage_volume_attachments
- debug: var=storage_volume_attachment_paths

- name: Gather facts about a specific attachment path
  oneview_storage_volume_attachment_facts:
    config: "{{ config }}"
    serverProfileName: "sp-web"
    storageVolumeUri: "/rest/storage-volumes/12345-AAA-BBBB-CCCC-121212AA"
    options:
      - paths:
            # You could inform either the path id or the path uri
            pathId: '9DFC8953-15A4-4EA9-AB65-23AB12AB23' # optional
            # pathUri: '/rest/storage-volume-attachments/123-123-123/paths/123-123-123'
  delegate_to: localhost

- debug: var=storage_volume_attachments
- debug: var=storage_volume_attachment_paths
'''

RETURN = '''
storage_volume_attachments:
    description: Has all the OneView facts about the Storage Volume Attachments.
    returned: always, but can be null
    type: complex

extra_unmanaged_storage_volumes:
    description: Has facts about the extra unmanaged storage volumes.
    returned: when requested, but can be null
    type: complex

storage_volume_attachment_paths:
    description: Has facts about all paths or a specific attachment path for the specified volume attachment.
    returned: when requested, but can be null
    type: complex
'''
ATTACHMENT_KEY_REQUIRED = "Server Profile Name and Volume Name or Volume Uri are required."
SPECIFIC_ATTACHMENT_OPTIONS = ['storageVolumeAttachmentUri', 'storageVolumeUri', 'storageVolumeName',
                               'serverProfileName']


class StorageVolumeAttachmentFactsModule(object):
    argument_spec = {
        "config": {"required": True, "type": 'str'},
        "serverProfileName": {"required": False, "type": 'str'},
        "storageVolumeAttachmentUri": {"required": False, "type": 'str'},
        "storageVolumeUri": {"required": False, "type": 'str'},
        "storageVolumeName": {"required": False, "type": 'str'},
        "options": {"required": False, "type": 'list'}}

    def __init__(self):
        self.module = AnsibleModule(argument_spec=self.argument_spec, supports_check_mode=False)
        self.oneview_client = OneViewClient.from_json_file(self.module.params['config'])

        resource_uri = self.oneview_client.storage_volume_attachments.URI
        self.__search_attachment_uri = str(resource_uri) + "?filter=storageVolumeUri='{}'&filter=hostName='{}'"

    def run(self):
        try:
            facts = {}
            client = self.oneview_client.storage_volume_attachments
            params = self.module.params
            options = {}

            if params.get('options'):
                options = transform_list_to_dict(params['options'])

            param_specific_attachment = [entry for entry in SPECIFIC_ATTACHMENT_OPTIONS if params.get(entry)]

            if param_specific_attachment:
                attachments = self.__get_specific_attachment(params)
                self.__get_paths(attachments, options, facts)
            else:
                attachments = client.get_all()

            facts['storage_volume_attachments'] = attachments

            if options.get('extraUnmanagedStorageVolumes'):
                volumes_options = self.__get_sub_options(options['extraUnmanagedStorageVolumes'])
                facts['extra_unmanaged_storage_volumes'] = client.get_extra_unmanaged_storage_volumes(**volumes_options)

            self.module.exit_json(changed=False, ansible_facts=facts)

        except Exception as exception:
            self.module.fail_json(msg=exception.message)

    def __get_specific_attachment(self, params):

        attachment_uri = params.get('storageVolumeAttachmentUri')

        if attachment_uri:
            return [self.oneview_client.storage_volume_attachments.get(attachment_uri)]
        else:
            volume_uri = params.get('storageVolumeUri')
            profile_name = params.get('serverProfileName')

            if not profile_name or not (volume_uri or params.get('storageVolumeName')):
                raise Exception(ATTACHMENT_KEY_REQUIRED)

            if not volume_uri and params.get('storageVolumeName'):
                volumes = self.oneview_client.volumes.get_by('name', params.get('storageVolumeName'))
                if volumes:
                    volume_uri = volumes[0]['uri']

            uri = self.__search_attachment_uri.format(volume_uri, profile_name)
            attachments = self.oneview_client.storage_volume_attachments.get(uri) or {}

            return attachments.get('members')

    def __get_paths(self, attachments, options, facts):

        if attachments and 'paths' in options:

            attachment_uri = attachments[0]['uri']
            paths_options = self.__get_sub_options(options['paths'])
            path_id_or_uri = paths_options.get('pathId') or paths_options.get('pathUri')

            if path_id_or_uri:
                paths = [self.oneview_client.storage_volume_attachments.get_paths(attachment_uri, path_id_or_uri)]
            else:
                paths = self.oneview_client.storage_volume_attachments.get_paths(attachment_uri)

            facts['storage_volume_attachment_paths'] = paths

    def __get_sub_options(self, option):
        return option if type(option) is dict else {}


def main():
    StorageVolumeAttachmentFactsModule().run()


if __name__ == '__main__':
    main()
