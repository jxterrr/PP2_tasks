from connect import connection, cursor


def insert(cur, conn, name, phone):
    try:
        cur.execute(
            "INSERT INTO phonebook(username, phone_number) VALUES (%s,%s)",
            (name, phone)
        )
        conn.commit()
        print("Inserted successfully!")
    except Exception as e:
        print("Insert failed:", e)


def update(cur, conn, name, phone):
    try:
        cur.execute(
            "UPDATE phonebook SET phone_number=%s WHERE username=%s",
            (phone, name)
        )
        conn.commit()
        print("Updated successfully!")
    except Exception as e:
        print("Update failed:", e)


def show(cur):
    try:
        cur.execute("SELECT * FROM phonebook")
        rows = cur.fetchall()

        print("\nID | NAME | PHONE")
        print("-" * 30)

        for row in rows:
            print(f"{row[0]} | {row[1]} | {row[2]}")
    except Exception as e:
        print("Show failed:", e)


def filter_data(cur, order_by, order_dir):
    try:
        cur.execute(
            f"SELECT * FROM phonebook ORDER BY {order_by} {order_dir}"
        )
        for row in cur.fetchall():
            print(row)
    except Exception as e:
        print("Filter failed:", e)


def import_csv(cur, conn):
    try:
        with open("contacts.csv", "r") as f:
            cur.copy_expert(
                "COPY phonebook(username, phone_number) FROM STDIN WITH CSV HEADER",
                f
            )
        conn.commit()
        print("CSV imported!")
    except Exception as e:
        print("CSV import failed:", e)


def delete(cur, conn, name):
    try:
        cur.execute(
            "DELETE FROM phonebook WHERE username=%s",
            (name,)
        )
        conn.commit()
        print("Deleted successfully!")
    except Exception as e:
        print("Delete failed:", e)


def main():
    conn = connection()
    if not conn:
        return

    cur = cursor(conn)

    while True:
        print("""
1) Insert
2) Update
3) Show all
4) Filter
5) Import CSV
6) Delete
0) Exit
""")

        choice = input("Choose: ")

        if choice == "1":
            insert(cur, conn,
                   input("Name: "),
                   input("Phone: "))

        elif choice == "2":
            update(cur, conn,
                   input("Name: "),
                   input("New phone: "))

        elif choice == "3":
            show(cur)

        elif choice == "4":
            col = input("1) Name 2) Phone: ")
            direction = input("1) ASC 2) DESC: ")

            order_by = "username" if col != "2" else "phone_number"
            order_dir = "ASC" if direction != "2" else "DESC"

            filter_data(cur, order_by, order_dir)

        elif choice == "5":
            import_csv(cur, conn)

        elif choice == "6":
            delete(cur, conn, input("Name: "))

        elif choice == "0":
            break

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()