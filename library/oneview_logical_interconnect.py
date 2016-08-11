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
from hpOneView.common import resource_compare


DOCUMENTATION = '''
---
module: oneview_logical_interconnect
short_description: Manage OneView Logical Interconnect resources.
description:
    - Provides an interface to manage Logical Interconnect resources.
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
            - Indicates the desired state for the Logical Interconnect resource.
              'compliant' brings the logical interconnect back to a consistent state.
              'ethernet_settings_updated' updates the Ethernet interconnect settings for the logical interconnect.
              'internal_networks_updated' updates the internal networks on the logical interconnect. This operation is
              non-idempotent.
              'settings_updated' updates the Logical Interconnect settings.
              'forwarding_information_base_generated' generates the forwarding information base dump file for the
              logical interconnect. This operation is non-idempotent and does not ensure that the operation is
              completed.
              'qos_aggregated_configuration_updated' updates the QoS aggregated configuration for the logical
              interconnect.
              'snmp_configuration_updated' updates the SNMP configuration for the logical interconnect.
              'port_monitor_updated' updates the port monitor configuration of a logical interconnect.
              'configuration_updated' asynchronously applies or re-applies the logical interconnect configuration
              to all managed interconnects. This operation is non-idempotent.
              'firmware_installed' installs firmware to a logical interconnect. The three operations that are supported
              for the firmware update are Stage (uploads firmware to the interconnect), Activate (installs firmware on
              the interconnect) and Update (which does a Stage and Activate in a sequential manner). All of them are
              non-idempotent.
        choices: ['compliant', 'ethernet_settings_updated', 'internal_networks_updated', 'settings_updated',
                  'forwarding_information_base_generated', 'qos_aggregated_configuration_updated',
                  'snmp_configuration_updated', 'port_monitor_updated', 'configuration_updated', 'firmware_installed']
    data:
      description:
        - List with the options.
      required: true
notes:
    - "A sample configuration file for the config parameter can be found at:
       https://github.com/HewlettPackard/oneview-ansible/blob/master/examples/oneview_config-rename.json"
'''

EXAMPLES = '''
- name: Return the logical interconnect to a consistent state
  oneview_logical_interconnect:
    config: "{{ config_file_path }}"
    state: compliant
    data:
      name: 'Name of the Logical Interconnect'

- name: Update the Ethernet interconnect settings for the logical interconnect
  oneview_logical_interconnect:
    config: "{{ config_file_path }}"
    state: ethernet_settings_updated
    data:
      name: "Name of the Logical Interconnect"
      ethernetSettings:
      macRefreshInterval: 10

- name: Update the internal networks on the logical interconnect
  oneview_logical_interconnect:
    config: "{{ config_file_path }}"
    state: internal_networks_updated
    data:
      name: "Name of the Logical Interconnect"
      internalNetworks:
        - name: "Name of the Ethernet Network 1"
        - name: "Name of the Ethernet Network 2"
        - uri: "/rest/ethernet-networks/8a58cf7c-d49d-43b1-94ce-da5621be490c"

- name: Update the interconnect settings
  oneview_logical_interconnect:
    config: "{{ config_file_path }}"
    state: settings_updated
    data:
      name: "Name of the Logical Interconnect"
      ethernetSettings:
        macRefreshInterval: 10

- name: Generate the forwarding information base dump file for the logical interconnect
  oneview_logical_interconnect
    config: "{{ config_file_path }}"
    state: forwarding_information_base_generated
    data:
      name: "Name of the Logical Interconnect"

- name: Update the QoS aggregated configuration for the logical interconnect
  oneview_logical_interconnect
    config: "{{ config_file_path }}"
    state: qos_aggregated_configuration_updated
    data:
      name: "Name of the Logical Interconnect"
      activeQosConfig:
        category: 'qos-aggregated-configuration'
        configType: 'Passthrough'
        downlinkClassificationType: ~
        uplinkClassificationType: ~
        qosTrafficClassifiers: []
        type: 'QosConfiguration'

- name: Update the SNMP configuration for the logical interconnect
  oneview_logical_interconnect:
    config: "{{ config_file_path }}"
    state: snmp_configuration_updated
    data:
      name: "Name of the Logical Interconnect"
      enabled: True
    delegate_to: localhost

- name: Update the port monitor configuration of the logical interconnect
  oneview_logical_interconnect:
    config: "{{ config_file_path }}"
    state: port_monitor_updated
    data:
      name: "Name of the Logical Interconnect"
      enablePortMonitor: False

  - name: Update the configuration on the logical interconnect
    oneview_logical_interconnect:
      config: "{{ config_file_path }}"
      state: configuration_updated
      data:
        name: "{{ logical_interconnect_name }}"

- name: Install a firmware to the logical interconnect
  oneview_logical_interconnect:
  config: "{{ config_file_path }}"
  state: firmware_installed
  data:
    name: "Name of the Logical Interconnect"
    firmware:
      - command: Update
      - spp: spp-filename
'''

