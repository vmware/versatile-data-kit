# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import shutil

from vdk.internal.control.exception.vdk_exception import VDKException


log = logging.getLogger(__name__)


class JobArchive:
    ZIP_ARCHIVE_TYPE = "zip"

    def archive_data_job(self, job_name, job_archive_path):
        try:
            log.debug(f"Archive data job {job_name} into path {job_archive_path}")
            job_folder_base = os.path.dirname(job_archive_path)
            job_content_folder = os.path.basename(job_archive_path)
            return shutil.make_archive(
                base_name=job_archive_path,
                format=self.ZIP_ARCHIVE_TYPE,
                root_dir=job_folder_base,
                base_dir=job_content_folder,
            )
        except Exception as e:
            raise VDKException(
                what=f"Cannot archive data job {job_name} as part of deployment.",
                why=f"VDK CLI did not create data job archive: {e}.",
                consequence="Cannot deploy the Data Job.",
                countermeasure="Make sure VDK CLI has proper permissions and the job exists in the folder",
            ) from e

    def unarchive_data_job(self, job_name, job_archive_path, job_directory):
        log.debug(
            f"Un-archive data job {job_name} from path {job_archive_path} into directory {job_directory}"
        )
        try:
            shutil.unpack_archive(
                job_archive_path, job_directory, format=self.ZIP_ARCHIVE_TYPE
            )
        except Exception as e:
            raise VDKException(
                what=f"Cannot un-archive data job {job_name} .",
                why=f"There was a problem with the archive: {e}.",
                consequence="Cannot download the Data Job.",
                countermeasure="Make sure VDK CLI has proper permissions and the job exists in the folder",
            ) from e
