import csv
import json
import os

from connect import get_connection


def export_json(path="contacts.json"):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT c.name, c.email, c.birthday, g.name,
                   COALESCE(json_agg(json_build_object('phone', p.phone, 'type', p.type))
                            FILTER (WHERE p.id IS NOT NULL), '[]')
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            LEFT JOIN phones p ON p.contact_id = c.id
            GROUP BY c.id, g.name
            ORDER BY c.name
            """
        )
        data = []
        for name, email, birthday, group_name, phones in cur.fetchall():
            data.append(
                {
                    "name": name,
                    "email": email,
                    "birthday": birthday.isoformat() if birthday else None,
                    "group": group_name,
                    "phones": phones,
                }
            )
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Exported to {path}")


def import_json(path="contacts.json"):
    if not os.path.exists(path):
        print(f"{path} not found. Export first (menu 3) or place file in TSIS1 folder.")
        return

    with open(path, "r", encoding="utf-8") as f:
        items = json.load(f)
    with get_connection() as conn, conn.cursor() as cur:
        for item in items:
            name = item["name"]
            cur.execute("SELECT id FROM contacts WHERE name=%s", (name,))
            row = cur.fetchone()
            if row:
                action = input(f"{name} exists. skip/overwrite? ").strip().lower()
                if action == "skip":
                    continue
                cur.execute("DELETE FROM contacts WHERE id=%s", (row[0],))

            cur.execute(
                "INSERT INTO groups(name) VALUES(%s) ON CONFLICT(name) DO NOTHING",
                (item.get("group") or "Other",),
            )
            cur.execute("SELECT id FROM groups WHERE name=%s", (item.get("group") or "Other",))
            group_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO contacts(name, email, birthday, group_id) VALUES(%s, %s, %s, %s) RETURNING id",
                (name, item.get("email"), item.get("birthday"), group_id),
            )
            contact_id = cur.fetchone()[0]
            for p in item.get("phones", []):
                cur.execute(
                    "INSERT INTO phones(contact_id, phone, type) VALUES(%s, %s, %s)",
                    (contact_id, p["phone"], p["type"]),
                )
    print(f"Imported from {path}")


def import_csv(path="contacts.csv"):
    with open(path, "r", encoding="utf-8") as f, get_connection() as conn, conn.cursor() as cur:
        for row in csv.DictReader(f):
            name = row["name"]
            cur.execute("SELECT id FROM contacts WHERE name=%s", (name,))
            existing = cur.fetchone()
            if existing:
                action = input(f"{name} exists. skip/overwrite? ").strip().lower() or "skip"
                if action == "skip":
                    continue
                cur.execute("DELETE FROM contacts WHERE id=%s", (existing[0],))

            group_name = row.get("group", "Other")
            cur.execute("INSERT INTO groups(name) VALUES(%s) ON CONFLICT(name) DO NOTHING", (group_name,))
            cur.execute("SELECT id FROM groups WHERE name=%s", (group_name,))
            group_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO contacts(name, email, birthday, group_id) VALUES(%s, %s, %s, %s) RETURNING id",
                (name, row.get("email"), row.get("birthday"), group_id),
            )
            contact_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO phones(contact_id, phone, type) VALUES(%s, %s, %s)",
                (contact_id, row["phone"], row.get("phone_type", "mobile")),
            )
    print(f"Imported CSV: {path}")


def search_and_filter():
    group_name = input("Group (or empty): ").strip()
    email_q = input("Email contains (or empty): ").strip()
    sort_by = input("Sort by [name/birthday/date]: ").strip().lower() or "name"
    sort_sql = {"name": "c.name", "birthday": "c.birthday", "date": "c.created_at"}.get(sort_by, "c.name")
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT c.name, c.email, c.birthday, g.name
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            WHERE (%s = '' OR g.name = %s)
              AND (%s = '' OR COALESCE(c.email, '') ILIKE '%%' || %s || '%%')
            ORDER BY {sort_sql}
            """,
            (group_name, group_name, email_q, email_q),
        )
        for r in cur.fetchall():
            print(r)


def page_loop(limit=2):
    page = 0
    with get_connection() as conn, conn.cursor() as cur:
        while True:
            try:
                cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, page * limit))
            except Exception:
                # Fallback if existing DB function has ambiguous ORDER BY or signature mismatch.
                conn.rollback()
                cur.execute(
                    """
                    SELECT c.name, c.email, c.birthday, g.name,
                           COALESCE(string_agg(p.phone || ' (' || p.type || ')', ', '), '')
                    FROM contacts c
                    LEFT JOIN groups g ON c.group_id = g.id
                    LEFT JOIN phones p ON c.id = p.contact_id
                    GROUP BY c.id, g.name
                    ORDER BY c.name
                    LIMIT %s OFFSET %s
                    """,
                    (limit, page * limit),
                )
            rows = cur.fetchall()
            print(f"\nPage {page + 1}")
            for r in rows:
                print(r)
            cmd = input("next/prev/quit: ").strip().lower()
            if cmd == "next":
                page += 1
            elif cmd == "prev" and page > 0:
                page -= 1
            else:
                break


if __name__ == "__main__":
    print("1) filter/search  2) page  3) export json  4) import json  5) import csv")
    choice = input("Choose: ").strip()
    if choice == "1":
        search_and_filter()
    elif choice == "2":
        page_loop()
    elif choice == "3":
        export_json()
    elif choice == "4":
        import_json()
    elif choice == "5":
        import_csv()
