#!/usr/bin/env python

import json
import csv
import argparse
from datetime import datetime
import calendar
import sys

title = "\nADExplorerDump.py v0.1\n"

def get_json_data(filename):
    with open(filename) as f:
        data = json.load(f)
    
    return data

def long_standing_accounts(data, max_password_age):
    now = calendar.timegm(datetime.utcnow().utctimetuple())
    cutoff = now - (max_password_age*60*60*24)

    accounts = []

    for account in data['data']:
        if "pwdlastset" in account["Properties"]:
            if account["Properties"]["pwdlastset"] < cutoff and account["Properties"]["pwdlastset"] != 0:
                last_changed = datetime.fromtimestamp(account["Properties"]["pwdlastset"]).strftime("%d/%m/%Y, %H:%M:%S")
                accounts.append([account["Properties"]["name"], last_changed])

    return accounts

def output_data(outputs, args):
    if args.format == "txt":
        print_outputs(outputs, args.outfile)
    elif args.format == "csv":
        csv_output(outputs, args.outfile)

def print_outputs(outputs, filename):
    if filename == "-":
        f = sys.stdout
    else:
        f = open(filename, "w")

    if "longstanding" in outputs:
        max_width = max([len(x[0]) for x in outputs["longstanding"]])
        table_width = max_width + 27
        print("-"*table_width, file=f)
        print("| {:<{max_width}} | {:<20} |".format("User", "Password Last Set", max_width=max_width), file=f)
        print("-"*table_width, file=f)
        for line in outputs["longstanding"]:
            print("| {:<{max_width}} | {:<20} |".format(*line, max_width=max_width), file=f)
            print("-"*table_width, file=f)

    if not filename == "-":
        f.close()

def csv_output(outputs, filename):
    with open(filename,"w", newline="") as f:
        if "longstanding" in outputs:
            header_row = ["User","Password Last Set"]
            rows = outputs["longstanding"]
        
        writer = csv.writer(f)
        writer.writerow(header_row)
        writer.writerows(rows)


def get_args():
    parser = argparse.ArgumentParser(
        prog="ADExplorerDump.py",
        description="Dumps selected data from ADExplorerSnapshot.py JSON output"
    )

    parser.add_argument("filename")
    mut_group = parser.add_mutually_exclusive_group(required=True)
    mut_group.add_argument("-S","--description-search", help="search principal description fields for the text provided", dest="description")
    mut_group.add_argument("-L", "--long-standing-accounts", action="store_true", dest="long_standing_accounts", help="Look for long standing accounts without recent password changes")
    parser.add_argument("--max-password-age", help="The maximum password age (in days) for determining long standing accounts, default: 365", default=365, dest="max_password_age", type=int)
    parser.add_argument("-O", "--outfile", help="File to output to", default="-")
    parser.add_argument("-F", "--format", help="Output file format, default: txt", default="txt", choices=["txt", "csv"])
    
    return parser.parse_args()

if __name__ == "__main__":

    print(title)

    args = get_args()

    data = get_json_data(args.filename)

    outputs = {}

    if args.long_standing_accounts:
        print("[+] Checking for long standing accounts without recent password changes...\n")
        outputs["longstanding"] = long_standing_accounts(data, args.max_password_age)

    output_data(outputs,args)
