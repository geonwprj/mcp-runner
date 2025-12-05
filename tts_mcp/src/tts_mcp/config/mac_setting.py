# config/mac_setting.py

import os

MAC_HOST = os.getenv("MAC_HOST", "192.168.1.100")
MAC_USER = os.getenv("MAC_USER", "user")
MAC_PASSWORD = os.getenv("MAC_PASSWORD", "password")
MAC_SSH_FILE = os.getenv("MAC_SSH_FILE", "/home/user/.ssh/id_rsa")
MAC_WORKING_PATH = os.getenv("MAC_WORKING_PATH", "/tmp")
MAC_PORT = os.getenv("MAC_PORT", 22)
