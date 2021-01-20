import urllib3
import argparse
import requests
from rich.table import Table
from rich import box
from rich.console import Console
from rich.progress import track

class Logger:
    def __init__(self, verbosity=0, quiet=False):
        self.verbosity = verbosity
        self.quiet = quiet

    def debug(self, message):
        if self.verbosity == 2:
            console.print("{}[DEBUG]{} {}".format("[yellow3]", "[/yellow3]", message), highlight=False)

    def verbose(self, message):
        if self.verbosity >= 1:
            console.print("{}[VERBOSE]{} {}".format("[blue]", "[/blue]", message), highlight=False)

    def info(self, message):
        if not self.quiet:
            console.print("{}[*]{} {}".format("[bold blue]", "[/bold blue]", message), highlight=False)

    def success(self, message):
        if not self.quiet:
            console.print("{}[+]{} {}".format("[bold green]", "[/bold green]", message), highlight=False)

    def warning(self, message):
        if not self.quiet:
            console.print("{}[-]{} {}".format("[bold orange3]", "[/bold orange3]", message), highlight=False)

    def error(self, message):
        if not self.quiet:
            console.print("{}[!]{} {}".format("[bold red]", "[/bold red]", message), highlight=False)


def file_reader(file_name):
    flist = []
    file = open(file_name,"r")
    file_in = file.readlines()
    for f in file_in:
        flist.append(f.replace("\n",""))
    return flist

def get_options():
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
    parser.add_argument(
        "-k",
        "--insecure",
        dest="verify",
        action="store_false",
        default=True,
        help="Allow insecure server connections when using SSL",
    )
    parser.add_argument(
        "-w",
        "--wordlist",
        dest="wordlist",
        action="store",
        default="http_verb_list",
        help="HTTP verbs wordlist",
    )
    options = parser.parse_args()
    return options


def main():
    logger.info("Starting HTTP verb enumerating and tampering")
    with open(options.wordlist, "r") as infile:
        methods = infile.read().split()
    results = {}
    logger.verbose("Pulling available methods with an OPTION request")
    r = requests.options(url=options.url, verify=options.verify)
    if r.status_code == 200:
        logger.verbose("URL accepts OPTIONS")
        if r.headers["Allow"]:
            logger.verbose("URL answers with a list of options")
            for method in r.headers["Allow"].replace(" ", "").split(","):
                if method not in methods:
                    logger.debug(f"Adding new method {method} to methods")
                    methods.append(method)
                else:
                    logger.debug(f"Method {method} already in known methods, passing")
        else:
            logger.verbose("URL doesn't answer with a list of options")
    else:
        logger.verbose("URL rejects OPTIONS")
    for method in track(methods):
        logger.debug(f"Requesting URL with method {method}")
        r = requests.request(method=method, url=options.url, verify=options.verify)
        logger.debug(f"Obtained results: {str(r.status_code)}, {r.reason}")
        # TODO : filter on status code to print results with color
        results[method] = {"status_code": str(r.status_code), "reason": r.reason[:100]}
    table = Table(show_header=True, header_style="bold blue", border_style="blue", box=box.SIMPLE)
    table.add_column("Method")
    table.add_column("Status code")
    table.add_column("Reason")
    for result in results.items():
        table.add_row(result[0], result[1]["status_code"], result[1]["reason"])
    console.log(table)


if __name__ == '__main__':
    try:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        options = get_options()
        logger = Logger(options.verbosity, options.quiet)
        console = Console()
        main()

    except KeyboardInterrupt:
        logger.info("Terminating script...")
        raise SystemExit
