import logging
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3


def log_progress(message):
    logging.basicConfig(
        filename="code_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s"
    )
    logging.info(message)


# log_progress("test numero 1")


# Task 2: Extraction of data
def extract():
    url = "https://web.archive.org/web/20230908091635/https://en.wikipedia.org/wiki/List_of_largest_banks"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Locate the table
    table = soup.find_all("table", {"class": "wikitable"})[0]
    rows = table.find_all("tr")

    data = []
    for row in rows[1:11]:  # Limit to top 10 rows
        cols = row.find_all("td")
        name = cols[1].text.strip()
        market_cap = float(
            cols[2]
            .text.strip()
            .replace("\n", "")
            .replace("$", "")
            .replace("B", "")
            .replace(",", "")
        )
        data.append([name, market_cap])

    df = pd.DataFrame(data, columns=["Name", "MC_USD_Billion"])
    log_progress("Data extraction complete.")
    return df


# Test the extraction function
df = extract()
print(df)


# Task 3: Transformation of data
def transform(df):
    exchange_rates = pd.read_csv(
        "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMSkillsNetwork-PY0221EN-Coursera/labs/v2/exchange_rate.csv"
    )

    df["MC_GBP_Billion"] = (
        df["MC_USD_Billion"]
        * exchange_rates.loc[exchange_rates["Currency"] == "GBP", "Rate"].values[0]
    )
    df["MC_EUR_Billion"] = (
        df["MC_USD_Billion"]
        * exchange_rates.loc[exchange_rates["Currency"] == "EUR", "Rate"].values[0]
    )
    df["MC_INR_Billion"] = (
        df["MC_USD_Billion"]
        * exchange_rates.loc[exchange_rates["Currency"] == "INR", "Rate"].values[0]
    )

    df = df.round(2)
    log_progress("Data transformation complete.")
    return df


# Test the transformation
df_transformed = transform(df)
print(df_transformed)


# Task 4: Loading to CSV
def load_to_csv(df):
    df.to_csv("./Largest_banks_data.csv", index=False)
    log_progress("Data loaded into CSV.")


# Test loading to CSV
load_to_csv(df_transformed)


# Task 5: Loading to Database
def load_to_db(df):
    conn = sqlite3.connect("Banks.db")
    df.to_sql("Largest_banks", conn, if_exists="replace", index=False)
    conn.close()
    log_progress("Data loaded into the database.")


# Test loading to the database
load_to_db(df_transformed)

# Task 6: Run SQL queries


# Task 6: Run SQL queries


def run_queries():
    conn = sqlite3.connect("Banks.db")

    query_select_all = "SELECT * FROM Largest_banks"
    all_data = pd.read_sql(query_select_all, conn)

    query_avg = "SELECT AVG(MC_GBP_Billion) FROM Largest_banks"
    bank_avg = pd.read_sql(query_avg, conn)

    query_limit = "SELECT Name from Largest_banks LIMIT 5"
    bank_limit = pd.read_sql(query_limit, conn)

    conn.close()
    log_progress("Query execution complete.")

    return all_data, bank_avg, bank_limit


# Test SQL query execution
all_data, bank_avg, bank_limit = run_queries()

print("\nAll Data from Largest_banks:")
print(all_data)
print("\Average Market Cap of Banks:")
print(bank_avg)
print("5 first Banks:")
print(bank_limit)
