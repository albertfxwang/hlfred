import os
import sys
import click
from datetime import datetime

CONTEXT_SETTINGS = dict(auto_envvar_prefix='HLFRED')

class Context(object):

    def __init__(self):
        self.verbose = False
        self.dsdir = None
        self.rundir = None 
        self.dataset_name = None
        self.refimg = None
        self.refcat = None
        self.useacs = False

    def log(self, msg, *args):
        """Logs a message to stderr."""
        if args:
            msg %= args
        click.secho(msg, file=sys.stderr, fg='blue')
    
    def wlog(self, msg, *args):
        """Logs a warning message to stderr."""
        if args:
            msg %= args
        click.secho(msg, file=sys.stderr, fg='yellow')
    
    def elog(self, msg, *args):
        """Logs a error message to stderr."""
        if args:
            msg %= args
        click.secho(msg, file=sys.stderr, fg='red')

    def vlog(self, msg, *args):
        """Logs a message to stderr only if verbose is enabled."""
        if not self.verbose:
            if args:
                msg %= args
            click.secho(msg, file=sys.stderr, fg='green')   
    
    def dt(self):
        """Returns current time as string."""
        return str(datetime.now())


pass_context = click.make_pass_decorator(Context, ensure=True)
cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'commands'))


class HLFRED_CLI(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith('.py') and filename.startswith('cmd_'):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = __import__('hlfred.commands.cmd_' + name, None, None, ['cli'])
        except ImportError, e:
            print e
            return
        return mod.cli


@click.command(cls=HLFRED_CLI, context_settings=CONTEXT_SETTINGS)
@click.argument('dataset_name')
@click.option('--dsdir',  type=click.Path(exists=True, dir_okay=True, resolve_path=True), help='Input datasets directory (overrides HLFRED_DSDIR enviroment variable)')
@click.option('--rundir', type=click.Path(exists=True, dir_okay=True, resolve_path=True), help='Dataset run directory (overrides HLFRED_RUNDIR enviroment variable)')
@click.option('-r', '--refimg', default='', help='Reference image for alignment')
@click.option('-c', '--refcat', default='', help='Reference catalog for alignment')
@click.option('-a', '--useacs', is_flag=True, help='Use only ACS/WFC images for alignment')
@click.option('-v', '--verbose', is_flag=True, help='Disables verbose mode')
@pass_context
def cli(ctx, dataset_name, dsdir, rundir, verbose, refimg, refcat, useacs):
    """The HLDFRED command line interface."""
    ctx.dataset_name = dataset_name
    dsdir_env = os.getenv('HLFRED_DSDIR')
    if not dsdir_env:
        if not dsdir:
            ctx.elog('No input dataset directory set. Must be set in the HLFRED_DSDIR enviroment variable or as an option (--dsdir).')
            sys.exit(1)
        else:
            ctx.dsdir = dsdir
    else:
        ctx.dsdir = dsdir_env
    ctx.log('HLFRED will use %s as input datset directory', ctx.dsdir)
    rundir_env = os.getenv('HLFRED_RUNDIR')
    if not rundir_env:
        if not rundir:
            ctx.elog('No running directory set. Must be set in the HLFRED_RUNDIR enviroment variable or as an option (--rundir).')
            sys.exit(1)
        else:
            ctx.rundir = rundir
    else:
        ctx.rundir = rundir_env
    ctx.log('HLFRED will use %s as the run directory', ctx.rundir)
    if refimg:
        if not os.path.exists(refimg):
            ctx.elog('Reference image %s not found!' % refimg)
            sys.exit(1)
        else:
            ctx.refimg = refimg
    if refcat:
        if not os.path.exists(refcat):
            ctx.elog('Reference catalog %s not found!' % refcat)
            sys.exit(1)
        else:
            ctx.refcat = refcat
    ctx.verbose = verbose
    if not ctx.verbose:
        ctx.vlog('Verbose is enabled')
    else:
        ctx.vlog('Verbose is disabled')
    if ctx.useacs:
        ctx.vlog('Using only ACSWFC images for alignment')
    