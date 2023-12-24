import os
import json
import pandas as pd

class ExcelFileReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_and_filter_data(self):
        df = pd.read_excel(self.file_path)
        # Remove commas from the description
        df['description'] = df['description'].astype(str).str.replace(',', '')
        # Filter out rows with missing amounts
        return df.dropna(subset=['amount'])



class CategoryManager:
    def __init__(self):
        self.categories = {}
        self.description_to_category = {}

    def get_category_for_description(self, description):
        if description not in self.description_to_category:
            self.query_user_for_category(description)
        return self.description_to_category[description]

    def query_user_for_category(self, description):
        while True:
            print("\nCategories:")
            print("0: Create New Category")
            for key, value in self.categories.items():
                print(f"{key}: {value}")
            choice = input(f"Assign a category for '{description}': ")

            if choice == '0':
                new_category = input("Enter new category name: ")
                if not self.categories:
                    new_key = '1'
                else:
                    new_key = str(max(map(int, self.categories.keys())) + 1)
                self.categories[new_key] = new_category
                self.description_to_category[description] = new_category
            elif choice in self.categories:
                self.description_to_category[description] = self.categories[choice]
            else:
                print("Invalid choice. Please try again.")
                continue
            break



class TransactionProcessor:
    def __init__(self, file_reader, category_manager):
        self.file_reader = file_reader
        self.category_manager = category_manager

    def process_transactions(self):
        data = self.file_reader.read_and_filter_data()
        data['category'] = None
        for index, row in data.iterrows():
            description = self.process_description(str(row['description']))
            category = self.category_manager.get_category_for_description(description)
            data.at[index, 'category'] = category
        return data

    @staticmethod
    def process_description(description):
        words = description.split()
        processed_description = ''
        for word in words:
            if len(processed_description + word) >= 15 and len(processed_description.split()) >= 2:
                break
            processed_description += (word + ' ')
        return processed_description.strip() or description



class CSVExporter:
    @staticmethod
    def export_to_csv(data, file_name):
        data.to_csv(file_name, index=False)


class DatabaseManager:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.csv_file_path = os.path.join(folder_path, 'transactions.csv')
        self.json_file_path = os.path.join(folder_path, 'categories.json')
        self.initialize_database()

    def initialize_database(self):
        if not os.path.exists(self.csv_file_path):
            pd.DataFrame(columns=['date', 'description', 'amount', 'category']).to_csv(self.csv_file_path, index=False)
        if not os.path.exists(self.json_file_path):
            with open(self.json_file_path, 'w') as file:
                json.dump({}, file)

    def load_transactions(self):
        return pd.read_csv(self.csv_file_path)

    def save_transactions(self, df):
        df.to_csv(self.csv_file_path, index=False)

    def load_category_associations(self):
        try:
            with open(self.json_file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def save_category_associations(self, associations):
        with open(self.json_file_path, 'w') as file:
            json.dump(associations, file, indent=4)