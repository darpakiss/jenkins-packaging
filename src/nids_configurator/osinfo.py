import os
import platform

class OSInfo:
    def __init__(self):
        self.name = None
        self.version = None
        self.family = None
        self.detect()

    def detect(self):
        sys_name = platform.system()
        if sys_name != "Linux":
            self.name = sys_name
            self.version = platform.release()
            self.family = "unknown"
            return

        os_release = {}
        try:
            with open("/etc/os-release") as release_file:
                for line in release_file:
                    if line.startswith("#"):
                        continue
                    if "=" in line:
                        env_key, v = line.strip().split("=", 1)
                        os_release[env_key] = v.strip('"')
        except FileNotFoundError:
            self.name = "Linux"
            self.version = platform.release()
            self.family = "unknown"
            return

        pretty_name = os_release.get("PRETTY_NAME", "Linux")
        version_id = os_release.get("VERSION_ID", "unknown")
        id_like = os_release.get("ID_LIKE", "")
        os_id = os_release.get("ID", "")

        family = "unknown"
        if "ubuntu" in os_id or "ubuntu" in id_like:
            family = "ubuntu"
        elif "rhel" in os_id or "rhel" in id_like or "redhat" in id_like:
            family = "redhat"

        self.name = pretty_name
        self.version = version_id
        self.family = family
