#!/usr/bin/env python3

import sqlite3
import pandas as pd
import getopt
import sys
import re


def create(db_name):
    dbh = db_connect(db_name)
    dbh.execute('CREATE TABLE category (item text, category text, level int)')
    dbh.close()


def import_categories(db_name, file_name):
    categories = read(db_name)
    data = pd.read_csv(file_name)
    new_records = []
    for i, item in enumerate(data['Item']):
        if item == item and re.match('^[a-z]+', item, re.I):
            category = data['Categories'][i]
            if category == category and re.match('^[a-z]+', category, re.I):
                if item not in categories:
                    new_records.append([item, category, 1])
    if len(new_records) > 0:
        add_categories(db_name, new_records)


def add_categories(db_name, records):
    dbh = db_connect(db_name)
    cursor = dbh.cursor()
    sql = 'INSERT INTO category ("item", "category", "level") VALUES (?, ?, ?)'
    for record in records:
        cursor.execute(sql, record)
    dbh.commit()
    dbh.close()

def read(db_name, item_list=None):
    dbh = db_connect(db_name)
    cursor = dbh.cursor()
    if item_list is None:
        query = "SELECT * FROM category"
        cursor.execute(query)
    else:
        query = f"SELECT * FROM category WHERE item IN ({','.join(['?']*len(item_list))})"
        cursor.execute(query, item_list)
    df = pd.DataFrame(cursor.fetchall(), columns=['item', 'category', 'level'])
    category_index = {}
    for i, item in enumerate(df['item'].values):
        category_index[item] = df['category'][i]

    return category_index


def db_connect(db_name):
    dbh = sqlite3.connect(db_name)

    return dbh


db = 'categories.db'
file = 'item-cat.csv'
op = None

options, remainder = getopt.getopt(sys.argv[1:], 'cid:f:')
for opt, arg in options:
    if opt in '-c':
        op = 'create'
    elif opt in '-i':
        op = 'import'
    elif opt in '-d':
        db = arg
    elif opt in '-f':
        file = arg

if op == 'create':
    create(db)
elif op == 'import':
    import_categories(db, file)
