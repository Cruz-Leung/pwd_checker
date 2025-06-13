import pyhibp
from pyhibp import pwnedpasswords as pw

def check_password():
    resp = pyhibp.get_all_breaches()
    print("Total breaches:", len(resp))

check_password()