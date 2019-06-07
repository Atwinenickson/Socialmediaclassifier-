#!C:\Users\atwiine\PycharmProjects\finalyearproject\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'bcrypt-tool==1.0','console_scripts','bcrypt-tool'
__requires__ = 'bcrypt-tool==1.0'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('bcrypt-tool==1.0', 'console_scripts', 'bcrypt-tool')()
    )
