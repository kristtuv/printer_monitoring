#!python3
"""
Script used to collect general printer info
Usage:
    python printer_status.py example_printer1 
    python printer_status.py example_printer1 example_printer2 example_printer3 
    python printer_status.py example_printer1.printer.example.com
"""

from printer_mibs import ping, get_mib
from datetime import datetime, timedelta
from argparse import ArgumentParser
import config as cfg
import multiprocessing as mp

def get_printer_info(printer):
    """
    Collect printerinfo:
        Location
        Model
        Display info
        Supply status
        Uptime
    Args:
        printer(str): printer name

    Returns:
        info(str): String of info collected about printer
    """
    model = str(get_mib(printer, 'SNMPv2-MIB', 'sysDescr', 0)).split('/')
    location = str(get_mib(printer, 'SNMPv2-MIB', 'sysLocation', 0)).split(',')[2]
    display = str(get_mib(printer, 'Printer-MIB', 'prtConsoleDisplayBufferText', 1, 1))
    supply_level_black = str(get_mib(printer, 'Printer-MIB', 'prtMarkerSuppliesLevel', 1, 1))
    supply_level_cyan = str(get_mib(printer, 'Printer-MIB', 'prtMarkerSuppliesLevel', 1, 3))
    supply_level_magenta = str(get_mib(printer, 'Printer-MIB', 'prtMarkerSuppliesLevel', 1, 4))
    supply_level_yellow = str(get_mib(printer, 'Printer-MIB', 'prtMarkerSuppliesLevel', 1, 5))
    supply_level_waste = str(get_mib(printer, 'Printer-MIB', 'prtMarkerSuppliesLevel', 1, 2))
    page_count = int(get_mib(printer, 'Printer-MIB', 'prtMarkerLifeCount', 1, 1))

    uptime_seconds = int(get_mib(printer, 'DISMAN-EVENT-MIB', 'sysUpTimeInstance'))/100
    uptime_time = timedelta(seconds=uptime_seconds)
    uptime_start = (datetime.today() - uptime_time).strftime('%a %b %d, %Y %H:%I')

    info = 'Querying \033[1m' + printer.split('.')[0] + '\033[0m'
    if location:
        info += ' (room ' + location +')'
    info += ':\nModel:\n'
    for line in model:
        info += f'{line}\n'
    info += 'Display:\n'
    info += f'{display}\n'
        
    info += 'Supply status:\n'
    info += '%6i %% Black\n' % int(supply_level_black)
    info += '%6i %% Cyan\n' % int(supply_level_cyan)
    info += '%6i %% Magenta\n' % int(supply_level_magenta)
    info += '%6i %% Yellow\n' % int(supply_level_yellow)
    info += '%6i %% Waste\n' % int(supply_level_waste)
    info += 'Page count: %s\n' % page_count
    info += 'Uptime: %s (since %s)\n' % (uptime_time, uptime_start)

    return info

def argparser():
    usage = """
    python printer_status.py example_printer1 
    python printer_status.py example_printer1 example_printer2 example_printer3 
    python printer_status.py example_printer1.printer.example.com
    """
    
    parser = ArgumentParser(usage=usage)
    parser.add_argument('printers', type=str, nargs='*', 
                        default=cfg.printers,
                        help='Give name(s) of printers')
    args = parser.parse_args()
    suffix = '.printer.example.com'
    args.printers = [p if p.endswith(suffix) else p+suffix for p in args.printers]
    return args


if __name__ == '__main__':
    args = argparser()
    #Ping all printers in parallel
    with mp.Pool(32) as pool:
        ping_async = [pool.apply_async(ping, args=(printer, 3)) for printer in args.printers]
        active_printers = [i for i, p in zip(args.printers, ping_async) if p.get()] 
        inactive_printers = [i for i, p in zip(args.printers, ping_async) if not p.get()] 
    
    if inactive_printers:
        for printer in inactive_printers:
            error += '{}: host \'{}\' unknown or offline\n'.format(printer.split('.')[0].upper(), printer)

    #Get all printer info in parallel
    with mp.Pool(32) as pool:
        info = []
        for printer in active_printers:
            info.append(pool.apply_async(get_printer_info, args=(printer,)))

        info = [i.get() for i in info]

    for i in info:
        print(i)
