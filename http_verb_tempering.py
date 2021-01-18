from colored import fore, back, style
import os
import argparse
import requests
from urllib3.exceptions import InsecureRequestWarning

def file_reader(file_name):
    flist = []
    file = open(file_name,"r")
    file_in = file.readlines()
    for f in file_in:
        flist.append(f.replace("\n",""))
    return flist

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', "--url", required=True, help="e.g. https://example.com:port/path")
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbosity",
        action="count",
        default=0,
        help="verbosity level (-v for verbose, -vv for debug)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        dest="quiet",
        action="store_true",
        default=False,
        help="show no information at all",
    )
    args = parser.parse_args()
    logger = Logger(args.verbosity, args.quiet)
    url = args.url
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    #Logger.verbose(f"Testing on host: {url}")
    print("Testing on host: " + fore.LIGHT_GREEN + style.BOLD + url + style.RESET)
    response = requests.options(url, verify=False)
    if response.status_code == 200:
        print('The HTTP methods available are: ')
        try:
            methods = response.headers['Allow'].replace(" ","").split(',')
        except:
            methods = []

        for verb in methods:
            print(fore.LIGHT_YELLOW + verb + style.RESET)
            tmp_methods = file_reader('http_verb_list')
            methods = methods + list(set(tmp_methods) - set(methods))
        if methods == []:
            print(fore.LIGHT_YELLOW + "OPTIONS HTTP method available but seems empty" + style.RESET)
            methods = file_reader('http_verb_list')
    else:
        print(fore.LIGHT_RED +'OPTIONS HTTP method is disabled' + style.RESET)
        print(fore.LIGHT_YELLOW + 'Testing with HTTP methods dictionary instead:'+ style.RESET)
        methods = file_reader('http_verb_list')
    for verb in methods:
        print(fore.LIGHT_GREEN + "Testing with verb: " + style.BOLD + verb + style.RESET)
        try:
            response = getattr(requests, verb.lower())
            response = response(url, verify=False)
            code = response.status_code
            print('HTTP/ ' + str(code) + ' ' + response.reason)
        #headers = response.headers
        #print(fore.LIGHT_YELLOW + 'Header:' + style.RESET)
        #print(headers)
        #print(fore.LIGHT_YELLOW + 'Body:' + style.RESET)
        #print(response.text)
        except:
            os.system('curl -LIk -X' + verb + ' ' + url + ' 2>&1 | head -n 4 | tail -1')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print ("\n Bye")
        raise SystemExit
