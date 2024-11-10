from typing import List
import csv
import re
from collections import defaultdict

# Định nghĩa lớp giao dịch

class Transaction:
    def __init__(self, date, transaction_id, transaction_amount, balance, message, counterpart):
        try:
            self.transaction_amount = float(transaction_amount.replace(',', '').replace('.', '')) if transaction_amount else 0
        except ValueError:
            # Bỏ qua các dòng không hợp lệ mà không in ra màn hình
            self.transaction_amount = 0

        self.date = date
        self.transaction_id = transaction_id
        self.balance = balance
        self.message = message
        self.counterpart = counterpart





# Đọc dữ liệu từ file CSV và lưu vào danh sách giao dịch
def read_data_file(csv_file):
    transaction_objs = []
    with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Bỏ qua dòng tiêu đề
        for row in reader:
            if len(row) >= 5:
                transaction = Transaction(row[0], row[1], row[2], row[3], row[4], row[4])
                transaction_objs.append(transaction)
    return transaction_objs

# Tính tổng số tiền ủng hộ theo từng người
def find_top_donor(transactions: List[Transaction]):
    donation_summary = defaultdict(float)

    for transaction in transactions:
        if transaction.counterpart:
            donation_summary[transaction.counterpart] += transaction.transaction_amount

    # Tìm người ủng hộ nhiều nhất
    top_donor = max(donation_summary.items(), key=lambda x: x[1])
    return top_donor

# Đường dẫn file CSV
csv_file_path = 'output.csv'

# Đọc dữ liệu từ CSV và tìm người ủng hộ nhiều nhất
transactions = read_data_file(csv_file_path)
top_donor = find_top_donor(transactions)

# Hiển thị kết quả
if top_donor:
    print(f"Người ủng hộ nhiều nhất là: {top_donor[0]} với tổng số tiền ủng hộ: {top_donor[1]:,.2f} VND")
else:
    print("Không có dữ liệu giao dịch.")
