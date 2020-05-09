import pandas as pd
import os.path
import re


class FinanceData:
    file = 'data.csv'
    file_path = ''
    file_name = None
    filtered = None
    expenses = None

    def __init__(self, file=None):
        self.file = file
        self.file_path = os.path.dirname(file)
        self.file_name = os.path.basename(file)
        self.read_file()

    def read_file(self):
        data = pd.read_csv(self.file)

        filtered = {'Date': [], 'Item': [], 'Debit': [], 'Credit': [], 'Category': []}
        for i, detail in enumerate(data['Details']):
            item = data['Type'][i] if detail != detail else detail
            item = data['Code'][i] \
                if re.match('[0-9]{4}-', item) or re.match('[0-9]{2}-', item) \
                else item
            filtered['Date'].append(pd.to_datetime(data['Date'][i], format='%d/%m/%Y'))
            filtered['Item'].append(item)
            filtered['Category'].append('')
            if data['Amount'][i] < 0:
                filtered['Debit'].append(abs(data['Amount'][i]))
                filtered['Credit'].append(0)
            else:
                filtered['Debit'].append(0)
                filtered['Credit'].append(data['Amount'][i])
        self.filtered = filtered

        return self

    def categorise_items(self, categories=None):
        category_index = {}
        for category in categories:
            category_index[category[0]] = category[1]
        for i, item in enumerate(self.filtered['Item']):
            if item in category_index:
                self.filtered['Category'][i] = category_index[item]

        return self

    def get_uncategorised(self):
        return self.expenses[self.expenses.Category == '']['Item'].unique()

    def get_data(self):
        return self.filtered

    def get_items(self):
        return self.filtered['Item']

    def save_expenses(self):
        self.expenses = pd.DataFrame(data=self.filtered)
        self.expenses \
            .sort_values(by='Date', ascending=True) \
            .to_csv(self.file_path + '/filtered-' + self.file_name,
                    date_format='%m/%d/%Y',
                    index=False,
                    columns=['Date', 'Item', 'Debit', 'Credit'])

        return self

    def get_expenses(self):
        return self.expenses
