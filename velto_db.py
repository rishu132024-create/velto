import sqlite3


class VeltoDatabase:
    def __init__(self, path):
        self.path = path
        self.connection = sqlite3.connect(
            path,
            check_same_thread=False
        )
        self.connection.row_factory = sqlite3.Row

    def execute(self, query, parameters=()):
        cursor = self.connection.execute(
            query,
            parameters
        )

        self.connection.commit()

        return cursor

    def query(self, query, parameters=()):
        cursor = self.connection.execute(
            query,
            parameters
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def create_table(self, name, columns):
        if not isinstance(name, str):
            raise ValueError(
                "Table name must be a string"
            )

        if not isinstance(columns, str):
            raise ValueError(
                "Columns must be a string"
            )

        query = (
            "CREATE TABLE IF NOT EXISTS "
            + name
            + " ("
            + columns
            + ")"
        )

        self.connection.execute(query)
        self.connection.commit()

        return True

    def insert(self, table, data):
        if not isinstance(data, dict):
            raise ValueError(
                "Data must be a dictionary"
            )

        keys = list(data.keys())
        values = list(data.values())

        columns = ", ".join(keys)

        placeholders = ", ".join(
            ["?" for value in values]
        )

        query = (
            "INSERT INTO "
            + table
            + " ("
            + columns
            + ") VALUES ("
            + placeholders
            + ")"
        )

        cursor = self.connection.execute(
            query,
            values
        )

        self.connection.commit()

        return cursor.lastrowid

    def update(self, table, data, where, parameters=()):
        if not isinstance(data, dict):
            raise ValueError(
                "Data must be a dictionary"
            )

        assignments = ", ".join(
            [
                key + " = ?"
                for key in data
            ]
        )

        values = list(data.values())
        values.extend(parameters)

        query = (
            "UPDATE "
            + table
            + " SET "
            + assignments
            + " WHERE "
            + where
        )

        cursor = self.connection.execute(
            query,
            values
        )

        self.connection.commit()

        return cursor.rowcount

    def delete(self, table, where, parameters=()):
        query = (
            "DELETE FROM "
            + table
            + " WHERE "
            + where
        )

        cursor = self.connection.execute(
            query,
            parameters
        )

        self.connection.commit()

        return cursor.rowcount

    def close(self):
        self.connection.close()
