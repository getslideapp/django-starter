from invoke import task
import json
import yaml
import semver
import dotenv
import os

from fabric.api import run, local
from fabric.tasks import execute

def get_config(config):
    """Import config file as dictionary"""
    if config[-5:] != '.yaml':
        config += '.yaml'

    # Use /server as base path
    dir_path = os.path.dirname(os.path.realpath(__file__))
    server_dir_path = dir_path
    if not os.path.isabs(config):
        config = os.path.join(server_dir_path, config)

    with open(config, 'r') as stream:
        config_dict = yaml.load(stream)

    return config_dict


@task
def compose(ctx, cmd='--help'):
    """
    Local only function: Wrapper for docker-compose
    """
    config_dict = get_config('local')
    image_name = config_dict['IMAGE'].split(':')[0]

    env_vars = ("IMAGE_NAME={image_name} "
                "ENV_FILE={env_file} "
                "CELERY_ID={celery_id}  "
                "COMPOSE_PROJECT_NAME={compose_project_name} "
                "POSTGRES_1_PORT_5432_TCP_PORT={postgres_port} "
                ).format(image_name=image_name,
                         env_file=config_dict['ENV_FILE'],
                         celery_id=config_dict['CELERY_ID'],
                         compose_project_name=config_dict['PROJECT_NAME'],
                         postgres_port=config_dict['POSTGRES_1_PORT_5432_TCP_PORT'])

    path = 'etc/local/docker-compose.yml'

    ctx.run(
        '{env} docker-compose -f {path} {cmd}'.format(env=env_vars, cmd=cmd, path=path))

@task
def manage(ctx, cmd):
    """Wrapper for manage function"""
    config_dict = get_config('local')
    venv_python = config_dict['VENV_PYTHON']

    # Switched to run via fabric as invoke was not displaying stdout correctly
    execute(local,'{python} src/manage.py {cmd}'.format(python=venv_python, cmd=cmd))
