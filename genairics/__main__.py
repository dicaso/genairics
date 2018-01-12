#!/ur/bin/env python
# PYTHON_ARGCOMPLETE_OK
import os, sys

def prepareParser():
    """
    Prepares the argument parser, joblaunchers and pipelines for genairics
    hooks up the different pipelines that are made available through the CLI
    returns (parser, joblaunchers, pipelines)
    """
    import argparse
    from collections import OrderedDict
    from genairics import typeMapping
    from genairics.jobs import QueuJob
    from genairics.RNAseq import RNAseq
    from genairics.ATACseq import ATACseq

    pipelines = OrderedDict((
        ('RNAseq',RNAseq),
        ('ATACseq',ATACseq)
    ))

    joblaunchers = OrderedDict((
        ('native', None),
        ('qsub', QueuJob)
    ))
    
    parser = argparse.ArgumentParser(
        prog = 'genairics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=r'''
      _______
      -------
         |||
      /+++++++:         __-_-_-_-_
  /#-'genairics'-,_     /;@;@,@'@+`
 /##@+;+++++++:@.+#\\/`,@@;@;@;@`@'\
 :#@:'###    #+';.#'\\@@'#####++;:@+
 |#@`:,:      #+#:+#+\\+#     #+@@++|
 ;@'.##         '+.:#_\\       #+@,`:
 :#@;.#         |+;,| ||        ##@`.|
 |@'..#         \\###-;|         #@:.:
 |#@;:#        '+\\::/\:         +#@::
 :@;,:+       #@@'\\/ ,\        #';@.|
 \#@'#'#     #'@',##;:@`        ##@,;;
  :##@:@:@;@;@;@.;/  \#+@;#` #'#+@`:;
  `\#.@;@;@;@:@.+/    :'@;@;@;@;@,:;
     \,,'::,,#::;      \'@:@'@;@'+'/

    GENeric AIRtight omICS pipeline.

    When the program is finished running, you can check the log file with "less -r plumbing/pipeline.log"
    from your project's result directory. Errors will also be printed to stdout.
    ''')

    parser.add_argument('--job-launcher', default = 'native', type = str, choices = joblaunchers.keys(),
                        help='choose where and how the job will run')
    parser.add_argument('--remote-host', default = '', type = str, help = 'submit job through ssh')
    parser.add_argument('--save-config', action = 'store_true',
                        help = 'save path related default values to a configuration file in the directory where you started genairics')
    parser.add_argument('--verbose', action = 'store_true', help = 'verbose output')

    # Pipeline subparsers
    subparsers = parser.add_subparsers(help='sub-command help')
    for pipeline in pipelines:
        subparser = subparsers.add_parser(
            pipeline,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            help='genairics {} -h'.format(pipeline)
        )
        subparser.set_defaults(function=pipelines[pipeline])
        for paran,param in pipelines[pipeline].get_params():
            if type(param._default) in typeMapping.values():
                subparser.add_argument('--'+paran, default=param._default, type=typeMapping[type(param)],
                                       help=param.description)
            else: subparser.add_argument(paran, type=typeMapping[type(param)], help=param.description)

    # Console option
    def startConsole():
        import IPython
        import genairics, genairics.datasources, genairics.resources
        from genairics.resources import InstallDependencies
        IPython.embed()
        exit()
        
    subparser = subparsers.add_parser(
        'console',
        help='Start console where tasks can be started not available in the commandline interface'
    )
    subparser.set_defaults(function=startConsole)

    return parser, joblaunchers, pipelines

def main(args=None):
    """
    Checks where arguments are provided (directly to main function, environment, CLI),
    parses them and starts the workflow.
    """
    import argcomplete, os, logging
    from genairics import config, typeMapping, logger, runWorkflow

    parser, joblaunchers, pipelines = prepareParser()
    
    if args is None:
        # if arguments are set in environment, they are used as the argument default values
        # but only when no other arguments are passed on the command line
        # this allows seemless integration with PBS jobs
        if len(sys.argv) == 1 and 'GENAIRICS_ENV_ARGS' in os.environ:
            #Retrieve arguments from qsub job environment
            args = [os.environ['GENAIRICS_ENV_ARGS']]
            positionals = []
            optionals = []
            for paran,param in pipelines[args[0]].get_params():
                if paran in os.environ:
                    if type(param._default) in typeMapping.values():
                        optionals += ['--'+paran, os.environ[paran]]
                    else: positionals.append(os.environ[paran])
            logger.warning(
                'Pipeline %s arguments were retrieved from environment: positional %s, optional %s',
                args[0], positionals, optionals
            )
            args+= optionals + positionals
            args = parser.parse_args(args)
        #wui
        elif len(sys.argv) == 1 and config.ui == 'wui':
            from genairics.utils import jobserver
            jobserver(parser)
            return "jobserver threads fully operational" #has to return to avoid executing the rest of main function
        #normal cli
        else:
            #Script started directly
            if config.ui == 'cli': argcomplete.autocomplete(parser)
            args = parser.parse_args()
    else: args = parser.parse_args(args) # args passed to main function directly
    
    #Make dict out of args namespace for passing to pipeline
    args = vars(args)

    # First check if it was requested to save config
    if args.pop('save_config'):
        from genairics import saveConfig
        for param in config.get_param_names():
            if param in args:
                config.__setattr__(param, args[param])
        saveConfig(config)
        
    # Extract other non pipeline specific arguments
    joblauncher = joblaunchers[args.pop('job_launcher')]
    remotehost = args.pop('remote_host')
    verbose = args.pop('verbose')
    workflow = args.pop('function')(**args)

    if verbose:
        logger.setLevel(logging.DEBUG)
    else: logger.setLevel(logging.INFO)
    
    if joblauncher:
        logger.debug('submitting %s to %s',workflow,joblauncher)
        joblauncher(job=workflow,remote=remotehost).run()
    else: runWorkflow(workflow)

# Run main program logics when script called directly
if __name__ == "__main__":
    main()
