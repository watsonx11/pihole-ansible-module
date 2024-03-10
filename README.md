# Pihole Ansible Module

This repo contains a custom Ansible collection for `pihole`.

## Tested with Ansible
Tested with the current ansible-core 2.16.x.
Tested with Python 3.12.x. 

Future versions will include previous version of both ansible-core and Python.

## Included content
* Pihole plugins:
    - ansible_pihole: Manage Pi-Hole deployments

## Using this collection

Before using this collection, yo uwill need to clone the repository, and place the `ansible_pihole.py` file in the same directory
as the playbook to be used, in a subdirectory title library

```
- site.yaml
|
|-library/
    |
    |-- ansible_pihole.py
```

## Available parameters

The following parameters are available, at this point in development all parameters are set to required=false

* pihole_path:
    - str
        - Default: `pihole`
    - Allows the user to set the non-standard path for the pihole command
* update_pihole:
    - true/false
        - Default: false
    - Effective to `pihole -up`
* update_gravity:
    - true/false
        - Default: false
    - Effective to `pihole -g`
* flush_log:
    - true/false
        - default: false
    - Effective to `pihole -f`
* restart_dns:
    - true/false
        - default: false
    - Effective to `pihole restartdns`
* blacklist:
    - str
    - Effective to `pihole blacklist <domain>`
* whitelist:
    - str
    - Effective to `pihole whitelist <domain>`
* enable_pihole:
    - true/false
        - default: true
    - Effective to `pihole enable(disable)`
* admin_pwd:
    - str
    - Effective to `pihole -a -p <password>`

## Examples

```
- name: Update Pi-Hole and Gravity if needed
  ansible_pihole:
    update_pihole: true
    update_gravity: true
```

```
- name: Disable Pi-Hole ad blocking
  ansible_pihole:
    pihole_enable: false
```

```
- name: Enable Pi-Hole ad blocking and flush logs
  ansible_pihole:
    pihole_enable: true
    flush_log: true
```

```
- name: Change Web Admin Password w/ non-standard pihole path
  ansible_pihole:
    pihole_path: /path/to/pihole
    admin_pwd: '{{ admin_password }}'
```