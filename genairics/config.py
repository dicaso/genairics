#!/usr/bin/env python
"""genairics configuration 

Integrated with luigi config.
"""
import luigi, os
from multiprocessing import cpu_count

class genairics(luigi.Config):
    general_log = luigi.Parameter(default=os.path.expanduser('~/.genairics.log'))
    datadir = luigi.Parameter(
        default = os.environ.get('GAX_DATADIR',os.path.expanduser('~/data')),
        description = 'default directory that contains data in project subfolders'
    )
    resultsdir = luigi.Parameter(
        default = os.environ.get('GAX_RESULTSDIR',os.path.expanduser('~/results')),
        description = 'default directory that contains results in project subfolders'
    )
    resourcedir = luigi.Parameter(
        default = os.environ.get('GAX_RESOURCES',os.path.expanduser('~/resources')),
        description = 'default directory where resources such as genomes are stored'
    )
    basespaceAPIfile = luigi.Parameter(
        default = os.path.expanduser('~/.BASESPACE_API'),
        description = 'file containing BaseSpace API token'
    )
    nodes = luigi.IntParameter(
        default = os.environ.get('PBS_NUM_NODES',1),
        description = 'nodes to use to execute pipeline'
    )
    threads = luigi.IntParameter(
        default = cpu_count(),
        description = 'processors per node to request'
    )
    ui = luigi.ChoiceParameter(
        default = 'wui',
        choices = ['wui','gui','cli'],
        description = 'user interface mode'
    )
    browser = luigi.Parameter(
        default = 'firefox',
        description = 'browser to use for wui'
    )

config = genairics()

def saveConfig(configs):
    """
    saves every config in list configs to LUIGI_CONFIG_PATH destination,
    or - if not provided - in 'luigi.cfg' in current working directory
    """
    if type(configs) != list: configs = [configs]
    with open(os.environ.get('LUIGI_CONFIG_PATH','luigi.cfg'),'wt') as outconfig:
        for config in configs:
            outconfig.write('[{}]\n'.format(config.get_task_family()))
            for param in config.get_param_names():
                outconfig.write('{}={}\n'.format(param,config.__getattribute__(param)))
