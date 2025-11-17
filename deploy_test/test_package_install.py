# tests/test_nids_configurator_package.py

def test_package_is_installed(host):
    pkg = host.package("nids-configurator")
    assert pkg.is_installed


def test_usr_bin_wrapper_exists(host):
    f = host.file("/usr/bin/nids-configurator")
    assert f.exists
    assert f.is_file
    # Typically installed as root and executable
    assert f.user == "root"
    assert f.group == "root"
    # Must be executable by at least owner
    assert f.mode & 0o111 != 0


def test_usr_bin_wrapper_content(host):
    f = host.file("/usr/bin/nids-configurator")
    # Common pattern: bash wrapper calling python module under /opt
    assert f.contains("python")
    assert "/opt/nids-configurator" in f.content_string


def test_etc_default_exists(host):
    f = host.file("/etc/default/nids-configurator")
    assert f.exists
    assert f.is_file
    assert f.user == "root"
    assert f.group == "root"
    # Config files usually 0644
    assert f.mode == 0o644


def test_etc_default_content_sane(host):
    f = host.file("/etc/default/nids-configurator")
    # At least ensure it’s not empty and looks like a config/env file
    assert f.size > 0
    # Optional, if you use NDIS_ env vars
    # assert "NDIS_" in f.content_string


def test_opt_install_dir_exists(host):
    d = host.file("/opt/nids-configurator")
    assert d.exists
    assert d.is_directory
    assert d.user == "root"
    assert d.group == "root"
    # Usually 0755 for app dirs
    assert d.mode == 0o755


def test_opt_main_script_exists(host):
    f = host.file("/opt/nids-configurator/nids-configurator")
    assert f.exists
    assert f.is_file
    assert f.user == "root"
    assert f.group == "root"
    # Python entry script / module should be executable
    assert f.mode & 0o111 != 0
    # Likely a Python script with a shebang
    assert f.contains("#!")
    assert "python" in f.content_string.lower()


def test_cli_help_works(host):
    cmd = host.run("/usr/bin/nids-configurator --help")
    assert cmd.rc == 0
    # Make sure it’s actually our program
    assert "NIDS" in cmd.stdout or "nids" in cmd.stdout.lower()

