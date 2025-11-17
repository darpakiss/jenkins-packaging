import ipaddress
import os
import sys
from .osinfo import OSInfo

try:
    import yaml  # pip install pyyaml
except ImportError:
    yaml = None


class NIDSConfigurator():
    def __init__(self, config_path="/etc/nids/nids-config.yml", non_interactive=False):
        self.non_interactive = non_interactive
        self.config_path = config_path
        self.os_info = OSInfo()
        self.config = self.default_config()

    # noinspection PyMethodMayBeStatic
    def default_config(self):
        return {
            "general": {
                "nids_name": "MyNIDS",
                "config_version": 1,
                "enabled": True,
            },
            "network": {
                "interfaces": [],
                "ipv4_home_nets": [],
                "ipv4_excluded_nets": [],
                "ipv6_home_nets": [],
                "ipv6_excluded_nets": [],
            },
            "rules": {
                "rule_paths": [],
                "enabled_rule_sets": [],
                "disabled_rule_sets": [],
            },
            "logging": {
                "mode": "file",
                "log_file": "/var/log/nids/alerts.log",
                "syslog_target": "localhost:514",
                "log_level": "INFO",
            },
        }

    def prompt_str(self, prompt, default=None):
        if default is not None:
            value = input(f"{prompt} [{default}]: ").strip()
            if value:
                return value
            return default
        return input(f"{prompt}: ").strip()

    def prompt_yes_no(self, prompt, default=True):
        default_str = "Y/n" if default else "y/N"
        while True:
            value = input(f"{prompt} [{default_str}]: ").strip().lower()
            if not value:
                return default
            if value in ("y", "yes"):
                return True
            if value in ("n", "no"):
                return False
            print("Please respond with 'y' or 'n'.")

    def prompt_choice(self, prompt, choices, default=None):
        choices_str = "/".join(choices)
        suffix = f" ({choices_str})"
        if default:
            suffix += f" [{default}]"
        while True:
            value = input(f"{prompt}{suffix}: ").strip()
            if not value and default:
                return default
            if value in choices:
                return value
            print(f"Invalid choice. Allowed: {choices_str}")

    def prompt_list(self, prompt, allow_empty=True):
        print(f"{prompt}")
        print("  Enter one item per line. Leave empty line to finish.")
        items = []
        while True:
            value = input("> ").strip()
            if not value:
                break
            items.append(value)
        if not items and not allow_empty:
            print("List cannot be empty, please enter at least one value.")
            return self.prompt_list(prompt, allow_empty=False)
        return items

    def validate_cidr_list(self, cidrs, ip_version):
        valid = []
        for cidr in cidrs:
            try:
                if ip_version == 4:
                    ipaddress.IPv4Network(cidr, strict=False)
                else:
                    ipaddress.IPv6Network(cidr, strict=False)
                valid.append(cidr)
            except ValueError:
                print(f"Warning: '{cidr}' is not a valid IPv{ip_version} network; skipping.")
        return valid

    def validate_paths(self, paths):
        valid = []
        for p in paths:
            if os.path.exists(p):
                valid.append(p)
            else:
                print(f"Warning: path '{p}' does not exist on this system (keeping anyway).")
                valid.append(p)
        return valid

    def configure_general(self):
        print("\n=== General settings ===")
        if self.non_interactive:
            return
        general = self.config["general"]
        general["nids_name"] = self.prompt_str("NIDS name", general["nids_name"])
        general["enabled"] = self.prompt_yes_no("Enable NIDS by default?", general["enabled"])

    def configure_network(self):
        print("\n=== Network settings ===")
        if self.non_interactive:
            return
        network = self.config["network"]
        interfaces = self.prompt_list("Network interfaces to monitor (e.g. eth0, ens33)", allow_empty=False)
        network["interfaces"] = interfaces

        ipv4_home = self.prompt_list("IPv4 home networks in CIDR (e.g. 192.168.0.0/24)")
        ipv4_home = self.validate_cidr_list(ipv4_home, ip_version=4)
        network["ipv4_home_nets"] = ipv4_home

        ipv4_excl = self.prompt_list("IPv4 excluded networks in CIDR (optional)")
        ipv4_excl = self.validate_cidr_list(ipv4_excl, ip_version=4)
        network["ipv4_excluded_nets"] = ipv4_excl

        ipv6_home = self.prompt_list("IPv6 home networks in CIDR (e.g. 2001:db8::/64)")
        ipv6_home = self.validate_cidr_list(ipv6_home, ip_version=6)
        network["ipv6_home_nets"] = ipv6_home

        ipv6_excl = self.prompt_list("IPv6 excluded networks in CIDR (optional)")
        ipv6_excl = self.validate_cidr_list(ipv6_excl, ip_version=6)
        network["ipv6_excluded_nets"] = ipv6_excl

    def configure_rules(self):
        print("\n=== Rules settings ===")
        if self.non_interactive:
            return
        rules = self.config["rules"]

        rule_paths = self.prompt_list("Rule directories (absolute paths)", allow_empty=False)
        rule_paths = self.validate_paths(rule_paths)
        rules["rule_paths"] = rule_paths

        enabled_sets = self.prompt_list("Enabled rule sets (logical names, not paths)")
        rules["enabled_rule_sets"] = enabled_sets

        disabled_sets = self.prompt_list("Disabled rule sets (optional)")
        rules["disabled_rule_sets"] = disabled_sets

    def configure_logging(self):
        print("\n=== Logging settings ===")
        if self.non_interactive:
            return
        logging_cfg = self.config["logging"]

        mode = self.prompt_choice(
            "Logging mode",
            choices=["file", "syslog", "both"],
            default=logging_cfg["mode"],
        )
        logging_cfg["mode"] = mode

        if mode in ("file", "both"):
            logging_cfg["log_file"] = self.prompt_str("Alert log file path", logging_cfg["log_file"])

        if mode in ("syslog", "both"):
            logging_cfg["syslog_target"] = self.prompt_str("Syslog target (host:port)", logging_cfg["syslog_target"])

        log_level = self.prompt_choice(
            "Log level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            default=logging_cfg["log_level"],
        )
        logging_cfg["log_level"] = log_level

    def save_config_yaml(self, path):
        if yaml is None:
            print("Error: PyYAML is not installed. Install it with:")
            print("  pip install pyyaml")
            sys.exit(1)
        with open(path, "w", encoding="utf-8") as config_file:
            yaml.safe_dump(self.config, config_file, sort_keys=False)
        print("\nConfiguration saved to:", path)

    def run(self):
        print("============================================")
        print("        NIDS Configuration Application      ")
        print("============================================\n")

        print(
            "Detected OS: {name} (family: {family}, version: {version})".format(
                name=self.os_info.name,
                family=self.os_info.family,
                version=self.os_info.version,
            )
        )

        if os.geteuid() != 0:
            print("\nWARNING: You are not running as root.")
            print("   Saving to system locations like /etc/nids may fail due to permissions.\n")

        self.configure_general()
        self.configure_network()
        self.configure_rules()
        self.configure_logging()

        if self.os_info.family in ("ubuntu", "rhel"):
            save_path = self.config_path
        else:
            save_path = "./nids-config.yml"

        print("\n=== Save configuration ===")
        save_path = self.prompt_str("Path to save configuration", save_path)
        self.save_config_yaml(save_path)

        print("\nDone. This file can now be consumed by your NIDS engine.")
        print("Note: This application does not start or manage the NIDS process itself.")


# def main():
#    configurator = NIDSConfigurator()
#    configurator.run()
