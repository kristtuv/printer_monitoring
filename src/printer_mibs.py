#!python3
"""
The main library used to collect the printer information
"""
__all__ = ['ping', 'get_mib', 'walk_mib', 'get_printer_errors']
from pysnmp.hlapi import *
from pysnmp.smi import builder
from subprocess import CalledProcessError, check_output, STDOUT
import config as cfg
from datetime import datetime, timedelta
import re

#Setting the PyMib source directory which has been build with create_mibs.py
engine = SnmpEngine()
engine.getMibBuilder().addMibSources(builder.DirMibSource(cfg.dstdirectory))


def ping(host, times=1):
    """
    Silently pings the host once. Returns true if host answers; false if it doesn't.
    Args:
        host(str): printer name e.g example_printer1.printer.example.com
        times(int): number of pings
    Returns
        bool: True if connection is established, else False
    """

    try:
        check_output(['ping', '-c', str(times), host], stderr=STDOUT, universal_newlines=True)
    except CalledProcessError:
        return False
    return True

def get_mib(printer, mib_name, mib_variable, *mib_id):
    """
    getCmd returns all the objects found as a generator. We use next(..)
    to get the generator value. The list returned is indexed in the following
    way:
    [3][0][1]

    The first index is a list of four elements with the first three being error values
    and the last index [3] being the varBind we want

    The second index is the varBind we want, however it is returned as a list because
    it is possible to bulksearch for varBinds in pysnmp.hlapi.nextCmd(..). 
    We have not implemented the bulk search and hence we
    want the first (and only) index in this list [0]

    The varBind is a list of one element containing an objectType.
    The object behaves as a list where element 0 is the mib number
    and element 1 is the returned information we want, hence the index 1
    Args:  
        printer(str): name of printer
        mib_name(str): name of the mib file to search e.g Printer-MIB
        mib_variable(str): the name of the mib we want to search for in the mib file
        *mib_id(int): The mib variable instance identification. 

    Returns:
        getCmd(str): a str of info found in the mib request

    Example:
        We want to walk the mib prtMarkerLifeCount.1.1
        get_mib('example_printer1.printer.example.com',
                'Printer-MIB',
                'prtMarkerLifeCount',
                1,
                1,)
     
    """
    return next(getCmd(engine,
                CommunityData('public', mpModel=0),
                UdpTransportTarget((printer, 161)),
                ContextData(),
                ObjectType(ObjectIdentity(mib_name, mib_variable, *mib_id).loadMibs()))
                )[3][0][1]

def walk_mib(printer, mib_name, mib_variable, *mib_id):
    """
    nextCmnd returns all the objects found as a generator. We convert this to a list.
    Every object in the list is nested and indexed in the following way:
    [3][0][1]

    The first index is a list of four elements with the first three being error values
    and the last index [3] being the varBind we want

    The second index is the varBind we want, however it is returned as a list because
    it is possible to bulksearch for varBinds in pysnmp.hlapi.nextCmd(..). 
    We have not implemented the bulk search and hence we
    want the first (and only) index in this list [0]

    The varBind is a list of one element containing an objectType.
    The object behaves as a list where element 0 is the mib number
    and element 1 is the returned information we want, hence the index 1

    With lexiographicMode turned on the nextCmd will traverse the entire mib-tree.

    Args:  
        printer(str): name of printer
        mib_name(str): name of the mib file to search e.g Printer-MIB
        mib_variable(str): the name of the mib we want to search for in the mib file
        *mib_id(int): The mib variable instance identification. 

    Returns:
        printer_info(list): a list of info found in the mib walk

    Example:
        We want to walk the mib prtAlerDescription.1
        mib_walk('example_printer1.printer.example.com',
                 'Printer-MIB',
                 'prtAlertDescription',
                 1)
    """
    printer_info  = list(
                nextCmd(engine,
                CommunityData('public', mpModel=0),
                UdpTransportTarget((printer, 161)),
                ContextData(),
                ObjectType(ObjectIdentity(mib_name, mib_variable, *mib_id)),
                lexicographicMode=False)
                )
    printer_info  = [str(info[3][0][1]) for info in printer_info] 
    return printer_info


def get_printer_errors(printer, ignore_list=None, all=False):
    """
    Checks the mib prtAlertDescription. This mib returns a large list of alerts
    and is cross-referenced with the ignore_list from config.py to only return
    relevant alerts. If the all flag is given, the ignore_list is is not used and
    all the alerts found will be returned.
    A string of the errors found with the location, alert description and time
    since the alert was registered is returned.

    Args:
        printer (str): name of printer
        ignore_list (list): alerts to ignore
        all (bool): print all alerts

    Returns:
        parsed_errors (str): A string of alert messages found 
    """
    printer_alerts = walk_mib(printer, 'Printer-MIB', 'prtAlertDescription', 1)
    if printer_alerts:
        printer_alerts = [alert.split('{')[0] for alert in printer_alerts] 
        printer_ticks = walk_mib(printer, 'Printer-MIB', 'prtAlertTime', 1)
        system_uptime_ticks = int(get_mib(printer, 'DISMAN-EVENT-MIB', 'sysUpTimeInstance'))
        time_since_alert = [str(timedelta(seconds=(system_uptime_ticks - int(tick)))/100) for tick in printer_ticks] 
        location = str(get_mib(printer, 'SNMPv2-MIB', 'sysLocation', 0)).split(',')[2]
        parsed_errors = ''
        for alert, time in zip(printer_alerts, time_since_alert):
            if all or not re.search(ignore_list, alert.lower()):
                parsed_errors += '%s (%s): %s in %s\n' % (printer.split('.')[0].upper(), location, alert, time)
        return parsed_errors