LOGICAL_INTERCONNECT_CONSISTENT = 'logical interconnect returned to a consistent state.'
LOGICAL_INTERCONNECT_ETH_SETTINGS_UPDATED = 'Ethernet settings updated successfully.'
LOGICAL_INTERCONNECT_INTERNAL_NETWORKS_UPDATED = 'Internal networks updated successfully.'
LOGICAL_INTERCONNECT_SETTINGS_UPDATED = 'Logical Interconnect setttings updated successfully.'
LOGICAL_INTERCONNECT_QOS_UPDATED = 'QoS aggregated configuration updated successfully.'
LOGICAL_INTERCONNECT_SNMP_UPDATED = 'SNMP configuration updated successfully.'
LOGICAL_INTERCONNECT_PORT_MONITOR_UPDATED = 'Port Monitor configuration updated successfully.'
LOGICAL_INTERCONNECT_CONFIGURATION_UPDATED = 'configuration on the logical interconnect updated successfully.'
LOGICAL_INTERCONNECT_FIRMWARE_INSTALLED = 'Firmware updated successfully.'
LOGICAL_INTERCONNECT_NOT_FOUND = 'Logical Interconnect not found.'
LOGICAL_INTERCONNECT_ETH_NETWORK_NOT_FOUND = 'Ethernet network not found: '
LOGICAL_INTERCONNECT_NO_CHANGES_PROVIDED = 'Nothing to do.'
LOGICAL_INTERCONNECT_NO_OPTIONS_PROVIDED = 'No options provided.'


