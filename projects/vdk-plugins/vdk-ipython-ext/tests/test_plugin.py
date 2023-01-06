import pytest
from vdk.api.job_input import IJobInput
from IPython.testing.globalipapp import start_ipython
from IPython.core.error import UsageError


@pytest.fixture(scope='session')
def session_ip():
    yield start_ipython()


@pytest.fixture(scope='function')
def ip(session_ip):
    session_ip.run_line_magic(magic_name='load_ext', line='vdk_ipython_ext')
    yield session_ip
    session_ip.run_line_magic(magic_name='reset', line='-f')


def test_load_job_input_with_no_arguments(ip):
    ip.run_line_magic(magic_name='reload_job_input', line='')
    assert ip.user_global_ns['job_input'] is not None
    assert isinstance(ip.user_global_ns['job_input'], IJobInput)


def test_load_job_input_with_valid_argument(ip):
    ip.run_line_magic(magic_name='reload_job_input', line='--name=test')
    assert ip.user_global_ns['job_input'] is not None
    assert isinstance(ip.user_global_ns['job_input'], IJobInput)
    assert ip.user_global_ns['job_input'].get_name() == "test"


def test_load_job_input_with_invalid_argument(ip):
    with pytest.raises(
            UsageError, match=r"unrecognized arguments: --invalid_arg=dummy"
    ):
        ip.run_line_magic(magic_name='reload_job_input', line='--invalid_arg=dummy')