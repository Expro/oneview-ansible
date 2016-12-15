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

import unittest
import yaml

from image_streamer_golden_image_facts import GoldenImageFactsModule, EXAMPLES
from utils import ModuleContructorTestCase

ERROR_MSG = 'Fake message error'


class GoldenImageFactsSpec(unittest.TestCase, ModuleContructorTestCase):
    """
    Test the module constructor
    ModuleContructorTestCase has common tests for class constructor and main function
    """

    def setUp(self):
        self.configure_mocks(self, GoldenImageFactsModule)
        self.i3s = self.mock_ov_client.create_image_streamer_client()

        # Load scenarios from module examples
        self.GOLDEN_IMAGE_FACTS_EXAMPLES = yaml.load(EXAMPLES)

        self.TASK_GET_ALL = self.GOLDEN_IMAGE_FACTS_EXAMPLES[0]['image_streamer_golden_image_facts']
        self.TASK_GET_BY_NAME = self.GOLDEN_IMAGE_FACTS_EXAMPLES[2]['image_streamer_golden_image_facts']
        self.TASK_GET_ARCHIVE = self.GOLDEN_IMAGE_FACTS_EXAMPLES[4]['image_streamer_golden_image_facts']

        self.GOLDEN_IMAGE = dict(
            name="Golden Image name",
            uri="/rest/golden-image/d1c7b09a-6c7b-4ae0-b68e-ed208ccde1b0")

    def test_get_all_golden_images(self):
        self.i3s.golden_images.get_all.return_value = [self.GOLDEN_IMAGE]
        self.mock_ansible_module.params = self.TASK_GET_ALL

        GoldenImageFactsModule().run()

        self.mock_ansible_module.exit_json.assert_called_once_with(
            changed=False,
            ansible_facts=dict(golden_images=[self.GOLDEN_IMAGE])
        )

    def test_get_a_golden_image_by_name(self):
        self.i3s.golden_images.get_by.return_value = [self.GOLDEN_IMAGE]
        self.mock_ansible_module.params = self.TASK_GET_BY_NAME

        GoldenImageFactsModule().run()

        self.mock_ansible_module.exit_json.assert_called_once_with(
            changed=False,
            ansible_facts=dict(golden_images=[self.GOLDEN_IMAGE])
        )

    def test_get_a_golden_image_by_name_with_archive_option(self):
        self.i3s.golden_images.get_by.return_value = [self.GOLDEN_IMAGE]
        self.i3s.golden_images.get_archive.return_value = "Golden Image logs"

        self.mock_ansible_module.params = self.TASK_GET_ARCHIVE

        GoldenImageFactsModule().run()

        self.mock_ansible_module.exit_json.assert_called_once_with(
            changed=False,
            ansible_facts=dict(
                golden_images=[self.GOLDEN_IMAGE],
                golden_image_archive="Golden Image logs"
            )
        )

    def test_should_fail_when_get_all_raises_an_exception(self):
        self.i3s.golden_images.get_all.side_effect = Exception(ERROR_MSG)
        self.mock_ansible_module.params = self.TASK_GET_ALL

        GoldenImageFactsModule().run()

        self.mock_ansible_module.fail_json.assert_called_once_with(msg=ERROR_MSG)


if __name__ == '__main__':
    unittest.main()
