# Imports 
import pandas as pd
import mariadb
import uuid
import json

# Importing Excel
data = pd.read_excel('EDA\RESOURCES.xlsx')
data2 = pd.read_excel('EDA\SITES.xlsx')
dataMerged = merged_df = pd.merge(data, data2, on="Site Name", how="left", suffixes=("_RESOURCES", "_SITES"))
dataMerged["email"] = dataMerged["Site Name"].str.replace(" ", "").str.lower() + "@voorbeeld.nl"
dataMerged["Unit of Measure"] = dataMerged["Unit of Measure"].str.replace(" ", "")
dataMerged["Unit of Measure"] = dataMerged["Unit of Measure"].str.replace("Money(€)", "MoneyEUR")
dataMerged["Unit of Measure"].unique()
dataMerged = dataMerged.drop_duplicates(subset=['Site Name'])


# Inserting Locations
# Filtering out unneeded columns
# location = dataMerged[["Street and Number_SITES", "Postal Code_SITES", "Latitude", "Longitude", "Site Name", "City_SITES"]]
dataMerged['Location_Id'] = [str(uuid.uuid4()) for _ in range(len(dataMerged))]
dataMerged = dataMerged.rename(columns={"Street and Number_SITES": "Address"})

# Display the filtered DataFrame
print(dataMerged)

# Database connection details
db_config = {
    "user": "root",
    "password": "None58-DB",
    "host": "localhost",
    "port": 3306,
    "database": "SymbioDb"
}

# Connect to MariaDB
try:
    conn = mariadb.connect(**db_config)
    cursor = conn.cursor()

    # SQL query for inserting data
    insert_query = """
    INSERT INTO locations (Id, Address, PostalCode, Latitude, Longitude, City, Country)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    # Iterate through each row in the DataFrame
    for _, row in dataMerged.iterrows():

        # Execute the query with values
        cursor.execute(insert_query, (
            row["Location_Id"],
            row["Address"],
            row["Postal Code_SITES"],
            row["Latitude"],
            row["Longitude"],
            row["City_SITES"],
            'Netherlands'
        ))

    # Commit the transaction
    conn.commit()
    print(f"{cursor.rowcount} rows inserted successfully.")

except mariadb.Error as e:
    print(f"Error: {e}")

finally:
    # Close the connection
    if conn:
        cursor.close()
        conn.close()


dataMerged['Company_Id'] = [str(uuid.uuid4()) for _ in range(len(dataMerged))]
dataMerged['Description_SITES'] = dataMerged['Description_SITES'].fillna("No Description")
# companies = dataMerged[['Company_Id', 'Site Name', 'Description_SITES', 'NACE Code', 'email', 'Location_Id']]

# Inserting companies

# Connect to MariaDB
try:
    conn = mariadb.connect(**db_config)
    cursor = conn.cursor()

    # SQL query for inserting data
    insert_query = """
    INSERT INTO companies (Id, Name, Description, NaceCode, Email, Phonenumber, LocationId)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    # Iterate through each row in the DataFrame
    for _, row in dataMerged.iterrows():

        # Execute the query with values
        cursor.execute(insert_query, (
            row["Company_Id"],
            row["Site Name"],
            row["Description_SITES"],
            row["NACE Code"],
            row["email"],
            "0612345678",
            row["Location_Id"],
        ))

    # Commit the transaction
    conn.commit()
    print(f"{cursor.rowcount} rows inserted successfully.")

except mariadb.Error as e:
    print(f"Error: {e}")

finally:
    # Close the connection
    if conn:
        cursor.close()
        conn.close()

# Inserting Products

dataMerged[["Category 1", "Category 2", "Category 3"]] = dataMerged[["Category 1", "Category 2", "Category 3"]].replace({"": "Unkwnown", None: "Unkwnown", " ": "Unkwnown"})
# For Category 2: Remove only the first number and the following whitespace
dataMerged["Category 2"] = dataMerged["Category 2"].str.replace(r"^\d+\s+", "", regex=True)
# For Category 3: Remove only the first two numbers and the following whitespace
dataMerged["Category 3"] = dataMerged["Category 3"].str.replace(r"^\d+\s+\d+\s+", "", regex=True)


dataMerged['Product_Id'] = [str(uuid.uuid4()) for _ in range(len(dataMerged))]
dataMerged["Valid From"] = pd.to_datetime(dataMerged["Valid From"]).dt.strftime("%Y-%m-%d")
dataMerged["Valid To"] = pd.to_datetime(dataMerged["Valid To"]).dt.strftime("%Y-%m-%d")
dataMerged["Create Date"] = pd.to_datetime(dataMerged["Create Date"]).dt.strftime("%Y-%m-%d")
dataMerged['Description_RESOURCES'] = dataMerged['Description_RESOURCES'].fillna("No Description")
# dataMerged = dataMerged.dropna(subset=['Description_RESOURCES'])
dataMerged["CategoryList"] = dataMerged[["Category 1", "Category 2", "Category 3"]].apply(lambda row: list(row), axis=1)
dataMerged["CategoryList"] = dataMerged["CategoryList"].apply(json.dumps)
dataMergedHave = dataMerged[dataMerged["Resource Type"] == "Have"]
# Connect to MariaDB
try:
    conn = mariadb.connect(**db_config)
    cursor = conn.cursor()

    # SQL query for inserting data
    insert_query = """
    INSERT INTO products (Id, Name, Description, SupplyType, Categories, ValidFrom, ValidTo, CreatedOn, CompanyId, BundleId, IsBundled, BundlingAllowed)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    # Iterate through each row in the DataFrame
    for _, row in dataMergedHave.iterrows():

        # Execute the query with values
        cursor.execute(insert_query, (
            row["Product_Id"],
            row["Resource Name"],
            row["Description_RESOURCES"],
            row["Supply Type"],
            row["CategoryList"],
            row["Valid From"],
            row["Valid To"],
            row["Create Date"],
            row["Company_Id"],
            None,
            False,
            True
        ))

    # Commit the transaction
    conn.commit()
    print(f"{cursor.rowcount} rows inserted successfully.")

except mariadb.Error as e:
    print(f"Error: {e}")

finally:
    # Close the connection
    if conn:
        cursor.close()
        conn.close()


# Inserting materials

dataMergedHave['Material_Id'] = [str(uuid.uuid4()) for _ in range(len(dataMergedHave))]

# Connect to MariaDB
try:
    conn = mariadb.connect(**db_config)
    cursor = conn.cursor()

    # SQL query for inserting data
    insert_query = """
    INSERT INTO materials (Id, Name, Description, AvailableQuantity, UnitOfMeasure, ProductId)
    VALUES (?, ?, ?, ?, ?, ?)
    """

    # Iterate through each row in the DataFrame
    for _, row in dataMergedHave.iterrows():

        # Execute the query with values
        cursor.execute(insert_query, (
            row["Material_Id"],
            row["Resource Name"],
            row["Description_RESOURCES"],
            row["Available Quantity"],
            row["Unit of Measure"],
            row["Product_Id"],
        ))

    # Commit the transaction
    conn.commit()
    print(f"{cursor.rowcount} rows inserted successfully.")

except mariadb.Error as e:
    print(f"Error: {e}")

finally:
    # Close the connection
    if conn:
        cursor.close()
        conn.close()

# Exporting to new excel sheet to use in part 2
dataMerged.to_excel('DATA_MERGED.xlsx', index=False)
