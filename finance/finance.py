import sqlite3
import pandas as pd
from finance.data import FinanceData
from datetime import date
from dateutil.relativedelta import relativedelta


class Finance:
    categories_db = 'categories.db'
    from_day = 20
    balance = 0
    data = None
    start_date = None
    end_date = None
    today = date.today()
    days_passed = None
    report = None

    def __init__(self, config):

        start_date = config['start_date']
        end_date = config['end_date']
        balance = config['balance']
        data = config['data']
        file = config['file']

        self.start_date = start_date
        self.end_date = end_date

        if self.start_date is None:
            month = self.today.month if self.today.day >= self.from_day else self.today.month - 1
            self.start_date = date(self.today.year, month, self.from_day)

        if self.end_date is None:
            self.end_date = self.start_date + relativedelta(months=1) - relativedelta(days=1)

        self.days_passed = self.today - self.start_date if \
            self.today < self.end_date else \
            self.end_date - self.start_date

        if balance is not None:
            self.balance = balance

        if data is not None:
            self.data = data

        if file is not None:
            self.data = FinanceData(file)

        if self.data is not None:
            self.data \
                .categorise_items(self.get_categories()) \
                .save_expenses()

    def get_categories(self):
        items = self.data.filtered['Item']
        dbh = sqlite3.connect(self.categories_db)
        cursor = dbh.cursor()
        query = f"SELECT item, category FROM category WHERE item IN ({','.join(['?']*len(items))})"
        cursor.execute(query, items)

        return cursor.fetchall()

    def get_days_passed(self):
        return self.days_passed.days

    def set_data(self, data):
        self.data = data

    def get_data(self):
        return self.data

    def get_expenses(self):
        return self.data.get_expenses()

    def get_uncategorised(self):
        return self.data.get_uncategorised()

    def get_daily_expenses(self):
        return pd \
            .DataFrame({'count': self.data.get_expenses().groupby(['Date'])['Debit'].sum()}) \
            .reset_index()

    def get_category_expenses(self):
        return pd \
            .DataFrame({'Total': self.data.get_expenses().groupby(['Category'])['Debit'].sum()}) \
            .reset_index()

    def get_summary(self):
        total = round(float(self.data.get_expenses()['Debit'].sum()), 2)
        total_percentage = round(total / self.balance * 100)
        overdraft = round(self.balance - total, 2)
        percentage = round(overdraft / self.balance * 100, 2)
        days_percentage = round((self.today - self.start_date) / (self.end_date - self.start_date) * 100)

        return pd.DataFrame({
            'Days': [
                self.get_days_passed(),
                str(days_percentage) + '%'
            ],
            'Expenses': [
                total, str(total_percentage) + '%'
            ],
            'Overdraft': [
                overdraft if overdraft < 0 else 0,
                str(abs(percentage) if overdraft < 0 else 0) + '%'
            ],
            'Balance': [
                overdraft if overdraft > 0 else 0,
                str(percentage if overdraft > 0 else 0) + '%'
            ]
        })

    def generate_report(self):
        self.report = {
            'Period': {'from': self.start_date, 'to': self.end_date},
            'Expenses': self.get_expenses(),
            'Uncategorised': self.get_uncategorised(),
            'Debit': self.get_daily_expenses(),
            'Category_expenses': self.get_category_expenses(),
            'Summary': self.get_summary()
        }

        return self.report

