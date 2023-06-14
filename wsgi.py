import os
import sys


PACKAGE_PARENT = os.path.abspath(os.getcwd())
activate_this = os.path.join(PACKAGE_PARENT, "venv\\Scripts\\activate_this.py")

with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

BASE_DIR = os.path.join(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
)
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from karmalegoweb import create_app

try:
    application = create_app()
except Exception as e:
    print(e)
