# from .app import main
import argparse
from .app import NIDSConfigurator


def build_parser(configurator):
    cfg = configurator.config
    general = cfg["general"]
    logging_cfg = cfg["logging"]

    parser = argparse.ArgumentParser(prog="ndis-configurator", description="NIDS Configuration Application")

    # ----- general -----
    parser.add_argument("-o", "--output", help="Path to save configuration file")
    parser.add_argument("--non-interactive", action="store_true",
                        help="Run in non-interactive mode (future extension)")
    parser.add_argument("--nids-name", default=general["nids_name"], help="Name of the NIDS instance")

    parser.add_argument("--config-version", type=int, default=general["config_version"],
                        help="Configuration version number")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--enable", dest="enabled", action="store_true", help="Enable NIDS by default")
    group.add_argument("--disable", dest="enabled", action="store_false", help="Disable NIDS by default")
    parser.set_defaults(enabled=general["enabled"])

    # ----- network (lists use append so they can be repeated) -----
    parser.add_argument("--iface", dest="interfaces", action="append", default=None,
                        help="Network interface to monitor (can be used multiple times)")

    parser.add_argument("--ipv4-home", dest="ipv4_home_nets", action="append", default=None,
                        help="IPv4 home network in CIDR (can be used multiple times)")

    parser.add_argument("--ipv4-excl", dest="ipv4_excluded_nets", action="append", default=None,
                        help="IPv4 excluded network in CIDR (can be used multiple times)")

    parser.add_argument("--ipv6-home", dest="ipv6_home_nets", action="append", default=None,
                        help="IPv6 home network in CIDR (can be used multiple times)")

    parser.add_argument("--ipv6-excl", dest="ipv6_excluded_nets", action="append", default=None,
                        help="IPv6 excluded network in CIDR (can be used multiple times)")

    # ----- rules -----
    parser.add_argument("--rule-path", dest="rule_paths", action="append", default=None,
                        help="Rule directory path (can be used multiple times)")

    parser.add_argument("--enable-rule-set", dest="enabled_rule_sets", action="append", default=None,
                        help="Logical rule set name to enable (can be used multiple times)")

    parser.add_argument("--disable-rule-set", dest="disabled_rule_sets", action="append", default=None,
                        help="Logical rule set name to disable (can be used multiple times)")

    # ----- logging -----
    parser.add_argument("--log-mode", choices=["file", "syslog", "both"], default=logging_cfg["mode"],
                        help="Logging mode: file, syslog or both")

    parser.add_argument("--log-file", default=logging_cfg["log_file"],
                        help="Path to alert log file (when using file or both)")

    parser.add_argument("--syslog-target", default=logging_cfg["syslog_target"],
                        help="Syslog target as host:port (when using syslog or both)")

    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        default=logging_cfg["log_level"], help="Logging level")

    return parser


def apply_args_to_config(configurator, args):
    cfg = configurator.config
    general = cfg["general"]
    network = cfg["network"]
    rules = cfg["rules"]
    logging_cfg = cfg["logging"]

    # general
    if args.output is not None:
        configurator.output_path = args.output
    if args.non_interactive:
        configurator.non_interactive = True
    general["nids_name"] = args.nids_name
    general["config_version"] = args.config_version
    general["enabled"] = args.enabled

    # network (only override if CLI provided something)
    if args.interfaces is not None:
        network["interfaces"] = args.interfaces

    if args.ipv4_home_nets is not None:
        network["ipv4_home_nets"] = args.ipv4_home_nets

    if args.ipv4_excluded_nets is not None:
        network["ipv4_excluded_nets"] = args.ipv4_excluded_nets

    if args.ipv6_home_nets is not None:
        network["ipv6_home_nets"] = args.ipv6_home_nets

    if args.ipv6_excluded_nets is not None:
        network["ipv6_excluded_nets"] = args.ipv6_excluded_nets

    # rules
    if args.rule_paths is not None:
        rules["rule_paths"] = args.rule_paths

    if args.enabled_rule_sets is not None:
        rules["enabled_rule_sets"] = args.enabled_rule_sets

    if args.disabled_rule_sets is not None:
        rules["disabled_rule_sets"] = args.disabled_rule_sets

    # logging
    logging_cfg["mode"] = args.log_mode
    logging_cfg["log_file"] = args.log_file
    logging_cfg["syslog_target"] = args.syslog_target
    logging_cfg["log_level"] = args.log_level


def main():
    configurator = NIDSConfigurator()
    parser = build_parser(configurator)
    args = parser.parse_args()


    # Use CLI values to override defaults before running the wizard.
    # The interactive prompts will now show these values as defaults.
    apply_args_to_config(configurator, args)

    configurator.run()


if __name__ == "__main__":
    main()
