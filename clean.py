#!/usr/bin/env python3

import getopt
import os.path
import sys
from datetime import datetime
from finance.finance import Finance


def print_report(report):

    print('<< PERIOD >>\n')
    print('%s - %s\n' % (report['Period']['from'], report['Period']['to']))

    print('<< EXPENSES >>\n')
    print(report['Expenses'].to_string(index=False))
    print()

    if len(report['Uncategorised']) > 0:
        print('<< UNCATEGORISED >>\n')
        for item in report['Uncategorised']:
            print(item)
        print()

    print('<< DAILY EXPENSES >>\n')
    print(report['Debit'].to_string(index=False))
    print()

    print('<< CATEGORICAL EXPENSES >>\n')
    print(report['Category_expenses'].to_string(index=False))
    print()

    print('<< SUMMARY >>\n')
    print(report['Summary'].to_string(index=False))


config = {
    'file': 'data.csv',
    'data': None,
    'balance': 0,
    'start_date': None,
    'end_date': None
}

options, remainder = getopt.getopt(sys.argv[1:], 'b:d:s:e:')
for opt, arg in options:
    if opt in '-b':
        config['balance'] = float(arg)
    elif opt in '-d':
        config['file'] = os.path.realpath(arg)
    elif opt in '-s':
        config['start_date'] = datetime.strptime(arg, '%Y/%m/%d')
    elif opt in '-e':
        config['end_date'] = datetime.strptime(arg, '%Y/%m/%d')

print_report(Finance(config).generate_report())

