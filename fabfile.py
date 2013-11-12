from fabric.api import local, env, sudo, run
from fabric.context_managers import cd, prefix
from fabric.colors import yellow as _yellow
import os.path
import inspect
import config

env.app_name = 'trade-tools'
env.apps_path = '/apps'
env.git_clone = 'https://github.com/mettienne/trade-import.git'
env.app_path = os.path.join(env.apps_path, env.app_name)
env.log_path = os.path.join(env.apps_path, 'log')
env.venv_path = os.path.join(env.app_path, '_venv')

def test():
    print(_yellow('>>> starting {}'.format(_fn())))
    local('py.test -sx --cov-report term-missing --cov .')

def itest():
    print(_yellow('>>> starting {}'.format(_fn())))
    local('py.test -sx --cov-report term-missing --cov . test/itest*.py')

def local():
    env.user = 'mikko'
    env.hosts = ['localhost']
    env.app_path = os.path.join(env.apps_path, env.app_name)
    env.venv_path = os.path.join(env.app_path, '_venv')

def clean():
    print(_yellow('>>> starting {}'.format(_fn())))
    with cd(env.apps_path):
        run('rm -rf {}'.format(env.app_name))

def prod():

    env.user = 'nelly'
    env.hosts = ['90.185.144.43']

def setup():
    mkdirs()
    clone()
    setup_virtualenv()

def deploy():
    pull()
    install_requirements()
    start()


def clone():
    print(_yellow('>>> starting {}'.format(_fn())))
    with cd(env.apps_path):
        run('git clone -q --depth 1 {} {}'.format(env.git_clone, env.app_name))

def pull():
    print(_yellow('>>> starting {}'.format(_fn())))
    with cd(env.app_path):
        run('git checkout . ')
        run('git pull origin master')

def clean():
    print(_yellow('>>> starting {}'.format(_fn())))
    run('rm -rf {}'.format(env.app_path))

def mkdirs():
    print(_yellow('>>> starting {}'.format(_fn())))
    run('sudo mkdir -p {}'.format(env.apps_path))
    run('sudo chown {} {}'.format(env.user, env.apps_path))
    run('sudo mkdir -p {}'.format(env.log_path))
    #run('mkdir -p {}'.format(os.path.join(env.app_path, config.log_dir)))

def setup_virtualenv():
    """
    Setup a fresh virtualenv.
    """
    print(_yellow('>>> starting {}'.format(_fn())))
    run('virtualenv --no-site-packages {}'.format(env.venv_path))
    virtualenv('easy_install -U setuptools')
    virtualenv('easy_install pip')

def virtualenv(command):
    """
    Run command in virtualenv.
    """
    print(_yellow('>>> starting {}'.format(_fn())))
    with prefix('source {}/bin/activate'.format(env.venv_path)):
        run(command)

def status():
    print(_yellow('>>> starting {}'.format(_fn())))
    with cd(env.app_path):
        run('pm2 list'.format(env.venv_path))

def log():
    with cd(env.app_path):
        run('tail -fn30 log/*')

def start():
    print(_yellow('>>> starting {}'.format(_fn())))
    with cd(env.app_path):
        run('pm2 stop import.py')
        run('pm2 start import.py -x --interpreter {}/bin/python'.format(env.venv_path))

def install_requirements():
    """
    Install the required packages using pip.
    """
    print(_yellow('>>> starting {}'.format(_fn())))
    virtualenv('pip install -q --upgrade -r {}/requirements.txt'.format(env.app_path))

def _fn():
    """
    Returns current function name
    """
    return inspect.stack()[1][3]
