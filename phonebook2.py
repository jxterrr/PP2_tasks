from connect import connection, cursor

def main() -> int:
    conn = connection()
    cur = cursor(conn)

    def insert(name: str, phone: str):
        try:
            cur.execute(
                "INSERT INTO PhoneBook (name, phone_number) VALUES (%s, %s)", (name, phone)
            )
            conn.commit()
            print("Successfully!")
        except:
            print("Failed")

    def update(name: str, phone: str):
        try:
            cur.execute(
                "UPDATE PhoneBook SET phone_number = %s WHERE name = %s", (phone, name)
            )
            conn.commit()
            print("Successfully!")
        except:
            print("Failed")

    def filter(order_by: str, order_dir: str):
        cur.execute(f"SELECT * FROM PhoneBook ORDER BY {order_by} {order_dir}")
        rows = cur.fetchall()
        for row in rows:
            print(row)

    # --- Menu ---
    print("1) Insert  2) Update  3) Filter")
    choice = input("Choose: ")

    if choice == "1":
        name  = input("Name: ")
        phone = input("Phone: ")
        insert(name, phone)

    elif choice == "2":
        name  = input("Name: ")
        phone = input("New phone: ")
        update(name, phone)

    elif choice == "3":
        print("Sort by: 1) Name  2) Phone")
        col = input("Choose: ")
        print("Order:   1) ASC   2) DESC")
        direction = input("Choose: ")

        order_by  = "name"         if col       != "2" else "phone_number"
        order_dir = "ASC"          if direction != "2" else "DESC"

        filter(order_by, order_dir)

main()