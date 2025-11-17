import pytest
from unittest.mock import patch, mock_open
import tempfile
import os
from src.nids_configurator.app import NIDSConfigurator


class TestNIDSConfigurator:

    @pytest.fixture
    def configurator(self):
        return NIDSConfigurator()

    def test_default_config_returns_all_required_sections(self, configurator):
        config = configurator.default_config()
        assert "general" in config
        assert "network" in config
        assert "rules" in config
        assert "logging" in config

    def test_default_config_has_nids_enabled_by_default(self, configurator):
        config = configurator.default_config()
        assert config["general"]["enabled"] is True

    @patch('builtins.input', return_value='test_value')
    def test_prompt_str_returns_user_input_when_provided(self, mock_input, configurator):
        result = configurator.prompt_str("Enter value")
        assert result == "test_value"

    @patch('builtins.input', return_value='')
    def test_prompt_str_returns_default_when_empty_input(self, mock_input, configurator):
        result = configurator.prompt_str("Enter value", default="default_val")
        assert result == "default_val"

    @patch('builtins.input', return_value='y')
    def test_prompt_yes_no_returns_true_for_yes(self, mock_input, configurator):
        result = configurator.prompt_yes_no("Confirm?")
        assert result is True

    @patch('builtins.input', return_value='n')
    def test_prompt_yes_no_returns_false_for_no(self, mock_input, configurator):
        result = configurator.prompt_yes_no("Confirm?")
        assert result is False

    @patch('builtins.input', return_value='')
    def test_prompt_yes_no_returns_default_when_empty(self, mock_input, configurator):
        result = configurator.prompt_yes_no("Confirm?", default=False)
        assert result is False

    @patch('builtins.input', side_effect=['invalid', 'y'])
    def test_prompt_yes_no_reprompts_on_invalid_input(self, mock_input, configurator):
        result = configurator.prompt_yes_no("Confirm?")
        assert result is True
        assert mock_input.call_count == 2

    @patch('builtins.input', return_value='option1')
    def test_prompt_choice_returns_valid_choice(self, mock_input, configurator):
        result = configurator.prompt_choice("Choose", ["option1", "option2"])
        assert result == "option1"

    @patch('builtins.input', return_value='')
    def test_prompt_choice_returns_default_when_empty(self, mock_input, configurator):
        result = configurator.prompt_choice("Choose", ["opt1", "opt2"], default="opt1")
        assert result == "opt1"

    @patch('builtins.input', side_effect=['invalid', 'opt1'])
    def test_prompt_choice_reprompts_on_invalid_choice(self, mock_input, configurator):
        result = configurator.prompt_choice("Choose", ["opt1", "opt2"])
        assert result == "opt1"
        assert mock_input.call_count == 2

    @patch('builtins.input', side_effect=['item1', 'item2', ''])
    def test_prompt_list_returns_list_of_items(self, mock_input, configurator):
        result = configurator.prompt_list("Enter items")
        assert result == ["item1", "item2"]

    @patch('builtins.input', side_effect=[''])
    def test_prompt_list_returns_empty_list_when_allow_empty(self, mock_input, configurator):
        result = configurator.prompt_list("Enter items", allow_empty=True)
        assert result == []

    @patch('builtins.input', side_effect=['', 'item1', ''])
    def test_prompt_list_reprompts_when_empty_not_allowed(self, mock_input, configurator):
        result = configurator.prompt_list("Enter items", allow_empty=False)
        assert result == ["item1"]

    def test_validate_cidr_list_accepts_valid_ipv4_networks(self, configurator):
        cidrs = ["192.168.1.0/24", "10.0.0.0/8"]
        result = configurator.validate_cidr_list(cidrs, ip_version=4)
        assert result == cidrs

    def test_validate_cidr_list_accepts_valid_ipv6_networks(self, configurator):
        cidrs = ["2001:db8::/32", "fe80::/10"]
        result = configurator.validate_cidr_list(cidrs, ip_version=6)
        assert result == cidrs

    def test_validate_cidr_list_filters_invalid_ipv4_networks(self, configurator):
        cidrs = ["192.168.1.0/24", "invalid", "10.0.0.0/8"]
        result = configurator.validate_cidr_list(cidrs, ip_version=4)
        assert result == ["192.168.1.0/24", "10.0.0.0/8"]

    def test_validate_cidr_list_filters_invalid_ipv6_networks(self, configurator):
        cidrs = ["2001:db8::/32", "not_valid", "fe80::/10"]
        result = configurator.validate_cidr_list(cidrs, ip_version=6)
        assert result == ["2001:db8::/32", "fe80::/10"]

    def test_validate_cidr_list_handles_empty_list(self, configurator):
        result = configurator.validate_cidr_list([], ip_version=4)
        assert result == []

    def test_validate_paths_keeps_all_paths(self, configurator):
        with tempfile.TemporaryDirectory() as tmpdir:
            existing = os.path.join(tmpdir, "exists")
            os.makedirs(existing)
            non_existing = "/path/that/does/not/exist"

            result = configurator.validate_paths([existing, non_existing])
            assert result == [existing, non_existing]

    @patch('builtins.input', side_effect=['TestNIDS', 'y'])
    def test_configure_general_updates_general_config(self, mock_input, configurator):
        configurator.configure_general()
        assert configurator.config["general"]["nids_name"] == "TestNIDS"
        assert configurator.config["general"]["enabled"] is True

    @patch('builtins.input', side_effect=['eth0', '', '192.168.1.0/24', '', '', '', '', ''])
    def test_configure_network_updates_network_config(self, mock_input, configurator):
        configurator.configure_network()
        assert configurator.config["network"]["interfaces"] == ["eth0"]
        assert configurator.config["network"]["ipv4_home_nets"] == ["192.168.1.0/24"]

    @patch('builtins.input', side_effect=['/etc/rules', '', 'ruleset1', '', '', ''])
    def test_configure_rules_updates_rules_config(self, mock_input, configurator):
        configurator.configure_rules()
        assert configurator.config["rules"]["rule_paths"] == ['/etc/rules']
        assert configurator.config["rules"]["enabled_rule_sets"] == ['ruleset1']

    @patch('builtins.input', side_effect=['file', '/var/log/test.log', 'DEBUG'])
    def test_configure_logging_updates_logging_config_for_file_mode(self, mock_input, configurator):
        configurator.configure_logging()
        assert configurator.config["logging"]["mode"] == "file"
        assert configurator.config["logging"]["log_file"] == "/var/log/test.log"
        assert configurator.config["logging"]["log_level"] == "DEBUG"

    @patch('builtins.input', side_effect=['syslog', 'remote:514', 'WARNING'])
    def test_configure_logging_updates_logging_config_for_syslog_mode(self, mock_input, configurator):
        configurator.configure_logging()
        assert configurator.config["logging"]["mode"] == "syslog"
        assert configurator.config["logging"]["syslog_target"] == "remote:514"

    @patch('builtins.input', side_effect=['both', '/var/log/test.log', 'remote:514', 'INFO'])
    def test_configure_logging_updates_logging_config_for_both_mode(self, mock_input, configurator):
        configurator.configure_logging()
        assert configurator.config["logging"]["mode"] == "both"
        assert configurator.config["logging"]["log_file"] == "/var/log/test.log"
        assert configurator.config["logging"]["syslog_target"] == "remote:514"

    @patch('yaml.safe_dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_config_yaml_writes_config_to_file(self, mock_file, mock_yaml_dump, configurator):
        configurator.save_config_yaml("/tmp/test.yml")
        mock_file.assert_called_once_with("/tmp/test.yml", "w", encoding="utf-8")
        mock_yaml_dump.assert_called_once()

    @patch('src.nids_configurator.app.yaml', None)
    def test_save_config_yaml_exits_when_yaml_not_installed(self, configurator):
        with pytest.raises(SystemExit):
            configurator.save_config_yaml("/tmp/test.yml")
