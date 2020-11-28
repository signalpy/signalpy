import json
import os.path
from os.path import join

import pytest

import rocohome as rh
import rocohome.cli as cli
import rocohome.db
import rocohome.db.admin


class MockArgs:
    dry_run = False
    jar_dir = 'dynamodb'


@pytest.fixture(scope='session')
def mock_args():
    cli.args = MockArgs()


@pytest.fixture(scope='session')
def db_instance(mock_args):
    print('Starting instance')
    db_pid = rocohome.db.local.up()
    yield db_pid
    print('Stopping instance')
    rocohome.db.local.down(db_pid)


@pytest.fixture
def db_client(db_instance):
    rocohome.db.admin.reset()
    return rocohome.db.client()


@pytest.fixture(scope='session')
def data_dir():
    return join(os.path.dirname(os.path.realpath(__file__)), 'data')


@pytest.fixture(scope='session')
def observations(building, data_dir):
    with open(join(data_dir, 'observations', 'short.json'), 'r') as stream:
        return [rh.Observation(obs) for obs in json.load(stream)]


@pytest.fixture(scope='session')
def account():
    return rh.Account('rscohn2')


@pytest.fixture(scope='session')
def building(account, data_dir):
    return account.load_building(join(data_dir, 'buildings', 'home.yaml'))


@pytest.fixture
def observation_table(db_client):
    return rocohome.db.admin.create_observation_table(db_client)


@pytest.fixture
def collector(observation_table):
    return rh.Collector(observation_table)


@pytest.fixture
def log_server(observation_table):
    return rh.LogServer(observation_table)
