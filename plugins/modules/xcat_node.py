#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: xcat_node
short_description: Module for updating an xCat node with a new image or
configuration. .
description:
    - Connect to the xCat API and execute the updates for the node.
options:
  name:
    description:
      - The name of the node.
    type: str
    required: true
  image:
    description:
      - The name of the image to be used for the node.
    type: str
    required: false
  action:
    description:
      - Action to be taken for the node
      - bootstate: Set the bootstate for the node and reset it.
    type: str
    required: true
    choices: ['bootstate']
  xcat_api:
    description:
      - URI of the xCat API
      - This needs to be a fully qualified URI string: http://127.0.0.1/xcatws
    type: str
    required: true
  xcat_token:
    description:
      - Token used to autenticate against the xCat API.
    type: str
    required: true
'''

EXAMPLES = r'''
- name: Set Node Bootstate
  community.xcat.xcat_node:
    name: 'stateless_node01'
    image: 'centos8-x86_64-netboot-stateless'
    action: 'bootstate'
    xcat_token: '1234567890'
    xcat_api: 'http://127.0.0.1/xcatws'

'''

RETURNS = r'''
changed:
  description:
    - Boolean parameter if the node state was updated or if there was a failure.
  type: bool
  returned: always
'''

import requests
import json
import sys

from ansible.module_utils.basic import AnsibleModule

class XcatNode:
    def __init__(self, image_args):
        self.__image_args = image_args
        self.__node_name = image_args['name']
        self.__image_name = image_args['image']
        self.__headers = {
            'X-Auth-Token': image_args['xcat_token'],
            'Content-Type': 'application/json'
        }

    def set_bootstate(self):
        bootstate_uri = (f"{self.__image_args['xcat_api']}"
                         f"/nodes/{self.__node_name}/bootstate")
        body_data = {"osimage": f"{self.__image_name}"}
        process_bootstate = requests.put(bootstate_uri, verify=False,
                                         headers=self.__headers, timeout=900,
                                         data=json.dumps(body_data))
        if process_bootstate.status_code != 200:
            sys.exit(1)


def run_xcat_node_module():

    module_args = dict(
        name=dict(type='str', required=False),
        image=dict(required=False, default=None),
        action=dict(type='str', required=True),
        xcat_token=dict(type='str', required=True),
        xcat_api=dict(type='str', required=True),
    )

    # Seed the results dictionary just in case.
    result = dict(
        changed=False,
    )

    # Setup the Ansible Module structure
    xcat_module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    image_args = {
        'name': xcat_module.params['name'],
        'image': xcat_module.params['image'],
        'action': xcat_module.params['action'],
        'xcat_token': xcat_module.params['xcat_token'],
        'xcat_api': xcat_module.params['xcat_api'],
    }

    node = XcatNode(image_args)

    if image_args['action'] == 'bootstate':
        node.set_bootstate()

    if xcat_module.check_mode:
        xcat_module.exit_json(**result)

    result['changed'] = True

    xcat_module.exit_json(**result)


def main():
    run_xcat_node_module()


if __name__ == '__main__':
    main()
