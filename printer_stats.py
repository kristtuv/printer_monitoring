#!python3
'''Printer Stats.
Stores the page count history for printers. Unless the script is provided with start 
and end dates, it will default to page count development since yesterday 
(Monday-Saturday) or the last week's development (Sundays).

Options:
  -s --start <YYYY-MM-DD>   Start date
  -e --end <YYYY-MM-DD>     End date
  -a --add <name>           Add a new printer
  -r --remove <name>        Remove a printer
  -d=True --debug=True      Run in debug mode

Made by Torgeir Lebesbye (torgeirl) during the fall of 2016. MIT License.
'''

import json
import os.path
import time

from argparse import ArgumentParser
from datetime import date, timedelta
from os.path import dirname, join
from sys import argv, exit

from config import printers, printer_placement
from printer_mibs import *



def map_path(target_name):
    '''Enables path names to be dynamically ascertained at runtime.'''
    return join(dirname(__file__), target_name).replace('\\', '/')

def file_existance(json_file):
    """
    Check the existance of file
    """
    file = map_path(json_file)
    if not os.path.exists(file):
        with open(file, 'w') as outfile:
            json.dump({}, outfile)
            

def get_page_count(printer):
    '''Returns a printer's page count'''
    page_count = walk_mib(printer, 'Printer-MIB', 'prtMarkerLifeCount')[0]
    if not page_count is None and not page_count is '0':
        return page_count
    else:
        return 'n/a'

def add_printer(printer, location):
    '''Add a new printer to the JSON file'''
    with open(map_path(json_file), 'r') as infile:
        data = json.load(infile)
    if printer not in data:
        try:
            data[printer] = {}
            data[printer]['location'] = str(location)
            with open(map_path(json_file), 'w') as outfile:
                json.dump(data, outfile)
            return f'{printer} has successfully been added to dataset'
        except:
            return f'Error: something went wrong while trying to add \'{printer}\''
    else:
        return f'Error: {printer} already in dataset'


def remove_printer(printer):
    '''Remove a printer from the JSON file'''
    with open(map_path(json_file), 'r') as infile:
        data = json.load(infile)
    if printer in data:
        try:
            data.pop(printer, None)
            with open(map_path(json_file), 'w') as outfile:
                json.dump(data, outfile)
            return f'{printer} has successfully been removed from dataset'
        except:
            return f'Error: something went wrong while trying to remove \'{printer}\'' 
    else:
        return f'Error: \'{printer}\' not in dataset'

def check_printers(debug=False):
    '''Checks page count on printer in the JSON file.'''
    with open(map_path(json_file), 'r') as infile:
        data = json.load(infile)
    for printer in data.keys():
        if debug:
            status = 'Querying %s ...' % printer.split('.')[0]
            print(status,)
        start_time = time.time()
        page_count = get_page_count(printer)
        end_time = time.time()
        data[printer][date.strftime(date.today(), '%Y-%m-%d')] = page_count
        if debug:
            print('OK (%.1f sec)' % (end_time - start_time))
    with open(map_path(json_file), 'w') as outfile:
        json.dump(data, outfile)

def make_report(start_date, end_date):
    """
    Returns a report on page count increase for the period.
    """

    with open(map_path(json_file), 'r') as infile:
        data = json.load(infile)
    total = 0
    report = '\nPRINTER USAGE BETWEEN %s AND %s:\n\n' % (start_date, end_date)
    report += '     PRINTER | ROOM# |  COUNT  | INCREASE\n'
    report += '-----------------------------------------\n'
    for printer in sorted(data,key=lambda x:int(data[x]['location'])):
        start = data[printer].get(start_date, 'n/a')
        end = data[printer].get(end_date, 'n/a')
        if start.isdigit() and end.isdigit():
            increase = int(end)-int(start)
            total += increase
            increase = str(increase)
        else:
            increase = 'n/a'
        location = int(data[printer].get('location'))
        report += '%12s | %5i | %7s | +%s\n' % (printer.split('.')[0], location, end, increase)
    report += '\n%i printers, total increase in period: %i pages\n' % (len(data), total)
    return report

def argparser():
    usage = f'Usage: {argv[0]} [-s startdate -e enddate] [-a new_printer]...' 

    parser = ArgumentParser(usage=usage)
    parser.add_argument('-s', '--start',
        help='Spesify a start date (YYYY-MM-DD)')
    parser.add_argument('-e', '--end',
        help='Spesify an end date (YYYY-MM-DD)')
    parser.add_argument('-a', '--add',
        help='Add a new printer')
    parser.add_argument('-r', '--remove',
        help='Remove a printer')
    parser.add_argument('-d', '--debug',
        action='store_true',
        help='Run script in debug mode')
    args = parser.parse_args()
    suffix = cfg.suffix
    args.printers = [p if p.endswith(suffix) else p+suffix for p in args.printers]
    return args

if __name__ == '__main__':
    args = argparser()
    json_file = 'page_count.json'
    file_existance(json_file)

    if args.add != None:
        text = f'Please provide the location (rom number) of \'{args.add}\':'
        print (text)
        location = input('-->')
        print(add_printer(args.add, location))

    if args.remove != None:
        text = f'Are you sure you want to remove \'{args.remove}\' from the dataset, (Y/N):'
        print (text)
        reply = input('-->')
        print (reply)
        if reply.lower() == 'y':
            print(remove_printer(args.remove))
        else:
            print(f'0K, leaving {args.remove} in the dataset. Be careful with the remove command!')

    if args.start != None and args.end != None:
        start_date = args.start
        end_date = args.end
    else:
        if date.weekday(date.today()) == 6:
            start_date = date.strftime(date.today()- timedelta(7), '%Y-%m-%d')
        else:
            start_date = date.strftime(date.today()- timedelta(1), '%Y-%m-%d')
        end_date = date.strftime(date.today(), '%Y-%m-%d')
    try:
        check_printers(debug=args.debug)
        print(make_report(start_date, end_date))
    except:
        print(usage)
        exit(1)
