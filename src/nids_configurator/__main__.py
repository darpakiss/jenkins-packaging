import os
import argparse
from .app import NIDSConfigurator


def env_get(name, default=None):
    value = os.environ.get(name)
    if value is None:
        return default
    return value


def env_get_int(name, default=None):
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def env_get_bool(name, default=None):
    value = os.environ.get(name)
    if value is None:
        return default
    v = value.strip().lower()
    if v in ("1", "true", "yes", "y", "on"):
        return True
    if v in ("0", "false", "no", "n", "off"):
        return False
    return default


def env_get_list(name, default=None):
    value = os.environ.get(name)
    if value is None:
        return default
    parts = [item.strip() for item in value.split(",")]
    return [p for p in parts if p]


def build_parser(configurator):
    cfg = configurator.config
    general = cfg["general"]
    network = cfg["network"]
    rules = cfg["rules"]
    logging_cfg = cfg["logging"]

    parser = argparse.ArgumentParser(
        prog="ndis-configurator",
        description="NIDS Configuration Application"
    )

    # ----- general -----
    nids_name_default = env_get("NDIS_NIDS_NAME", general["nids_name"])
    parser.add_argument(
        "--nids-name",
        default=nids_name_default,
        help="Name of the NIDS instance (env: NDIS_NIDS_NAME)"
    )

    config_version_default = env_get_int("NDIS_CONFIG_VERSION", general["config_version"])
    parser.add_argument(
        "--config-version",
        type=int,
        default=config_version_default,
        help="Configuration version number (env: NDIS_CONFIG_VERSION)"
    )

    enabled_default = env_get_bool("NDIS_ENABLED", general["enabled"])
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--enable",
        dest="enabled",
        action="store_true",
        help="Enable NIDS by default (env: NDIS_ENABLED)"
    )
    group.add_argument(
        "--disable",
        dest="enabled",
        action="store_false",
        help="Disable NIDS by default (env: NDIS_ENABLED)"
    )
    parser.set_defaults(enabled=enabled_default)

    # ----- network (lists use append; env vars use comma-separated lists) -----
    iface_default = env_get_list("NDIS_INTERFACES", None)
    parser.add_argument(
        "--iface",
        dest="interfaces",
        action="append",
        default=iface_default,
        help="Network interface to monitor, can be used multiple times (env: NDIS_INTERFACES, comma-separated)"
    )

    ipv4_home_default = env_get_list("NDIS_IPV4_HOME_NETS", None)
    parser.add_argument(
        "--ipv4-home",
        dest="ipv4_home_nets",
        action="append",
        default=ipv4_home_default,
        help="IPv4 home network in CIDR, can be used multiple times (env: NDIS_IPV4_HOME_NETS, comma-separated)"
    )

    ipv4_excl_default = env_get_list("NDIS_IPV4_EXCLUDED_NETS", None)
    parser.add_argument(
        "--ipv4-excl",
        dest="ipv4_excluded_nets",
        action="append",
        default=ipv4_excl_default,
        help="IPv4 excluded network in CIDR, can be used multiple times "
             "(env: NDIS_IPV4_EXCLUDED_NETS, comma-separated)"
    )

    ipv6_home_default = env_get_list("NDIS_IPV6_HOME_NETS", None)
    parser.add_argument(
        "--ipv6-home",
        dest="ipv6_home_nets",
        action="append",
        default=ipv6_home_default,
        help="IPv6 home network in CIDR, can be used multiple times (env: NDIS_IPV6_HOME_NETS, comma-separated)"
    )

    ipv6_excl_default = env_get_list("NDIS_IPV6_EXCLUDED_NETS", None)
    parser.add_argument(
        "--ipv6-excl",
        dest="ipv6_excluded_nets",
        action="append",
        default=ipv6_excl_default,
        help="IPv6 excluded network in CIDR, can be used multiple times "
             "(env: NDIS_IPV6_EXCLUDED_NETS, comma-separated)"
    )

    # ----- rules -----
    rule_paths_default = env_get_list("NDIS_RULE_PATHS", None)
    parser.add_argument(
        "--rule-path",
        dest="rule_paths",
        action="append",
        default=rule_paths_default,
        help="Rule directory path, can be used multiple times (env: NDIS_RULE_PATHS, comma-separated)"
    )

    enabled_sets_default = env_get_list("NDIS_ENABLED_RULE_SETS", None)
    parser.add_argument(
        "--enable-rule-set",
        dest="enabled_rule_sets",
        action="append",
        default=enabled_sets_default,
        help="Logical rule set name to enable, can be used multiple times "
             "(env: NDIS_ENABLED_RULE_SETS, comma-separated)"
    )

    disabled_sets_default = env_get_list("NDIS_DISABLED_RULE_SETS", None)
    parser.add_argument(
        "--disable-rule-set",
        dest="disabled_rule_sets",
        action="append",
        default=disabled_sets_default,
        help="Logical rule set name to disable, can be used multiple times "
             "(env: NDIS_DISABLED_RULE_SETS, comma-separated)"
    )

    # ----- logging -----
    log_mode_default = env_get("NDIS_LOG_MODE", logging_cfg["mode"])
    parser.add_argument(
        "--log-mode",
        choices=["file", "syslog", "both"],
        default=log_mode_default,
        help="Logging mode: file, syslog or both (env: NDIS_LOG_MODE)"
    )

    log_file_default = env_get("NDIS_LOG_FILE", logging_cfg["log_file"])
    parser.add_argument(
        "--log-file",
        default=log_file_default,
        help="Path to alert log file (env: NDIS_LOG_FILE)"
    )

    syslog_target_default = env_get("NDIS_SYSLOG_TARGET", logging_cfg["syslog_target"])
    parser.add_argument(
        "--syslog-target",
        default=syslog_target_default,
        help="Syslog target as host:port (env: NDIS_SYSLOG_TARGET)"
    )

    log_level_default = env_get("NDIS_LOG_LEVEL", logging_cfg["log_level"])
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=log_level_default,
        help="Logging level (env: NDIS_LOG_LEVEL)"
    )

    return parser


def apply_args_to_config(configurator, args):
    cfg = configurator.config
    general = cfg["general"]
    network = cfg["network"]
    rules = cfg["rules"]
    logging_cfg = cfg["logging"]

    # general
    general["nids_name"] = args.nids_name
    general["config_version"] = args.config_version
    general["enabled"] = args.enabled

    # network (only override if CLI/env provided something)
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

    # Use CLI/env values to override defaults before running the wizard.
    # The interactive prompts will now show these values as defaults.
    apply_args_to_config(configurator, args)

    configurator.run()


if __name__ == "__main__":
    main()
