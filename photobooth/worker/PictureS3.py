#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Photobooth - a flexible photo booth software
# Copyright (C) 2018  Balthasar Reuter <photobooth at re - web dot eu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import logging
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from .WorkerTask import WorkerTask

def send_file(s3_conn, bucket_name, src_path, dst_path):
    """
    Send a file to S3 bucket.
    """
    try:
        # Create object on S3 and write data
        obj = s3_conn.Object(bucket_name, dst_path)
        s3_conn.meta.client.upload_file(src_path, bucket_name, dst_path)
    except Exception as err:
        logging.error("Unable to send picture " + str(src_path) + " to S3 : ", err)

class PictureS3(WorkerTask):

    def __init__(self, config):

        super().__init__()
        self._aws_profile = config.get('S3', 'aws_profile')
        self._bucket_name = config.get('S3', 'bucket_name')
        self._bucket_prefix = config.get('S3', 'prefix')

        s3_endpoint_url = config.get('S3', 'endpoint_url')
        if s3_endpoint_url:
            self._endpoint_url = s3_endpoint_url
        else:
            self._endpoint_url = None


    def do(self, pictures_list):
        s3 = boto3.session.Session(profile_name=self._aws_profile).resource('s3', endpoint_url=self._endpoint_url)

        for picture_path in pictures_list:
            logging.debug('Sending picture %s to bucket %s', Path(picture_path).name, self._bucket_name)
            send_file(s3, self._bucket_name, picture_path, self._bucket_prefix + Path(picture_path).name)
