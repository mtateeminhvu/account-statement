from typing import List, Any

import PyPDF2
import csv
import re
from pathlib import Path

date_pattern = r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}'
page_number_pattern = r"Page (\d{1,5}) of (12028)"
#line_prefix = ['Ngày GD/', 'TNX Date', 'Số CT/ Doc NoSố tiền ghi nợ/', 'DebitSố tiền ghi có/', 'CreditSố dư/',
               #'BalanceNội dung chi tiết/', 'Transactions in detail']
line_prefix = ['STT', 'Ngày GD', 'Mô tả giao dịch', 'Số tiền', 'Tên đối ứng']



class Transaction:
    def __init__(self, date, transaction_id, transaction_amount, balance, message):
        self.date = date
        self.transaction_id = transaction_id
        self.transaction_amount = transaction_amount
        self.balance = balance
        self.message = message


transaction_objs = []


def read_data_file(csv_file):
    with open(csv_file, mode='r', newline='') as file:
        reader = csv.reader(file)
        # Skip the header
        next(reader)

        # Process each row in the CSV file
        for row in reader:
            transaction_objs.append(
                Transaction(row[0], row[1], row[2], row[3], row[4]))


def pdf_to_csv(pdf_file, csv_file):
    # Open the PDF file

    with open(pdf_file, 'rb') as file:
        reader = PyPDF2.PdfReader(file)

        # Open the CSV file for writing
        i = 0
        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            i = 0

            # Iterate through each page in the PDF
            for page in reader.pages:
                text = page.extract_text()

                # Split the text into lines
                lines = text.split('\n')

                # Process each line and write to CSV
                found_match = False
                collected = []

                # clear unnecessary data
                for line in lines:
                    if found_match or re.match(date_pattern, line.strip()):
                        collected.append(line.strip())
                        found_match = True
                    if re.search(page_number_pattern, line.strip()):
                        found_match = False

                # parse data to object
                transactions = split_transactions(collected)
                for transaction in transactions:
                    date = transaction[0]
                    if len(transaction[1].strip().split(' ')[0]) > 10:
                        transaction_id = transaction[1][:9]
                    else:
                        transaction_id = transaction[1][:10]
                    slices = transaction[1].replace(transaction_id, '').strip().split(' ')
                    transaction_amount = slices[0]
                    message: list[str] = [
                        transaction[1].replace(transaction_id, '').replace(transaction_amount, '').strip()]
                    transaction.pop(0)  # remove first item
                    transaction.pop(0)  # remove next item
                    transaction_obj = Transaction(date, transaction_id, transaction_amount, 0,
                                                  ' '.join(message + transaction).strip())
                    transaction_objs.append(transaction_obj)
                    if i == 0:
                        writer.writerow(transaction_obj.__dict__)
                        i = i + 1
                    writer.writerow(transaction_obj.__dict__.values())


def split_transactions(lst):
    result = []
    temp = []

    for item in lst:
        temp.append(item)
        if re.match(date_pattern, item):
            temp.pop()
            if temp:
                result.append(temp)
            temp = [item]

    if temp:  # Add the last sub-list if it exists
        result.append(temp)

    return result


def remove_using_pop(lst):
    for _ in range(len(line_prefix)):
        if lst:
            lst.pop(0)
    return lst


# Usage
file_path = Path('output.csv')
if not file_path.is_file():
    print("Data file not exists")
    pdf_to_csv('input.pdf', 'output.csv')
else:
    print("Data file exists")
    read_data_file('output.csv')
print("Loaded data file")
print(len(transaction_objs))
user_input = input("Please enter search word: ")
filtered_trxns = [trxn for trxn in transaction_objs if
                  user_input in str(trxn.transaction_amount).replace('.', '') or user_input in str(trxn.message)]
print(len(filtered_trxns))
for trxn in filtered_trxns:
    print(trxn.__dict__)
