#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: xcat_token
short_description: Module for authenticating against the xCat API and generating
an authorization token.
description:
  - Call the xCat API and generate an authorization token.
  - This module does require the use of the requests Python module to be installed
  on the destination system.
options:
  xcat_api:
    description:
      - URI of the xCat API
      - This needs to be a fully qualified URI string: http://127.0.0.1/xcatws
    type: str
    required: true
  xcat_api_user:
    description:
      - The user name to authenticate against the API
    type: str
    required: true
  xcat_api_password:
    description:
      - The password for the API user.
    type: str
    required: true
'''

EXAMPLES = r'''
- name: "Generate the xCat Token for the API"
  community.xcat.xcat_token:
    xcat_api: http://127.0.0.1/xcatws
    xcat_api_user: xcat_user
    xcat_api_password: xcat_password
  register: xcat_token
'''

RETURNS = r'''
token:
  description:
    - JSON dictionary that contains the token ID and expiration date.
  returned: success
  type: list
  elements: dict
  contains:
    id:
      description:
        - The authentication token
      type: str
      returned: success
    expire:
      description:
        - The expiration date of the token
      type: str
      returned: success
'''

import requests
import json

from ansible.module_utils.basic import AnsibleModule

def generate_token(token_args):
  """
  This method is used to generate the token from the xcat API by using
  the xcat_api arguemnt as the base URI and appending the /tokens 
  endpoint to it. Then using the user name and password in a JSON
  header, pass that information in and get the token string back
  from the API

  Parameters
  ----------
  token_args : dict
    This is a dictionary of the arguments passed into the module that
    includes the API URI, user name, and password

  Returns
  -------
  token : json
    The JSON object that is obtained from the XCAT API that includes
    the token ID string and the expiration date. 
  """
  get_token = f"{token_args['xcat_api']}/tokens"
  user_data = {'userName': token_args['xcat_api_user'],
               'userPW': token_args['xcat_api_password']}
  token = requests.post(get_token, verify=False,
                        headers={'Content-Type': 'application/json'},
                        data=json.dumps(user_data))
  return token.json()


def run_xcat_module():
  """
  This is the main xcat module call from the main() method. The goal
  of this is to parse the arguments that were sent in from the 
  Ansible call to the indiovidual arguments, call the generate_token
  method and then return the values so that the Ansible playbook
  can use the token in other modules. 

  Parameters 
  ----------
  None

  Returns
  -------
  None
  """

  module_args = dict(
      xcat_api=dict(type='str', required=True),
      xcat_api_user=dict(type='str', required=True),
      xcat_api_password=dict(type='str', required=True),
  )

  # Seed the results dictionary just in case.
  result = dict(
      changed=False,
  )

  xcat_module = AnsibleModule(
      argument_spec=module_args,
      supports_check_mode=True
  )

  token_args = {
      'xcat_api': xcat_module.params['xcat_api'],
      'xcat_api_user': xcat_module.params['xcat_api_user'],
      'xcat_api_password': xcat_module.params['xcat_api_password'],
  }

  token = generate_token(token_args)

  result['token'] = token['token']

  if xcat_module.check_mode:
      xcat_module.exit_json(**result)

  xcat_module.exit_json(**result)

def main():
  """
  Main module

  Parameters
  ----------
  None

  Returns
  -------
  None
  """
  run_xcat_module()

if __name__ == '__main__':
  main()
