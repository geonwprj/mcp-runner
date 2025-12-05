# clients/mac_ssh.py

import paramiko
import logging

class MacSSHClient:
    _working_path: str

    def __init__(self, host: str, user: str, password: str = None, key_filename: str = None, port: int = 22, working_path: str = "/tmp", logger: logging.Logger = logging.getLogger(__name__)) -> None:
        self.logger = logger
        self.host = host
        self.user = user
        self.password = password
        self.key_filename = key_filename
        self.port = port
        self._working_path = working_path
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._connect()

    def _connect(self):
        try:
            if self.key_filename:
                self.client.connect(self.host, username=self.user, key_filename=self.key_filename, port=self.port)
            else:
                self.client.connect(self.host, username=self.user, password=self.password, port=self.port)
        except Exception as e:
            self.logger.error(f"Failed to connect to SSH: {str(e)}")
            raise

    def _ensure_connection(self):
        if self.client.get_transport() is None or not self.client.get_transport().is_active():
            self.logger.info("SSH connection lost. Reconnecting...")
            self._connect()

    def __del__(self) -> None:
        try:
            self.client.close()
        except Exception as e:
            self.logger.warning(f"Failed to close SSH connection: {str(e)}")

    def run_command(self, command: str) -> str:
        try:
            self._ensure_connection()
            stdin, stdout, stderr = self.client.exec_command(command)
            return stdout.read().decode("utf-8")
        except Exception as e:
            self.logger.error(f"Failed to run command '{command}': {str(e)}")
            return ""

    def upload_file(self, file_path: str, remote_path: str) -> bool:
        try:
            self._ensure_connection()
            sftp = self.client.open_sftp()
            sftp.put(file_path, remote_path)
            sftp.close()
            return True
        except Exception as e:
            self.logger.error(f"Failed to upload file '{file_path}' to '{remote_path}': {str(e)}")
            return False

    def download_file(self, remote_path: str, file_path: str = None) -> bool:
        try:
            self._ensure_connection()
            sftp = self.client.open_sftp()
            sftp.get(remote_path, file_path)
            sftp.close()
            return True
        except Exception as e:
            self.logger.error(f"Failed to download file '{remote_path}' to '{file_path}': {str(e)}")
            return False

    def exists_file(self, remote_path: str) -> bool:
        try:
            self._ensure_connection()
            sftp = self.client.open_sftp()
            sftp.stat(remote_path)
            sftp.close()
            return True
        except Exception as e:
            self.logger.error(f"Failed to check if file '{remote_path}' exists: {str(e)}")
            return False

    def delete_file(self, remote_path: str) -> bool:
        try:
            self._ensure_connection()
            sftp = self.client.open_sftp()
            sftp.remove(remote_path)
            sftp.close()
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete file '{remote_path}': {str(e)}")
            return False

    def exists_directory(self, remote_path: str) -> bool:
        try:
            self._ensure_connection()
            sftp = self.client.open_sftp()
            sftp.stat(remote_path)
            sftp.close()
            return True
        except Exception as e:
            self.logger.error(f"Failed to check if directory '{remote_path}' exists: {str(e)}")
            return False

    def delete_directory(self, remote_path: str) -> bool:
        try:
            self._ensure_connection()
            sftp = self.client.open_sftp()
            sftp.remove(remote_path)
            sftp.close()
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete directory '{remote_path}': {str(e)}")
            return False

    def list_files(self, remote_path: str) -> list[str]:
        try:
            self._ensure_connection()
            sftp = self.client.open_sftp()
            files = sftp.listdir(remote_path)
            sftp.close()
            return files
        except Exception as e:
            self.logger.error(f"Failed to list files in directory '{remote_path}': {str(e)}")
            return []

    def list_directories(self, remote_path: str) -> list[str]:
        try:
            self._ensure_connection()
            sftp = self.client.open_sftp()
            directories = sftp.listdir(remote_path)
            sftp.close()
            return directories
        except Exception as e:
            self.logger.error(f"Failed to list directories in directory '{remote_path}': {str(e)}")
            return []

