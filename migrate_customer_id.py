import sqlite3


DATABASE = "sentinel.db"


connection = sqlite3.connect(DATABASE)

cursor = connection.cursor()


# Check existing columns
cursor.execute("PRAGMA table_info(investigations)")

columns = cursor.fetchall()

column_names = [column[1] for column in columns]


# Add customer_id only if it does not already exist
if "customer_id" not in column_names:

    cursor.execute(
        """
        ALTER TABLE investigations
        ADD COLUMN customer_id TEXT
        """
    )

    print("customer_id column added successfully.")

else:

    print("customer_id column already exists.")


connection.commit()

connection.close()

print("Database migration completed.")