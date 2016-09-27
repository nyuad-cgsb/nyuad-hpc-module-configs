# gencore_app.utils.main_build_env

import logging
import sys
from gencore_app.utils.main import run_command
from gencore_app.utils.main_env import from_file

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def try_conda_env_create(fname):

    #Clean up any extra tags
    env = from_file(fname)
    env.save()

    retries_max = 2
    retries_count = 0
    create_env = False

    while retries_count <= retries_max:
        retries_count = retries_count + 1
        ec = run_conda_env_create(fname)
        if ec:
            logging.info('Conda Env for {} created successfully'.format(fname) )
            create_env = True
            break
        else:
            logging.warn('Conda Env was NOT created successfully! Retrying {}'.format(retries_count))

    #Add back in extra_args
    env.save_extra_args()

    return create_env

def run_conda_env_create(fname):

    logger.info("Testing environment build file {}".format(fname))
    cmd = "conda env create --force --file {}".format(fname)
    return run_command(cmd)

def status_check_build(build_passes):

    if not build_passes:
        logging.warn("One or more builds did not pass!")
        sys.exit(1)
    else:
        logging.info("Build passed!")
