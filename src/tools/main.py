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

    for index, row in transactions.iterrows():
        if pd.isna(row['category']):
            description = TransactionProcessor.process_description(str(row['description']))
            category = category_manager.get_category_for_description(description)
            transactions.at[index, 'category'] = category

    database_manager.save_transactions(transactions)
    database_manager.save_category_associations(category_manager.categories)

def export_transactions(database_manager):
    transactions = database_manager.load_transactions()
    if transactions['category'].isnull().any():
        raise ValueError("Some transactions are not categorized. Please categorize all transactions before exporting.")

    # Optionally, here you can add more processing before exporting
    database_manager.save_transactions(transactions)


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
    print("1: Add new transactions")
    print("2: Categorize transactions")
    print("3: Export transactions")
    choice = input("Enter your choice: ")

    if choice == '1':
        file_path = input("Enter the path to the Excel file: ")
        add_new_transactions(database_manager, file_path)
    elif choice == '2':
        categorize_transactions(database_manager)
    elif choice == '3':
        export_transactions(database_manager)
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