class LogicalInterconnectModule(object):

    argument_spec = dict(
        config=dict(required=True, type='str'),
        state=dict(
            required=True,
            choices=['compliant', 'ethernet_settings_updated', 'internal_networks_updated', 'settings_updated',
                     'forwarding_information_base_generated', 'qos_aggregated_configuration_updated',
                     'snmp_configuration_updated', 'port_monitor_updated', 'configuration_updated',
                     'firmware_installed']
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
            resource = self.__get_by_name(data)

            if resource:
                uri = resource['uri']

                if state == 'compliant':
                    self.__compliance(uri)
                if state == 'ethernet_settings_updated':
                    self.__update_ethernet_settings(resource, data)
                if state == 'internal_networks_updated':
                    self.__update_internal_networks(uri, data)
                if state == 'settings_updated':
                    self.__update_settings(resource, data)
                if state == 'forwarding_information_base_generated':
                    self.__generate_forwarding_information_base(uri)
                if state == 'qos_aggregated_configuration_updated':
                    self.__update_qos_configuration(uri, data)
                if state == 'snmp_configuration_updated':
                    self.__update_snmp_configuration(uri, data)
                if state == 'port_monitor_updated':
                    self.__update_port_monitor(uri, data)
                if state == 'configuration_updated':
                    self.__update_configuration(uri)
                if state == 'firmware_installed':
                    self.__install_firmware(uri, data)
            else:
                raise Exception(LOGICAL_INTERCONNECT_NOT_FOUND)

        except Exception as exception:
            self.module.fail_json(msg=exception.message)

    def __compliance(self, uri):
        li = self.oneview_client.logical_interconnects.update_compliance(uri)

        self.module.exit_json(changed=True,
                              msg=LOGICAL_INTERCONNECT_CONSISTENT,
                              ansible_facts=dict(logical_interconnect=li))

    def __update_ethernet_settings(self, resource, data):
        if 'ethernetSettings' in data:
            ethernet_settings_merged = resource['ethernetSettings'].copy()
            ethernet_settings_merged.update(data['ethernetSettings'])

            if resource_compare(resource['ethernetSettings'], ethernet_settings_merged):
                self.module.exit_json(changed=False,
                                      msg=LOGICAL_INTERCONNECT_NO_CHANGES_PROVIDED)
            else:
                li = self.oneview_client.logical_interconnects.update_ethernet_settings(resource['uri'],
                                                                                        ethernet_settings_merged)
                self.module.exit_json(changed=True,
                                      msg=LOGICAL_INTERCONNECT_ETH_SETTINGS_UPDATED,
                                      ansible_facts=dict(logical_interconnect=li))

        else:
            raise Exception(LOGICAL_INTERCONNECT_NO_OPTIONS_PROVIDED)

    def __update_internal_networks(self, uri, data):
        if 'internalNetworks' in data:
            networks = []
            for network_uri_or_name in data['internalNetworks']:
                if 'name' in network_uri_or_name:
                    ethernet_network = self.__get_ethernet_network_by_name(network_uri_or_name['name'])
                    if not ethernet_network:
                        raise Exception(LOGICAL_INTERCONNECT_ETH_NETWORK_NOT_FOUND + network_uri_or_name['name'])
                    networks.append(ethernet_network['uri'])
                elif 'uri' in network_uri_or_name:
                    networks.append(network_uri_or_name['uri'])

            li = self.oneview_client.logical_interconnects.update_internal_networks(uri, networks)

            self.module.exit_json(changed=True,
                                  ansible_facts=dict(logical_interconnect=li),
                                  msg=LOGICAL_INTERCONNECT_INTERNAL_NETWORKS_UPDATED)
        else:
            raise Exception(LOGICAL_INTERCONNECT_NO_OPTIONS_PROVIDED)

    def __update_settings(self, resource, data):
        if 'ethernetSettings' in data or 'fcoeSettings' in data:
            ethernet_settings_merged = resource['ethernetSettings'].copy()
            fcoe_settings_merged = resource['fcoeSettings'].copy()

            if 'ethernetSettings' in data:
                ethernet_settings_merged.update(data['ethernetSettings'])

            if 'fcoeSettings' in data:
                fcoe_settings_merged.update(data['fcoeSettings'])

            if resource_compare(resource['ethernetSettings'], ethernet_settings_merged) and \
               resource_compare(resource['fcoeSettings'], fcoe_settings_merged):

                self.module.exit_json(changed=False,
                                      msg=LOGICAL_INTERCONNECT_NO_CHANGES_PROVIDED)
            else:
                settings = {
                    'ethernetSettings': ethernet_settings_merged,
                    'fcoeSettings': fcoe_settings_merged
                }
                li = self.oneview_client.logical_interconnects.update_settings(resource['uri'], settings)
                self.module.exit_json(changed=True,
                                      msg=LOGICAL_INTERCONNECT_SETTINGS_UPDATED,
                                      ansible_facts=dict(logical_interconnect=li))
        else:
            raise Exception(LOGICAL_INTERCONNECT_NO_OPTIONS_PROVIDED)

    def __generate_forwarding_information_base(self, uri):
        result = self.oneview_client.logical_interconnects.create_forwarding_information_base(uri)

        self.module.exit_json(changed=True,
                              msg=result.get('status'),
                              ansible_facts=dict(interconnect_fib=result))

    def __update_qos_configuration(self, uri, data):
        if 'qosAggregatedConfiguration' in data:
            qos_config = self.__get_qos_aggregated_configuration(uri)
            qos_config_merged = self.__merge_options_with_subresource(data['qosAggregatedConfiguration'], qos_config)

            if resource_compare(qos_config_merged, qos_config):

                self.module.exit_json(changed=False,
                                      msg=LOGICAL_INTERCONNECT_NO_CHANGES_PROVIDED)
            else:
                qos_config_updated = self.oneview_client.logical_interconnects.update_qos_aggregated_configuration(
                    uri, qos_config_merged)

                self.module.exit_json(changed=True,
                                      msg=LOGICAL_INTERCONNECT_QOS_UPDATED,
                                      ansible_facts=dict(qos_aggregated_configuration=qos_config_updated))
        else:
            raise Exception(LOGICAL_INTERCONNECT_NO_OPTIONS_PROVIDED)

    def __update_snmp_configuration(self, uri, data):
        if 'snmpConfiguration' in data:
            snmp_config = self.__get_snmp_configuration(uri)
            snmp_config_merged = self.__merge_options_with_subresource(data['snmpConfiguration'], snmp_config)

            if resource_compare(snmp_config_merged, snmp_config):

                self.module.exit_json(changed=False,
                                      msg=LOGICAL_INTERCONNECT_NO_CHANGES_PROVIDED)
            else:
                snmp_config_updated = self.oneview_client.logical_interconnects.update_snmp_configuration(
                    uri, snmp_config_merged)

                self.module.exit_json(changed=True,
                                      msg=LOGICAL_INTERCONNECT_SNMP_UPDATED,
                                      ansible_facts=dict(snmp_configuration=snmp_config_updated))
        else:
            raise Exception(LOGICAL_INTERCONNECT_NO_OPTIONS_PROVIDED)

    def __update_port_monitor(self, uri, data):
        if 'portMonitor' in data:
            monitor_config = self.__get_port_monitor_configuration(uri)
            monitor_config_merged = self.__merge_options_with_subresource(data['portMonitor'], monitor_config)

            if resource_compare(monitor_config_merged, monitor_config):
                self.module.exit_json(changed=False,
                                      msg=LOGICAL_INTERCONNECT_NO_CHANGES_PROVIDED)
            else:
                monitor_config_updated = self.oneview_client.logical_interconnects.update_port_monitor(
                    uri, monitor_config_merged)

                self.module.exit_json(changed=True,
                                      msg=LOGICAL_INTERCONNECT_PORT_MONITOR_UPDATED,
                                      ansible_facts=dict(port_monitor_configuration=monitor_config_updated))
        else:
            raise Exception(LOGICAL_INTERCONNECT_NO_OPTIONS_PROVIDED)

    def __install_firmware(self, uri, data):
        if 'firmware' in data:
            options = data['firmware'].copy()
            if 'spp' in options:
                options['sppUri'] = '/rest/firmware-drivers/' + options.pop('spp')

            firmware = self.oneview_client.logical_interconnects.install_firmware(options, uri)

            self.module.exit_json(changed=True,
                                  ansible_facts=dict(firmware=firmware),
                                  msg=LOGICAL_INTERCONNECT_FIRMWARE_INSTALLED)
        else:
            raise Exception(LOGICAL_INTERCONNECT_NO_OPTIONS_PROVIDED)

    def __update_configuration(self, uri):
        result = self.oneview_client.logical_interconnects.update_configuration(uri)

        self.module.exit_json(changed=True,
                              msg=LOGICAL_INTERCONNECT_CONFIGURATION_UPDATED,
                              ansible_facts=dict(logical_interconnect=result))

    def __get_by_name(self, data):
        return self.oneview_client.logical_interconnects.get_by_name(data['name'])

    def __get_ethernet_network_by_name(self, name):
        result = self.oneview_client.ethernet_networks.get_by('name', name)
        return result[0] if result else None

    def __get_qos_aggregated_configuration(self, uri):
        return self.oneview_client.logical_interconnects.get_qos_aggregated_configuration(uri)

    def __get_snmp_configuration(self, uri):
        return self.oneview_client.logical_interconnects.get_snmp_configuration(uri)

    def __get_port_monitor_configuration(self, uri):
        return self.oneview_client.logical_interconnects.get_port_monitor(uri)

    def __merge_options_with_subresource(self, data, subresource):
        options = data.copy()

        options_merged = subresource.copy()
        options_merged.update(options)

        return options_merged


def main():
    LogicalInterconnectModule().run()


if __name__ == '__main__':
    main()
