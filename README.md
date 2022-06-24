xCat Collection for Ansible
===========================

An [Ansible][ansible] collection for maintaining xCat images, image profiles,
and node functionality. This collection works with xCat version 2 with
implementations for extending xCat 3 in the future.

[ansible]: http://www.ansible.com/
[redline]: http://redlineperf.com/

Code of Conduct
---------------
We follow the [Ansible Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)
in all our interactions within this project.

Requirements
------------

This collection requires Ansible 2.4+

Included Content
----------------
- `xcat_image`: Module for handling various image tasks.
  - [xCat Image Module](https://github.com/redline/ansible-collection-xcat/plugins/modules/xcat_image.py)
- `xcat_node`: Module for handling node resets and settings.
  - [xCat Node Module](https://github.com/redline/ansible-collection-xcat/plugins/modules/xcat_node.py)
- `xcat_token`: Module for authenticating against the xCat API and getting the
authorization token.
  - [xCat Token Module](https://github.com/redline/ansible-collection-xcat/plugins/modules/xcat_token.py)

Using This Collection
=====================
Please ensure that you have the Ansible Galaxy command line utility installed on
your system before executing these instructions

Installing the Collection
-------------------------
1. Checkout the ansible-collection-xcat
```bash
git clone git@github.com:redline/ansible-collection-xcat
```
1. Install the ansible collection into your local Ansible environment
```bash
ansible-galaxy collection install ansible-collection-xcat
```
