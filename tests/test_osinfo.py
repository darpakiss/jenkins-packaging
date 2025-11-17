import pytest
from unittest.mock import patch, mock_open, MagicMock
from src.nids_configurator.osinfo import OSInfo


def test_detects_non_linux_system():
    with patch('platform.system', return_value='Windows'), \
            patch('platform.release', return_value='10.0.19041'):
        os_info = OSInfo()
        assert os_info.name == 'Windows'
        assert os_info.version == '10.0.19041'
        assert os_info.family == 'unknown'


def test_detects_macos_system():
    with patch('platform.system', return_value='Darwin'), \
            patch('platform.release', return_value='20.6.0'):
        os_info = OSInfo()
        assert os_info.name == 'Darwin'
        assert os_info.version == '20.6.0'
        assert os_info.family == 'unknown'


def test_detects_ubuntu_from_os_release():
    os_release_content = '''NAME="Ubuntu"
VERSION="20.04.3 LTS (Focal Fossa)"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 20.04.3 LTS"
VERSION_ID="20.04"
'''
    with patch('platform.system', return_value='Linux'), \
            patch('builtins.open', mock_open(read_data=os_release_content)):
        os_info = OSInfo()
        assert os_info.name == 'Ubuntu 20.04.3 LTS'
        assert os_info.version == '20.04'
        assert os_info.family == 'ubuntu'


def test_detects_redhat_from_os_release():
    os_release_content = '''NAME="Red Hat Enterprise Linux"
VERSION="8.4 (Ootpa)"
ID="rhel"
ID_LIKE="fedora"
VERSION_ID="8.4"
PRETTY_NAME="Red Hat Enterprise Linux 8.4 (Ootpa)"
'''
    with patch('platform.system', return_value='Linux'), \
            patch('builtins.open', mock_open(read_data=os_release_content)):
        os_info = OSInfo()
        assert os_info.name == 'Red Hat Enterprise Linux 8.4 (Ootpa)'
        assert os_info.version == '8.4'
        assert os_info.family == 'redhat'


def test_detects_centos_as_redhat_family():
    os_release_content = '''NAME="CentOS Linux"
VERSION="7 (Core)"
ID="centos"
ID_LIKE="rhel fedora"
VERSION_ID="7"
PRETTY_NAME="CentOS Linux 7 (Core)"
'''
    with patch('platform.system', return_value='Linux'), \
            patch('builtins.open', mock_open(read_data=os_release_content)):
        os_info = OSInfo()
        assert os_info.family == 'redhat'


def test_handles_missing_os_release_file():
    with patch('platform.system', return_value='Linux'), \
            patch('platform.release', return_value='5.4.0-74-generic'), \
            patch('builtins.open', side_effect=FileNotFoundError):
        os_info = OSInfo()
        assert os_info.name == 'Linux'
        assert os_info.version == '5.4.0-74-generic'
        assert os_info.family == 'unknown'


def test_handles_os_release_with_comments():
    os_release_content = '''# This is a comment
NAME="Ubuntu"
# Another comment
ID=ubuntu
VERSION_ID="20.04"
PRETTY_NAME="Ubuntu 20.04 LTS"
'''
    with patch('platform.system', return_value='Linux'), \
            patch('builtins.open', mock_open(read_data=os_release_content)):
        os_info = OSInfo()
        assert os_info.name == 'Ubuntu 20.04 LTS'
        assert os_info.version == '20.04'
        assert os_info.family == 'ubuntu'


def test_handles_os_release_with_quoted_values():
    os_release_content = '''NAME="Debian GNU/Linux"
VERSION="11 (bullseye)"
ID="debian"
PRETTY_NAME="Debian GNU/Linux 11 (bullseye)"
VERSION_ID="11"
'''
    with patch('platform.system', return_value='Linux'), \
            patch('builtins.open', mock_open(read_data=os_release_content)):
        os_info = OSInfo()
        assert os_info.name == 'Debian GNU/Linux 11 (bullseye)'
        assert os_info.version == '11'


def test_handles_os_release_without_quotes():
    os_release_content = '''NAME=Arch Linux
PRETTY_NAME=Arch Linux
ID=arch
VERSION_ID=rolling
'''
    with patch('platform.system', return_value='Linux'), \
            patch('builtins.open', mock_open(read_data=os_release_content)):
        os_info = OSInfo()
        assert os_info.name == 'Arch Linux'
        assert os_info.version == 'rolling'


def test_handles_minimal_os_release_file():
    os_release_content = '''ID=unknown
'''
    with patch('platform.system', return_value='Linux'), \
            patch('builtins.open', mock_open(read_data=os_release_content)):
        os_info = OSInfo()
        assert os_info.name == 'Linux'
        assert os_info.version == 'unknown'
        assert os_info.family == 'unknown'


def test_handles_empty_os_release_file():
    with patch('platform.system', return_value='Linux'), \
            patch('builtins.open', mock_open(read_data='')):
        os_info = OSInfo()
        assert os_info.name == 'Linux'
        assert os_info.version == 'unknown'
        assert os_info.family == 'unknown'


def test_handles_malformed_os_release_lines():
    os_release_content = '''NAME="Ubuntu"
INVALID_LINE_WITHOUT_EQUALS
VERSION_ID="20.04"
=INVALID_EMPTY_KEY
'''
    with patch('platform.system', return_value='Linux'), \
            patch('builtins.open', mock_open(read_data=os_release_content)):
        os_info = OSInfo()
        assert os_info.name == 'Linux'
        assert os_info.version == '20.04'


def test_detects_ubuntu_via_id_like():
    os_release_content = '''NAME="Linux Mint"
ID="linuxmint"
ID_LIKE="ubuntu debian"
VERSION_ID="20.2"
PRETTY_NAME="Linux Mint 20.2"
'''
    with patch('platform.system', return_value='Linux'), \
            patch('builtins.open', mock_open(read_data=os_release_content)):
        os_info = OSInfo()
        assert os_info.family == 'ubuntu'


def test_detects_fedora_as_redhat_family():
    os_release_content = '''NAME="Fedora Linux"
ID="fedora"
ID_LIKE="redhat"
VERSION_ID="34"
PRETTY_NAME="Fedora Linux 34"
'''
    with patch('platform.system', return_value='Linux'), \
            patch('builtins.open', mock_open(read_data=os_release_content)):
        os_info = OSInfo()
        assert os_info.family == 'redhat'


