```
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

GENeric AIRtight omICS pipelines
```

## Disclosure

There comes a point in time when any human just has to develop their
own, fully-fledged computational genomics platform. This is not that
time for me, but it is good to set it as an aim: aiming for the stars,
landing somewhere on the moon.

### Design goals

#### generic pipelines

Although the pipelines here available are only developed for my
specific bioinformatics needs and that of my collaborators, they are
build up in a generic way, and some of the functionality in the main
genairics package file might help or inspire you to build your own
pipelines. The core of the pipelines is build with
[luigi](https://luigi.readthedocs.io) and extensions are provided in
this package's initialization file.

#### airtight pipelines

The pipelines are build so they can be started with a single,
fool-proof command.  This should allow my collaborators, or scientists
wanting to replicate my results, to easily do so. A
docker container is provided with the package so the processing
can be started up on any platform.

#### omics pipelines

The pipelines grow organically, as my research needs expand. I aim to
process any kind of data. If you want to use my set of pipelines, but
desire an expansion to make it more omics-like, contact me and we can
see if there are opportunities to collaborate. More generally,
everyone is welcome to leave suggestions in the [issues
section](https://github.com/beukueb/genairics/issues) of the
repository.

## Installation

### genairics package

#### Dependencies

Python 3 has to be installed: see https://www.python.org/downloads/ for instructions.

#### Prepare virtualenv [optional]

     sudo pip3 install virtualenvwrapper
     echo "export WORKON_HOME=~/Envs" >> ~/.bashrc
     echo "export VIRTUALENVWRAPPER_PYTHON=$(which python3)" >> ~/.bashrc
     . ~/.bashrc
     mkdir -p $WORKON_HOME
     . /usr/local/bin/virtualenvwrapper.sh
     mkvirtualenv genairics
     echo "export GAX_REPOS=$VIRTUAL_ENV/repos" >> $VIRTUAL_ENV/bin/postactivate
     echo "export GAX_PREFIX=$VIRTUAL_ENV" >> $VIRTUAL_ENV/bin/postactivate
     echo "export GAX_RESOURCES=$VIRTUAL_ENV/resources" >> $VIRTUAL_ENV/bin/postactivate
     echo "unset GAX_REPOS GAX_PREFIX GAX_RESOURCES" >> $VIRTUAL_ENV/bin/predeactivate

#### Install

     workon genairics #only when working in virtualenv
     pip3 install genairics

### Get your BASESPACE_API_TOKEN accessToken

Folow the steps 1-5 from this link:
https://help.basespace.illumina.com/articles/tutorials/using-the-python-run-downloader/

	emacs ~/.BASESPACE_API #Store your accessToke here, instead of emacs use any editor you like
	chmod 600 ~/.BASESPACE_API #For security, only rw access for your user

### Prepare your HPC account [for UGent collaborators]

#### add to your HPC ~/.bashrc =>

    if [[ -v SET_LUIGI_FRIENDLY ]]; then module load pandas; unset SET_LUIGI_FRIENDLY; fi
    if [[ -v R_MODULE ]]; then module purge; module load R-bundle-Bioconductor; unset R_MODULE; fi
    export PATH=$VSC_DATA_VO/resources/bin:$PATH:~/.local/bin
    export BASESPACE_API_TOKEN= #Set this to your basespace api token

#### Execute the following commands

    module load pandas
    pip3 install --user genairics
    mkdir $VSC_DATA_VO_USER/{data,results}

## Example run

### Docker

    docker run -v ~/resources:/resources -v ~/data:/data -v ~/results:/results \
	       --env-file ~/.BASESPACE_API beukueb/genairics RNAseq \
	       NSQ_Run240 /data --genome saccharomyces_cerevisiae

### qsub job

    qsub -l walltime=10:50:00 -l nodes=1:ppn=12 -m n \
    -v project=NSQ_Run240,datadir=$VSC_DATA_VO_USER/data,forwardprob=0,GENAIRICS_ENV_ARGS=RNAseq,SET_LUIGI_FRIENDLY= \
    $(which genairics)
   
## General setup for sys/vo admin

Choose a different prefix, if you want dependencies installed in different dir

    git clone https://github.com/beukueb/genairics.git && cd genairics
    PREFIX=$VSC_DATA_VO/resources genairics/scripts/genairics_dependencies.sh

## Development

### HPC

#### Interactive node for debugging

    qsub -I -l walltime=09:50:00 -l nodes=1:ppn=12

#### Debug job

    qsub -q debug -l walltime=00:50:00 -l nodes=1:ppn=4 -m n \
    -v datadir=$VSC_DATA_VO_USER/data,project=NSQ_Run270,forwardprob=0,SET_LUIGI_FRIENDLY=,GENAIRICS_ENV_ARGS= \
    $VSC_DATA_VO/resources/repos/genairics/genairics/RNAseq.py

### Submit package to pypi

    python setup.py sdist upload -r pypi

### Docker

#### Build container

     docker build . --tag beukueb/genairics:latest
     docker push beukueb/genairics:latest
     docker tag beukueb/genairics:latest genairics

To debug, reset entrypoint:

    docker run -it -v /tmp/data:/data -v /tmp/results:/results -v /Users/cvneste/mnt/vsc/resources:/resources --env-file ~/.BASESPACE_API --entrypoint bash bcaf446c7765

#### Cleaning docker containers/images

     docker system prune -f