
import sys
import json

try:
    import urllib.request
except ModuleNotFoundError:
    print("Please install urllib. (pip install urllib3)")
    e = input("Press enter to close")
    sys.exit("Process finished with exit code: ModuleNotFoundError")


def get_ip_address():
    url = 'https://ipinfo.io/json'
    resp = urllib.request.urlopen(url)
    data = json.load(resp)

    return data['ip']
