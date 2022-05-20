#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from pathlib import Path

import boto3

from .WorkerTask import WorkerTask

S3_FAILED_LOG_FILE="s3_failed_files.log"

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
        raise err

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
        is_session_crashed = False

        for picture_path in pictures_list:
            if not is_session_crashed:
                logging.debug('Sending picture %s to bucket %s', Path(picture_path).name, self._bucket_name)
                try:
                    send_file(s3, self._bucket_name, picture_path, self._bucket_prefix + Path(picture_path).name)
                except Exception:
                    is_session_crashed = True

            if is_session_crashed:
                with open(S3_FAILED_LOG_FILE, 'a') as fd:
                    fd.write(picture_path)
                    fd.write("\n")
