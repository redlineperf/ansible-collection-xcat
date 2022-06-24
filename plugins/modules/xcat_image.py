#!/usr/bin/python

DOCUMENTATION = r'''
---
module: xcat_image
short_description: Module for managing xCat stateful and stateless images.
description:
    - Connect to the xCat API and create either stateless or stateful images.
options:
  name:
    description:
      - The name of the image.
      - If the image name is not used then this name is used in the format
      osvers-osarch-provmethod-name
    type: str
    required: true
  image_name:
    description:
      - The name of the image to be used.
      - If the image_name is specified that is what will be used. If not it
      will use a combination of the name parameter in the format of
      osvers-osarch-provmethod-name. 
    type: str
    required: false
  state:
    description:
      - Identify if the image is stateles or stateful.
    type: str
    required: true
    choices: ['stateless', 'stateful]
  objtype:
    description:
      - The object type to be passed to the xCat API when creating or managing 
      the image.
      - This should almost always be the default osimage. 
    type: str
    required: false
    default: osimage
  exlist:
    description:
      - The fully qualified name of the file that stores the file names and 
      directory names that will be excluded from the image during packimage command. 
      It is used for diskless image only.
    type: str
    required: false
  imagetype:
    description:
      - The type of image to create. 
    type: str
    required: false
    default: linux
  osarch:
    description:
      - The hardware architecture of this node. 
      - Valid values: x86_64, ppc64, x86, ia64. 
    type: str
    required: false
    default: x86_64
    choices: ['x86_64', 'ppc64', 'x86', 'ia64']
  osdistroname:
    description:
      - The name of the OS distro definition.
      - This attribute can be used to specify which OS distro to use, 
      instead of using the osname,osvers,and osarch attributes.
    type: str
    required: false
  osname:
    description:
      - Operating system name- AIX or Linux.
    required: false
    type: str
    choices: ['AIX','Linux']
    default: LinuxThe fully qualified name of the file that stores the distro packages list that will be included in the image. 
    description: 
      - The Linux operating system deployed on this node. 
      - Valid values: rhels*,rhelc*, rhas*,centos*,rocky*,SL*, fedora*, sles* 
      (where * is the version #).
    required: true
    type: str
  otherpkgdir:
    description:
      - The base directory and urls of internet repos from which the non-distro packages are retrived. 
      - Only 1 local directory is supported at present.
      - The entries should be delimited with comma “,”.
    required: false
    type: str
  permission:
    description:
      - The mount permission of /.statelite directory. 
    required: false
    type: int
    default: 755
  pkgdir:
    description:
      - The name of the directory where the distro packages are stored. 
      - It could be set to multiple paths. 
      - The multiple paths must be separated by “,”.
    required: false
    type: str
  pkglist
    description:
      - The fully qualified name of the file that stores the distro packages list that will be 
      included in the image. 
    required: false
    type: str
  postinstall:
    description:
      - Supported in diskless image only. 
      - The fully qualified name of the scripts and the user-specified arguments running in 
      non-chroot mode after the package installation but before initrd generation during genimage.
      - If multiple scripts are specified, they should be seperated with comma “,”.
    required: false
    type: str
  profile:
    description:
      - The node usage category. For example compute.
    required: false
    type: str
    default: compute
  rootimgdir:
    description:
      - The directory name where the image is stored.
      - It is generally used for diskless image.
    required: false
    type: str
  operation:
    description:
      - The type of operation to execute with the image. 
      - Package: pack up the image
      - Generate: generate the image. 
    type: str
    required: true
    choices: ['package', 'generate']
  template:
    description:
      - The fully qualified name of the template file that will be used to create the 
      OS installer configuration file for stateful installations.
    type: str
    required: false
  update:
    description:
      - If the image already exists, use true to update it with any new parameters.
      - If false, then if the image exists it will use the existing image only and
      will not update any packages or parameters. 
    type: bool
    required: false
    default: false
  xcat_api:
    description:
      - The full URI to the xcat API
    required: true
    type: str
  xcat_token:
    description:
      - Token used to autenticate against the xCat API.
    type: str
    required: true
'''

