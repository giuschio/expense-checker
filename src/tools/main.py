import matplotlib.pyplot as plt
import os

from expense_checker.tools import *

def add_new_transactions(database_manager, file_path):
    file_reader = ExcelFileReader(file_path)
    new_transactions = file_reader.read_and_filter_data()
    existing_transactions = database_manager.load_transactions()
    combined_transactions = pd.concat([existing_transactions, new_transactions], ignore_index=True)
    database_manager.save_transactions(combined_transactions)


def categorize_transactions(database_manager):
    transactions = database_manager.load_transactions()
    categories = database_manager.load_category_associations()
    category_manager = CategoryManager(categories)

    try:
        for index, row in transactions.iterrows():
            if pd.isna(row['category']):
                description = TransactionProcessor.process_description(str(row['description']))
                category = category_manager.get_category_for_description(description)
                transactions.at[index, 'category'] = category
                database_manager.save_category_associations(category_manager.description_to_category)
    except KeyboardInterrupt as e:
        print("shutting down...")


def get_categorized_transactions(database_manager):
    transactions = database_manager.load_transactions()
    categories = database_manager.load_category_associations()
    category_manager = CategoryManager(categories)

    transactions_with_categories = transactions[['date', 'description', 'amount']].copy()

    def categorize(description):
        desc = TransactionProcessor.process_description(str(description))
        return category_manager.get_category_for_description(desc)

    transactions_with_categories['categories'] = transactions_with_categories['description'].apply(categorize)

    # Convert 'date' to datetime and extract the year and month
    transactions_with_categories['date'] = pd.to_datetime(transactions_with_categories['date'])
    transactions_with_categories['year_month'] = transactions_with_categories['date'].dt.to_period('M')

   # Group by 'year_month' and 'categories', and sum only the 'amount' column
    monthly_expenses = transactions_with_categories.groupby(['year_month', 'categories'])['amount'].sum().reset_index()
    return monthly_expenses



def export_transactions(database_manager, file_path):
    monthly_expenses = get_categorized_transactions(database_manager)
    monthly_expenses.to_excel(file_path, index=False)


def visualize(database_manager):
    df = get_categorized_transactions(database_manager)
    df['amount'] = df['amount'] * -1

    # Create pivot table
    pivot_df = df.pivot_table(index='year_month', columns='categories', values='amount', fill_value=0)

    # Calculate average expenses for each category and sort columns based on this
    average_expenses = pivot_df.mean().sort_values(ascending=False)
    pivot_df = pivot_df[average_expenses.index]

    # Add 'average' as a new row in the pivot table
    pivot_df.loc['Average'] = average_expenses

    # Plot a stacked bar chart
    pivot_df.plot(kind='bar', stacked=True, figsize=(10, 7))

    plt.title('Monthly Expenses by Category')
    plt.xlabel('Month')
    plt.ylabel('Amount')
    plt.legend(title='Category')
    plt.show()


def main():
    folder_path = input("Enter the path to the database folder: ")

    if not os.path.exists(folder_path):
        create_folder = input(f"The folder '{folder_path}' does not exist. Create it? (y/n): ")
        if create_folder.lower() == 'y':
            os.makedirs(folder_path)
        else:
            print("Operation cancelled.")
            return

    database_manager = DatabaseManager(folder_path)

    print("Select an option:")
    print("1: Add new expenses")
    print("2: Categorize expenses")
    print("3: Export expenses")
    print("4: Visualize expenses")
    choice = input("Enter your choice: ")

    if choice == '1':
        file_path = input("Enter the path to the Excel file: ")
        add_new_transactions(database_manager, file_path)
    elif choice == '2':
        categorize_transactions(database_manager)
    elif choice == '3':
        file_path = input("Enter the path to the csv file: ")
        export_transactions(database_manager, file_path)
    elif choice == '4':
        visualize(database_manager)
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
