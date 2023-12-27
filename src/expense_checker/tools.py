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
    def __init__(self, description_to_category=None):
        # categories is a dictionary of description -> category
        if description_to_category is not None:
            unique_categories = list(set([category for category in description_to_category.values()]))
            self.categories = {str(idx): cat for idx, cat in enumerate(unique_categories)}
            self.description_to_category = description_to_category
        else:
            self.categories = {}
            self.description_to_category = {}

    def get_category_for_description(self, description):
        if description not in self.description_to_category:
            self.query_user_for_category(description)
        return self.description_to_category[description]

    def query_user_for_category(self, description):
        while True:
            print("\nCategories:")
            print("n: Create New Category")
            for idx, value in self.categories.items():
                print(f"{idx}: {value}")
            print("Ctrl + C to exit")
            choice = input(f"Assign a category for '{description}': ")

            if choice == 'n':
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
            pd.DataFrame(columns=['date', 'description', 'amount']).to_csv(self.csv_file_path, index=False)
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
                categories_to_descriptions = json.load(file)

            descriptions_to_categories = {}
            for cat, descriptions in categories_to_descriptions.items():
                for description in descriptions:
                    descriptions_to_categories[description] = cat
            return descriptions_to_categories
        except FileNotFoundError:
            return {}

    def save_category_associations(self, description_to_category):
        category_to_descriptions = {}
        for description, cat in description_to_category.items():
            if cat not in category_to_descriptions:
                category_to_descriptions[cat] = [description]
            else:
                category_to_descriptions[cat].append(description)

        with open(self.json_file_path, 'w') as file:
            json.dump(category_to_descriptions, file, indent=4)