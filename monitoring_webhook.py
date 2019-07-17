#!python3
"""
Used to collect printer errors and sending 
error alert to a mattermost channel configured in
the config.py file. 
Depends on matterhook https://github.com/numberly/matterhook
"""
import config as cfg
from matterhook import Webhook
from printer_mibs import get_printer_errors, ping
import multiprocessing as mp

if __name__ == '__main__':
    quiet = True
    pings = 5
    all_errors = False
    error = ''
  
    #Ping all printers in parallel
    with mp.Pool(32) as pool:
        ping_async = [pool.apply_async(ping, args=(printer, pings)) for printer in cfg.printers]
        active_printers = [i for i, p in zip(cfg.printers, ping_async) if p.get()] 
        inactive_printers = [i for i, p in zip(cfg.printers, ping_async) if not p.get()] 
        
    if inactive_printers and not quiet:
        for printer in inactive_printers:
            error += '{}: host \'{}\' unknown or offline\n'.format(printer.split('.')[0].upper(), printer)

    #Running queries in parallel
    with mp.Pool(32) as pool:
        err = []
        for printer in active_printers:
            err.append(pool.apply_async(get_printer_errors, args=(printer, cfg.ignore_list, all_errors)))
       
        if err:
            err = [str(e.get()) for e in err]
            err = list(filter(None, err))
            error += ''.join(err)
            error = error.strip('\n')
    
    if len(error) > 0:
        mwh = Webhook(cfg.webhook_url, cfg.webhook_key)
        mwh.send(error.replace('\xe6', 'ae').replace('\xf8', 'oe').replace('\xe5', 'aa'))
