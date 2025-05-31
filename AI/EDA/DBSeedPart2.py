# Imports 
import pandas as pd
import mariadb
import uuid
import json
import random
dataMerged = pd.read_excel('DATA_MERGED.xlsx')

db_config = {
    "user": "root",
    "password": "None58-DB",
    "host": "localhost",
    "port": 3306,
    "database": "SymbioDb"
}

# Check if 'user_Id' column exists in the DataFrame
if "user_Id" not in dataMerged.columns:
    try:
        # Connect to MariaDB
        conn = mariadb.connect(**db_config)
        cursor = conn.cursor()

        # Query to retrieve Id and email from aspnetusers
        query = "SELECT Id, email FROM aspnetusers"
        cursor.execute(query)

        # Fetch results and create a DataFrame
        aspnetusers_data = cursor.fetchall()
        aspnetusers_df = pd.DataFrame(aspnetusers_data, columns=["user_Id", "email"])


        # Merge aspnetusers DataFrame with dataMerged on the email column
        dataMerged = pd.merge(aspnetusers_df, dataMerged, on="email", how="left")

        print("user_Id column added successfully.")
    except mariadb.Error as e:
        print(f"Error: {e}")

    finally:
        if conn:
            cursor.close()
            conn.close()
else:
    print("The 'user_Id' column already exists in the DataFrame.")

    
dataMerged["Keywords"] = dataMerged["Keywords"].fillna("")
dataMergedWant = dataMerged[dataMerged["Resource Type"] == "Want"]


random.seed(42)

# dataMergedWant["CategoryList2"] = dataMerged[["Category 1", "Category 2", "Category 3"]].apply(lambda row: list(row), axis=1)
# dataMerged["CategoryList"] = dataMerged["CategoryList"].apply(json.dumps)


# Group by 'user_Id' and apply aggregation
grouped = dataMergedWant.groupby("user_Id").agg({
    "Category 1": lambda x: ", ".join(set(x)),  # Flatten and deduplicate, then CSV
    "Category 2": lambda x: ", ".join(set(x)),  # Flatten and deduplicate, then CSV
    "Category 3": lambda x: ", ".join(set(x)),  # Flatten and deduplicate, then CSV
    "Keywords": lambda x: ", ".join(set(x)),  # Flatten and deduplicate, then CSV
    "Unit of Measure": lambda x: ", ".join(set(x)),  # Flatten and deduplicate, then CSV
    "Supply Type": lambda x: ", ".join(set(x)),  # Deduplicate and convert to CSV
    "Available Quantity": ["min", "max"],  # Minimum and maximum quantity
    "Valid From": "min",  # Smallest date value
    "Valid To": "max",  # Largest date value
    "Site Name": "first",  # Use the first occurrence of the Site Name
}).reset_index()

# Flatten column names for "Available Quantity"
grouped.columns = ["_".join(col).strip("_") if isinstance(col, tuple) else col for col in grouped.columns]

# Rename columns for clarity
grouped.rename(columns={
    "Available Quantity_min": "Minimum Quantity",
    "Available Quantity_max": "Maximum Quantity",
    "Supply Type_<lambda>": "Supply Type",
    "Keywords_<lambda>": "Keywords",
    "CategoryList2_<lambda>": "CategoryList",
    "Valid From_min": "Valid From",
    "Valid To_max": "Valid To",
    "Site Name_first" : "Site Name",
    "Unit of Measure_<lambda>" : "Unit of Measure",
    "Category 1_<lambda>": "Category 1",
    "Category 2_<lambda>": "Category 2",
    "Category 3_<lambda>": "Category 3",

}, inplace=True)

grouped['Preference_Id'] = [str(uuid.uuid4()) for _ in range(len(grouped))]



# Sort by site name to ensure same value for max distance is given 
random.seed(42)
grouped = grouped.sort_values(by="Site Name")

grouped.head()

# Connect to MariaDB
try:
    conn = mariadb.connect(**db_config)
    cursor = conn.cursor()

    # SQL query for inserting data
    insert_query = """
    INSERT INTO userpreferences (Id, PreferredKeywords, MaxSearchRadiusKM, MinimumAvailableQuantity, MaximumAvailableQuantity, PreferredSupplyType, PreferredUnitOfMeasures, PreferredValidFrom, PreferredValidTo, UserId, PreferredCategories1, PreferredCategories2, PreferredCategories3)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    # Iterate through each row in the DataFrame
    for _, row in grouped.iterrows():

        # Execute the query with values
        cursor.execute(insert_query, (
            row["Preference_Id"],
            row["Keywords"],
            str(random.randint(10, 100)),
            row["Minimum Quantity"],
            row["Maximum Quantity"],
            row["Supply Type"],
            row["Unit of Measure"],
            row["Valid From"],
            row["Valid To"],
            row["user_Id"],
            row["Category 1"],
            row["Category 2"],
            row["Category 3"],




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