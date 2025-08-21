# 💰 Simple Finance Dashboard

A simple finance tracking dashboard built with **Streamlit**, **Pandas**, and **Plotly**.  
This app lets you upload a CSV of your transactions (it works for my Wells Fargo CSV, I am unsure about other banks), 
categorize them, and visualize your spending with interactive charts.

## 🚀 Features
- Upload a CSV file of your bank transactions.
- Automatically parses dates, amounts, and details.
- Add custom categories to organize your expenses.
- View:
  - Raw debit and credit transactions
  - Interactive **pie chart** of spending by category
  - Positive expense values for easy readability

## 📂 CSV Format
Your CSV file should look like this:

```csv
Date,Amount,Debit/Credit,Blank,Details
"08/18/2025","-4.24","*","","WEGMANS"
"08/17/2025","-33.07","*","","MARUFUJI"
"08/15/2025","-16.41","*","","DOMINO'S"
