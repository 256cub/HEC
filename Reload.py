import time
import os
import logging

filename = '/var/log/HEC/info.log'
logging.basicConfig(filename=filename, level=logging.INFO,
                    format='%(asctime)s %(name)s | %(levelname)s => %(message)s')

with open(filename, 'r') as f:
    lines = f.read().splitlines()
    total = len(lines)

time.sleep(60)

with open(filename, 'r') as f:
    lines = f.read().splitlines()
    current = len(lines)

    if current == total:
        print("Script will be restarted")
        logging.warning('RESTARTING HEC | No new Logs | Total: {} lines'.format(current))
        # os.system('reboot')

        time.sleep(1)
        os.system('killall chrome')
        time.sleep(1)
        os.system('killall lxterminal')
        time.sleep(1)

        os.system('lxterminal -e /usr/bin/python3.8 /PYTHON/HEC/HEC.py')
        time.sleep(5)