EXAMPLES = r'''
- name: "Generate xCat Image for ansible_stateless"
  community.xcat.xcat_image:
    name: "ansible_stateless"
    state: stateless
    operation: generate
    exlist: /tmp/centos/ansible_stateless.centos8.x86_64.exlist
    osdistroname: centos8-x86_64
    osvers: centos8
    otherpkgdir: /data/otherpkgs/centos8/x86_64
    pkgdir: /data/centos8/x86_64
    pkglist: /tmp/centos/ansible_stateless.centos8.x86_64.pkglist
    postinstall: /tmp/centos/ansible_stateless.centos8.x86_64.postinstall
    rootimgdir: /install/stateless/centos8/x86_64/ansible_stateless
    xcat_token: 1234567890
    xcat_api: http://127.0.0.1/xcatws
  register: xcat_image

  # Yum can then be used on the existing stateless image to deploy 
  # additional packages. 
- name: "Installing packages on ansible_stateless"
  yum:
    name: "{{ item }}"
    state: present
    installroot: /install/stateless/centos8/x86_64/ansible_stateless/rootimg"
  loop:
    - python38-psycopg2
  become: yes
  become_user: root
  when:
  - image.packages is defined
  - xcat_image.update

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

class XcatImage:

    def __init__(self, image_args):
        self.image_args = image_args
        if image_args['image_name'] is not None:
            self.image_name = image_args['image_name']
        else:
            self.image_name = (f"{self.image_args['osvers']}-"
                               f"{self.image_args['osarch']}-"
                               f"{self.image_args['provmethod']}-"
                               f"{self.image_args['name']}")
        self.image_options = [
            'imagetype', 'osarch', 'osdistroname', 'osname',
            'osvers', 'otherpkgdir', 'pkgdir', 'pkglist', 'profile',
            'provmethod', 'synclists', 'template', 'permission', 'postinstall',
            'rootimgdir',
        ]
        self.__common_options = [
            'objtype', 'imagetype', 'osarch', 'osdistroname', 'osname',
            'osvers', 'otherpkgdir', 'pkgdir', 'pkglist', 'profile',
            'provmethod',
        ]
        self.__stateful_options = [
            'template'
        ]
        self.__stateless_options = [
            'permission', 'exlist', 'rootimgdir'
        ]
        self.headers = {
            'X-Auth-Token': self.image_args['xcat_token'],
            'Content-Type': 'application/json'
        }

    def get_image_name(self):
        return self.image_name

    def exists(self):
        verify_image = f"{self.image_args['xcat_api']}/osimages/{self.image_name}"
        image_exists = requests.get(verify_image, verify=False,
                                    headers=self.headers)
        if image_exists.status_code == 200:
            self.image_contents = image_exists.json()
            return True
        elif image_exists.status_code == 403:
            return False
        else:
            sys.exit(1)

    def update(self):
        gen_image = False
        update_endpoint = (f"{self.image_args['xcat_api']}/osimages/"
                           f"{self.image_name}")
        for key, value in self.image_contents[self.image_name].items():
            if value != self.image_args[key]:
                body_data = {key: self.image_args[key] }
                process_update = requests.put(update_endpoint, verify=False,
                                              headers=self.headers,
                                              data=json.dumps(body_data))
                if process_update.status_code != 200:
                    sys.exit(1)
                else:
                    gen_image = True
        for key, value in self.image_args.items():
            if not key in self.image_contents[self.image_name] and \
                    key in self.__common_options:
                body_data = {key: self.image_args[key]}
                process_update = requests.put(update_endpoint, verify=False,
                                              headers=self.headers,
                                              data=json.dumps(body_data))
                if process_update.status_code != 200:
                    sys.exit(1)
                else:
                    gen_image = True
        if gen_image:
            self.generate()


    def generate(self):
        generate_endpoint = (f"{self.image_args['xcat_api']}/osimages/"
                             f"{self.image_name}/instance")
        body_data = {"action":"gen",
                     "params": [{"--tempfile": self.image_name}]}
        process_generate = requests.post(generate_endpoint, verify=False,
                                         headers=self.headers, timeout=900,
                                         data=json.dumps(body_data))
        if process_generate.status_code != 201:
            sys.exit(1)

    def create(self):
        create_endpoint = (f"{self.image_args['xcat_api']}/osimages/"
                           f"{self.image_name}")
        body_data = {}
        for key in self.__common_options:
            if key in self.image_args.keys():
                body_data[key] = self.image_args[key]
        if self.image_args['state'] == 'stateful':
            for key in self.__stateful_options:
                if key in self.image_args.keys():
                    body_data[key] = self.image_args[key]
        if self.image_args['state'] == 'stateless':
            for key in self.__stateless_options:
                if key in self.image_args.keys():
                    body_data[key] = self.image_args[key]
        process_create = requests.post(create_endpoint, verify=False,
                                       headers=self.headers, timeout=900,
                                       data=json.dumps(body_data))
        if process_create.status_code != 201:
            return False
        else:
            return True

    def pack_up(self):
        packup_endpoint = (f"{self.image_args['xcat_api']}/osimages/"
                           f"{self.image_name}/instance")
        body_data = {"action":"pack",
                     "params": [{"--tempfile": self.image_name}]}
        process_packup = requests.post(packup_endpoint, verify=False,
                                       headers=self.headers, timeout=900,
                                       data=json.dumps(body_data))
        if process_packup.status_code != 201:
            sys.exit(1)

class xcat_stateless:
    def __init__(self, image_args):
        print("stateless image")

def run_xcat_module():

    # Module Arguments
    module_args = dict(
        name=dict(type='str',required=True),
        image_name=dict(required=False, default=None),
        state=dict(type='str',required=True),
        operation=dict(type='str',required=False,default='generate'),
        objtype=dict(type='str',required=False, default='osimage'),
        exlist=dict(type='str',required=False),
        imagetype=dict(type='str',required=False, default='linux'),
        osarch=dict(type='str',required=False, default='x86_64'),
        osdistroname=dict(type='str',required=False),
        osname=dict(type='str',required=False, default='Linux'),
        osvers=dict(type='str',required=True),
        otherpkgdir=dict(type='str',required=False),
        permission=dict(type='str',required=False, default=755),
        pkgdir=dict(type='str',required=False),
        pkglist=dict(type='str',required=False),
        postinstall=dict(type='str',required=False),
        profile=dict(type='str',required=False, default='compute'),
        rootimgdir=dict(type='str',required=False),
        template=dict(type='str',required=False),
        update=dict(type='bool',required=False,default=False),
        xcat_token=dict(type='str',required=True),
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
        'image_name': xcat_module.params['image_name'],
        'state': xcat_module.params['state'],
        'objtype': xcat_module.params['objtype'],
        'exlist': xcat_module.params['exlist'],
        'imagetype': xcat_module.params['imagetype'],
        'osarch': xcat_module.params['osarch'],
        'osdistroname': xcat_module.params['osdistroname'],
        'osname': xcat_module.params['osname'],
        'osvers': xcat_module.params['osvers'],
        'otherpkgdir': xcat_module.params['otherpkgdir'],
        'permission': xcat_module.params['permission'],
        'pkgdir': xcat_module.params['pkgdir'],
        'pkglist': xcat_module.params['pkglist'],
        'postinstall': xcat_module.params['postinstall'],
        'profile': xcat_module.params['profile'],
        'rootimgdir': xcat_module.params['rootimgdir'],
        'operation': xcat_module.params['operation'],
        'template': xcat_module.params['template'],
        'update': xcat_module.params['update'],
        'xcat_token': xcat_module.params['xcat_token'],
        'xcat_api': xcat_module.params['xcat_api'],
    }

    if image_args['state'] == 'stateless':
        image_args['provmethod'] = 'netboot'
    elif image_args['state'] == 'stateful':
        image_args['provmethod'] = 'install'
    else:
        xcat_module.exit_json(**result)

    image = XcatImage(image_args)

    if image.exists() and image_args['update']:
        image.update()
    elif image_args['operation'] == 'generate' and not image.exists():
        if image.create():
            image.generate()
        else:
            print(f"Image {image_args['name']} not created.")
    elif image_args['operation'] == 'package' and image.exists():
        image.pack_up()

    result['image_name'] = image.get_image_name()
    result['update'] = image_args['update']

    if xcat_module.check_mode:
        xcat_module.exit_json(**result)

    xcat_module.exit_json(**result)

def main():
    run_xcat_module()

if __name__ == '__main__':
    main()
