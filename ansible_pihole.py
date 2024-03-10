#!/usr/bin/python
#
# Copyright (c) 2024 Sean Watson
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)

import subprocess
import re
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
module: pihole_management
short_description: Manage Pi-hole settings and lists via Ansible
version_added: "1.0.0"
author: "Sean Watson"
description:
    - This module provides automation for managing Pi-holle settings and lists directly from Ansible playbooks
    - It allows for updating Pi-hole, its gravity database, flushing logs, restarting DNS, modifying the blacklist and whitelist, and toggling Pi-hole's operational state.
options:
    update_pihole:
    description: Whether to update Pi-hole to the latest version.
    type: bool
    required: False
    default: False
  update_gravity:
    description: Whether to update the gravity list, Pi-hole's main ad-blocking list compiled from multiple sources.
    type: bool
    required: False
    default: False
  flush_log:
    description: Whether to flush all DNS logs.
    type: bool
    required: False
    default: False
  restart_dns:
    description: Whether to restart the DNS service.
    type: bool
    required: False
    default: False
  blacklist:
    description: Domain to add to the blacklist. Can be used to block specific domains.
    type: str
    required: False
  whitelist:
    description: Domain to add to the whitelist. Can be used to allow specific domains that might be blocked.
    type: str
    required: False
  enable_pihole:
    description: Whether to enable or disable Pi-hole. When disabled, Pi-hole will not block any domains.
    type: bool
    required: False
    default: True
  admin_pwd:
    description: Change the Web Admin password
    type: str
    required: False
notes:
  - This module performs operations that can affect network behavior, particularly related to domain name resolution and blocking.
  - Ensure that you have appropriate permissions and that actions taken are in compliance with your organization's policies.
  - The module executes commands on the host where Pi-hole is installed, requiring sufficient access rights to perform these actions.
  - This module uses best-effort checks to avoid unnecessary updates or actions, but some operations, like DNS log flushing, do not have checks and will always be executed if requested.
requirements:
  - Pi-hole installed on the target system.
  - AnsibleModule from ansible.module_utils.basic for Ansible integration.
  - subprocess module for executing system commands.
license: GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
'''

EXAMPLES = '''

# The examples are using the module pihole:, this is the name of the .py you have called it in the ./library/ directory

- name: Disable Pi-Hole ad blocking
  pihole:
    enable_pihole: false

- name: Change Pi-Hole Web Admin Password
  pihole:
    admin_pwd: '{{ admin_pwd }}'

- name: Add sites to Blacklist
  pihole:
    blacklist: '{{ item.url }}
  loop:
    - { url: 'example.com' }
    - { url: 'foo.bar' }
'''

def execute_command(command):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        # Including both stdout and stderr for comprehensive debugging information
        return False, f"STDOUT: {e.stdout}\nSTDERR: {e.stderr}"

def main():

    no_update_phrases = [
        "nothing to update",
        "up to date",
        "list stayed unchanged",
        "blocking already enabled",
        "blocking already disabled"
    ]

    blacklist_no_update_phrases = [
        "already exists"
    ]

    whitelist_no_update_phrases = [
        "already exists"
    ]

    module = AnsibleModule(
        argument_spec={
            'update_pihole': {'type': 'bool', 'required': False, 'default': False},
            'update_gravity': {'type': 'bool', 'required': False, 'default': False},
            'flush_log': {'type': 'bool', 'required': False, 'default': False},
            'restart_dns': {'type': 'bool', 'required': False, 'default': False},
            'blacklist': {'type': 'str', 'required': False},
            'whitelist': {'type': 'str', 'required': False},
            'enable_pihole': {'type': 'bool', 'required': False, 'default': True},
            'admin_pwd': {'type': 'str', 'required': False},
        }
    )

    pihole_cmd = "pihole"
    commands = []
    # Update Pihole if new version exists
    if module.params['update_pihole']:
        commands.append(("Pi-hole update", [pihole_cmd, "-up"]))

    # Update Blocklist Database
    if module.params['update_gravity']:
        commands.append(("Gravity update", [pihole_cmd, "-g"]))

    # Flush all DNS Logs
    if module.params['flush_log']:
        commands.append(("Log flush", [pihole_cmd, "-f"]))

    # Restart DNS
    if module.params['restart_dns']:
        commands.append(("DNS restart", [pihole_cmd, "restartdns"]))

    # Blacklist Domains
    if module.params['blacklist']:
        commands.append(("Blocking Domain", [pihole_cmd, "blacklist", module.params['blacklist']]))

    # Whitelist domains
    if module.params['whitelist']:
        commands.append(("Whitelisting Domain", [pihole_cmd, "whitelist", module.params['whitelist']]))

    # Enable / disable Pihole
    if module.params['enable_pihole']:
        commands.append(("Pi-Hole enabled", [pihole_cmd, "enable"]))
    elif module.params['enable_pihole'] is False:
        commands.append(("Pi-Hole disabled", [pihole_cmd, "disable"]))

    # Change Web-Admin Password
    if module.params['admin_pwd']:
        commands.append(("Changing Web Admin Password", [pihole_cmd, "-a", "-p", module.params['admin_pwd']]))

    messages = []
    changed = False

    for description, command in commands:
        success, output = execute_command(command)
        if success:
            if any(phrase in output.lower() for phrase in no_update_phrases):
                messages.append(f"{description}: No update was necessary.")
            elif any(phrase in output.lower() for phrase in blacklist_no_update_phrases):
                messages.append(f"{description} ({module.params['blacklist']}): Domain already blocked.")
            elif any(phrase in output.lower() for phrase in whitelist_no_update_phrases):
                messages.append(f"{description} ({module.params['whitelist']}): Domain already allowed.")
            else:
                messages.append(f"{description}: {output.strip()}")
                changed = True  # Mark as changed if any command produces an actionable output
        else:
            module.fail_json(msg=f"{description} failed: {output}")

    final_message = "\n".join(messages)
    module.exit_json(changed=changed, msg=final_message)

if __name__ == '__main__':
    main()
