Printer Tools    
=============    
    
## Table of contents        
* [General Info](#general-info)        
* [Directory Structure](#directory-structure)        
* [Technologies](#technologies)        
* [Setup](#setup)        
* [Documentation](#documentation)        
* [Setting up CRON job](#setting-up-cron-job)        
* [Credits](#credits)        
* [License](#license)        
        
## General Info        
Python scripts that helps you monitor printers on a network.    
    
## Directory Structure        
```bash        
├── check_online.py                #Ping all printers        
├── compiled_mibs                  #Collection of mibs compiled by create_pymibs.py. Pysnmp needs files to be compiled to a .py file.        
│   ├── DISMAN-EVENT-MIB.py        #Compiled Mib        
│   ├── HOST-RESOURCES-MIB.py      #Compiled Mib        
│   ├── IANA-CHARSET-MIB.py        #Compiled Mib        
│   ├── IANAifType-MIB.py          #Compiled Mib        
│   ├── IANA-PRINTER-MIB.py        #Compiled Mib        
│   ├── IF-MIB.py                  #Compiled Mib        
│   └── Printer-MIB.py             #Compiled Mib        
├── config.py                      #Settings used in various scripts        
├── create_pymibs.py               #Used to compiled mibs into .py format used by Pysnmp        
├── matterhook                     #Hook for mattermost        
│   └── incoming.py                #Hook for mattermost        
├── monitoring_webhook.py          #Used to check for printer errors and send collected errors to mattermost channel        
├── printer_mibs.py                #Function file with general functions used in the scripts        
├── printer_monitor.py             #Used to check for errors/alerts        
├── printer_stats.py               #Used to process page_count.json        
├── printer_status.py              #Used to print general system stats of printers. Location, page_count, ink status etc.        
```        
            
## Technologies        
|Package       |Version          | 
|------------- |---------        |
|certifi       |2019.6.16        | 
|chardet       |3.0.4            | 
|idna          |2.8              | 
|pip           |19.1.1           | 
|ply           |3.11             | 
|pyasn1        |0.4.5            | 
|pycryptodomex |3.8.2            | 
|pysmi         |0.3.4            | 
|pysnmp        |4.4.9            | 
|requests      |2.22.0           | 
|setuptools    |28.8.0           | 
|urllib3       |1.25.3           | 
|wheel         |0.29.0           | 
|python        |3.6              | 
|matterhook    |                 |

## Setup        
To run the scripts you need to be on a network with access to the printers.
    
If the directory compiled_mibs are not found in the src directory, you need to generate this folder.      
You need to have access to the relevant mibs used and set the path to them in config.py, then run create_pymibs.py to compile the directory.      
   
Relevant mibs:       
DISMAN-EVEN-MIB    
Printer-MIB    
SNMPv2-MIB    
    
## Documentation    
### check_online.py    
DESCRIPTION    
    Pings all the printers registered in config.py, or if arguments    
    arguments are given at runtime pings the printers given as    
    arguments    
        
    Usage:    
    python check_online.py    
    python check_online.py example_printer1    
    python check_online.py example_printer1 example_printer2    
    python check_online.py example_printer1.printer.example.com    
    python check_online.py example_printer1.printer.example.com example_printer2.printer.example.com    
    
### compiled_mibs    
DESCRIPTION    
    Directory containing precompiled mibs. If this directory does not exist follow setup description      
    
### config.py/config.py.example    
DESCRIPTION    
File containing settings for running the scripts    
If example file, all settings must be set manually for your system    
    
### create_pymibs    
DESCRIPTION    
    Program is used to generate the .py versions of the mibs    
    which are used py pysnmp.    
    This files should already be generated and can be found    
    in the directory name equal to the dstdirectory name    
    found in config.py.    
    If the directory exist and you are not adding any new mibs    
    there should not be any reason for you to run this program.    
    
    Usage:    
    python create_pymibs.py    
    
    
### monitoring_webhook.py    
Used to collect printer errors and sending error alerts to mattermost chennel configureed in config.py      
Depends on [matterhook](https://github.com/numberly/matterhook)    
    
### printer_mibs.py    
DESCRIPTION    
    The main library used to collect the printer information    
    
### printer_monitor.py    
    
DESCRIPTION    
    Collects errors from printers    
        
    Usage:    
        python printer_monitor.py     
        python printer_monitor.py example_printer1    
        python printer_monitor.py example_printer1 --all    
        python printer_monitor.py example_printer1 --pings 5    
        python printer_monitor.py example_printer1 --quiet    
        python printer_monitor.py example_printer1 example_printer2    
    
### printer_stats.py    
DESCRIPTION    
    Stores the page count history for printers. Unless the script is provided with start     
    and end dates, it will default to page count development since yesterday     
    (Monday-Saturday) or the last weeks development (Sundays).    
    
    Options:    
      -s --start <YYYY-MM-DD>   Start date    
      -e --end <YYYY-MM-DD>     End date    
      -a --add <name>           Add a new printer    
      -r --remove <name>        Remove a printer    
      -d=True --debug=True      Run in debug mode    
        Monitor page count of your printers    
    
    
### printer_status    
DESCRIPTION    
    Script used to collect general printer info    
    Usage:    
        python printer_status.py example_printer1     
        python printer_status.py example_printer1 example_printer2 example_printer3     
        python printer_status.py example_printer1.printer.example.com    
    
    
## Setting up CRON job    
`$ export VISUAL=vim; crontab -e` opens the list of CRON jobs the user have on the server in the VIM editor. The following will create a CRON job that runs 23:45 each day:    
    
    TERM=xterm    
    45 23 * * * python printer_stats.py 2>&1 | mail -s "Subject" "mail@example.com"    
    
## Credits    
`printer_status.py` is essentially a port of an old (but still functional) Perl script written by [Peder Stray](https://github.com/pstray) in 2007, 2008 and 2011.     
    
The following scripts were written in python2 by [Torgeir Lebesbye](https://github.com/torgeirl) in 2016. Originally written using netsnmp and are fully functional when using python2.    
```    
printer_status.py    
printer_stats.py    
check_online.py    
monitoring_weebhook.py    
printer_monitor.py    
```    
`monitoring_webhook` and `printer_stats` is mainly unchanged from the origianl.
    
## License    
See the [LICENSE](LICENSE.md) file for license rights and limitations (MIT).    
