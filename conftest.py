import pytest

def pytest_addoption(parser):
    parser.addoption('--diag',
        action = 'store_true', default = False,
        help = 'show extra information')

@pytest.fixture
def diag(request):
    return request.config.getoption('--diag')
