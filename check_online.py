#!/python3

"""
Pings all the printers registered in config.py, or if arguments
arguments are given at runtime pings the printers given as
arguments

Usage:
python check_online.py
python check_online.py example_printer1
python check_online.py example_printer1 example_printer2
python check_online.py example_printer1.printer.example.com
python check_online.py example_printer1.printer.example.com example_printer2.printer.example.com
"""
from subprocess import CalledProcessError, check_output, STDOUT

from sys import argv
from printer_mibs import ping
from argparse import ArgumentParser
import config as cfg
import multiprocessing as mp


if __name__=='__main__':
    usage = '''
    python check_online.py
    python check_online.py example_printer1
    python check_online.py example_printer1 example_printer2
    python check_online.py example_printer1.printer.example.com
    python check_online.py example_printer1.printer.example.com example_printer2.printer.example.com
    '''
    
    error = ''
    parser = ArgumentParser(usage=usage)
    parser.add_argument('printers', type=str, nargs='*', 
                        default=cfg.printers,
                        help='Give name(s) of printers')
    parser.add_argument('-a', '--all', action='store_true',
                        help='Use all printers defined in config.py')
    args = parser.parse_args()
    suffix = cfg.suffix
    args.printers = [p if p.endswith(suffix) else p+suffix for p in args.printers]

    with mp.Pool(32) as pool:
        ping_async = [pool.apply_async(ping, args=(printer, 3)) for printer in args.printers]
        inactive_printers = [i for i, p in zip(args.printers, ping_async) if not p.get()] 

    if inactive_printers:
        for printer in inactive_printers:
            error += '{}: host \'{}\' unknown or offline\n'.format(printer.split('.')[0].upper(), printer)
        print(error)

