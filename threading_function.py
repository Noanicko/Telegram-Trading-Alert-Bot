import config as cfg
import trade_logic as tl
import threading as td

def threading(threads):
     for pair_name,pair in cfg.WATCHED_PAIRS:
            t = td.Thread(target=tl.monitor_pair, args=(pair_name, pair))
    
            #Clear Threads after Exit
            t.daemon = True 
            t.start()
            threads.append(t)