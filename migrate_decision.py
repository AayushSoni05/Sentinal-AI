import sqlite3


DATABASE = "sentinel.db"


connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()


cursor.execute("PRAGMA table_info(investigation_decisions)")

table_exists = cursor.fetchall()


if not table_exists:

    cursor.execute(
        """
        CREATE TABLE investigation_decisions (
            id TEXT PRIMARY KEY,
            investigation_id TEXT NOT NULL UNIQUE,
            recommendation TEXT NOT NULL,
            analyst_decision TEXT,
            approval_status TEXT NOT NULL DEFAULT 'Pending',
            approver_decision TEXT,
            reason TEXT,
            created_at DATETIME,
            FOREIGN KEY (investigation_id)
                REFERENCES investigations(id)
        )
        """
    )

    print(
        "investigation_decisions table created successfully."
    )

else:

    print(
        "investigation_decisions table already exists."
    )


connection.commit()
connection.close()

print("Decision database migration completed.")