#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging

from paramiko import SSHClient
from scp import SCPClient

from pathlib import Path, PurePosixPath

from .WorkerTask import WorkerTask


def send_file(server_host, server_port, dest_folder, ssh_user, ssh_password, picture_path):
    """
    Send a file using SCP.

    Args:
      server_host (str): SSH server
      server_port (str): SSH server port
      dest_folder (str): Destination folder
      ssh_user (str): SSH username
      ssh_password (str): SSH password (optional)
    """
    with SSHClient() as ssh:
        ssh.load_system_host_keys()
        try:
            ssh.connect(server_host, server_port, ssh_user, ssh_password)

            with SCPClient(ssh.get_transport()) as scp:
                scp.put(picture_path, remote_path=PurePosixPath(dest_folder,Path(picture_path).name))
        except Exception as err:
            logging.error("Unable to send picture " + str(picture_path) + " using SSH : ", err)

class PictureSSH(WorkerTask):

    def __init__(self, config):

        super().__init__()

        self._server_host = config.get('SSH', 'ssh_server_host')
        self._server_port = config.get('SSH', 'ssh_server_port')
        self._dest_folder = config.get('SSH', 'ssh_server_folder')
        self._ssh_user = config.get('SSH', 'ssh_server_user')
        self._ssh_password = config.get('SSH', 'ssh_server_password')

    def do(self, pictures_list):

        for picture_path in pictures_list:
            logging.debug('Sending picture %s to %s', PurePosixPath(self._dest_folder,Path(picture_path).name), self._server_host)
            send_file(self._server_host, self._server_port, self._dest_folder, self._ssh_user, self._ssh_password, picture_path)

