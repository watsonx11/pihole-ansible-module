#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
import subprocess

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
