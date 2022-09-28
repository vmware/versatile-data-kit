import logging
from vdk.api.job_input import IJobInput

log = logging.getLogger(__name__)

def run(job_input: IJobInput):
    properties = job_input.get_all_properties()
   
    # Insert your github token from https://github.com/settings/tokens
    # Repository path user/repo, for example 'vmware/versatile-data-kit'
    job_input.set_all_properties({
        'token': '',
        'repo_path': ''
    })
