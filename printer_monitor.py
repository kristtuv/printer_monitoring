#!python3

"""
Run script to collect errors from the printers
Usage:
    ../venv/bin/python printer_monitor.py 
    ../venv/bin/python printer_monitor.py example_printer1
    ../venv/bin/python printer_monitor.py example_printer1 --all
    ../venv/bin/python printer_monitor.py example_printer1 --pings 5
    ../venv/bin/python printer_monitor.py example_printer1 --quiet
    ../venv/bin/python printer_monitor.py example_printer1 example_printer2

"""

from argparse import ArgumentParser
from datetime import datetime, timedelta

import config as cfg
import multiprocessing as mp

from printer_mibs import ping, get_mib, walk_mib, get_printer_errors

def argparser():
    """
    Parsing arguments given at runtime
    """

    usage = """
    Run script to collect errors from the printers at ifi

    ../venv/bin/python printer_monitor.py 
    ../venv/bin/python printer_monitor.py example_printer1
    ../venv/bin/python printer_monitor.py example_printer1 --all
    ../venv/bin/python printer_monitor.py example_printer1 --pings 5
    ../venv/bin/python printer_monitor.py example_printer1 --quiet
    ../venv/bin/python printer_monitor.py example_printer1 example_printer2

    """

    parser = ArgumentParser(usage=usage)
    parser.add_argument('-a', '--all',
        action='store_true', 
        help='Display all errors')
    parser.add_argument('-p', '--pings',
        default=1,
        help='More pings takes more time, but gives less false positives')
    parser.add_argument('-q', '--quiet',
        default=False,
        help='Ignore unresponsive printers (no response to ping)')
    parser.add_argument('printers', nargs='*', default=cfg.printers,
                        help='If no arguments are given, all printernames in config.py are used')
    args = parser.parse_args()
    suffix = cfg.suffix
    args.printers = [p if p.endswith(suffix) else p+suffix for p in args.printers]
    return args

if __name__ == '__main__':
    args = argparser()
    error = ''
    
    #Pinging printers async
    with mp.Pool(32) as pool:
        ping_async = [pool.apply_async(ping, args=(printer, args.pings)) for printer in args.printers]
        active_printers = [i for i, p in zip(args.printers, ping_async) if p.get()] 
        inactive_printers = [i for i, p in zip(args.printers, ping_async) if not p.get()] 
        
    if inactive_printers and not args.quiet:
        for printer in inactive_printers:
            error += '{}: host \'{}\' unknown or offline\n'.format(printer.split('.')[0].upper(), printer)

    #Running queries async
    with mp.Pool(32) as pool:
        err = []
        for printer in active_printers:
            err.append(pool.apply_async(get_printer_errors, args=(printer, cfg.ignore_list, args.all)))
       
        if err:
            err = [e.get() for e in err]
            err = list(filter(None, err))
            error += ''.join(err)
            error = error.strip('\n')

    print(error)
