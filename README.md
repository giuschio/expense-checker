# Expense-Checker
I was bored on a Sunday and my online banking doesn't let me easily categorize expenses. So I wrote this.

## Features

- **Import Expenses**: Load data from Excel files (assumes three columns: 'date', 'description', 'amount').
- **Categorize Expenses**: Assign categories to each transaction.
- **Export Expenses**: Export categorized expenses in xlsx format.
- **Visualization**: Generate a stacked bar chart to visualize expenses per category over time.

## Usage
1. Clone the repository:
   ```sh
   git clone https://github.com/giuschio/expense-checker.git
   ```
2. Navigate to the project directory and install
   ```sh
   cd expense-checker
   python3 -m pip install -e .
   ```
3. Run with:
   ```sh
   python3 src/tools/main.py
   ```