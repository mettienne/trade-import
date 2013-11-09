from fabric.api import local, env, sudo, run
from fabric.context_managers import cd, prefix
from fabric.colors import yellow as _yellow
import os.path
import inspect

def test():
    print(_yellow('>>> starting {}'.format(_fn())))
    local('py.test -sx --cov-report term-missing --cov .')


def prod():

    env.user = 'nelly'
    env.app_name = 'trade-tools'
    env.apps_path = '/apps'
    env.git_clone = 'https://github.com/mettienne/trade-import.git'
    env.hosts = ['90.185.144.43']
    env.app_path = os.path.join(env.apps_path, env.app_name)
    env.venv_path = os.path.join(env.app_path, '_venv')

def setup():
    mkdirs()
    pull()
    setup_virtualenv()

def deploy():
    pull()
    #clone()
    install_requirements()
    start()


def clone():
    print(_yellow('>>> starting {}'.format(_fn())))
    with cd(env.app_path):
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
    run('mkdir -p {}'.format(env.app_path))

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

def start():
    """
    Start the script using pm2
    """
    print(_yellow('>>> starting {}'.format(_fn())))
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
