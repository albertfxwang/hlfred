import click
from hlfred.cli import pass_context
from hlfred.utils import utils
from hlfred.tasks import drizzle_mosaic
import sys, os, shutil, glob

task = os.path.basename(__name__).split('.')[-1][4:]

@click.command(task, short_help='Drizzle single images')
@click.option('--ctype', default='minmed', help='Type of combine operation')
@click.option('--itype', default='_flt.fits', help='Input file type')
@click.option('--ofile', help='Output file (defaults to dsname_filter)')
@click.option('--ptask', default='apsh', help='Previous task run')
@pass_context
def cli(ctx, itype, ofile, ptask):
    """
    Drizzles final mosaic for each filter with an orientation of 0.0 (north up)
    """
    dsn = ctx.dataset_name
    useacs = ctx.useacs
    ctx.log('Running task %s for dataset %s', task, dsn)
    procdir = os.path.join(ctx.rundir, dsn)
    os.chdir(procdir)
    cfgf = '%s_cfg.json' % dsn
    cfg = utils.rConfig(cfgf)
    tcfg = cfg['tasks'][task] = {}
    tcfg['ptask'] = ptask
    tcfg['itype'] = itype
    tcfg['ofile'] = ofile
    tcfg['stime'] = ctx.dt()
    tcfg['completed'] = False
    for instdet, data in cfg['images'].iteritems():
        for fltr, images in data.iteritems():
            outfile = '%s_%s' % (dsn, fltr.lower())
            infiles = [str('%s%s' % (i, itype)) for i in images]
            ctx.vlog('Drizzling mosaic %s', outfile)
            try:
                drizzle_mosaic.drzMosaic(infiles, outfile, ctype=ctype)
            except Exception, e:
                utils.wConfig(cfg, cfgf)
                print e
                raise
    tcfg['etime'] = ctx.dt()
    tcfg['completed'] = True
    ctx.vlog('Writing configuration file %s for %s task', cfgf, task)
    utils.wConfig(cfg, cfgf)