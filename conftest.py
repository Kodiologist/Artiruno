import pytest

def pytest_addoption(parser):
    parser.addoption('--slow',
        action = 'store_true', default = False,
        help = 'run slow tests')

def pytest_configure(config):
    config.addinivalue_line('markers', 'slow: mark test as slow to run')

def pytest_collection_modifyitems(config, items):
    # Skip slow tests unless `--slow` is provided.
    if config.getoption('--slow'):
       return
    for item in items:
        if 'slow' in item.keywords:
            item.add_marker(pytest.mark.skip(reason =
                '--slow not provided'))

@pytest.fixture
def run_slow_tests(request):
    return request.config.getoption('--slow')
