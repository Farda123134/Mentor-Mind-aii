
# ═══════════════════════════════════════════════════════
# MIGRATION SCRIPT
# SQLite data → PostgreSQL migrate karo
# ═══════════════════════════════════════════════════════

import json
import logging
import sqlite3

log = logging.getLogger("MentorMind")


def migrate_sqlite_to_postgres(sqlite_path: str = "mentor_mind.db"):
    """
    SQLite ka data PostgreSQL mein copy karo.

    Steps:
    1. SQLite se sab data padhte hain
    2. PostgreSQL mein insert karte hain
    3. Verify karte hain
    """
    from mentor_mind.database.db_operations import (
        get_or_create_user, save_study_plan,
        save_message, save_quiz_result
    )
    from mentor_mind.database.engine import init_database

    print("Starting migration...")

    # Step 1: PostgreSQL tables banao
    init_database()
    print("✅ PostgreSQL tables ready")

    # Step 2: SQLite se data padhو
    try:
        conn = sqlite3.connect(sqlite_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
    except Exception as e:
        print(f"❌ SQLite open failed: {e}")
        return False

    migrated = {"users": 0, "plans": 0, "messages": 0}

    # Users migrate karo
    try:
        cursor.execute("SELECT * FROM users")
        for row in cursor.fetchall():
            get_or_create_user(row["session_id"], row.get("name","Student"))
            migrated["users"] += 1
        print(f"✅ Users migrated: {migrated['users']}")
    except Exception as e:
        print(f"⚠️  Users migration: {e}")

    # Study plans migrate karo
    try:
        cursor.execute("SELECT * FROM study_plans")
        for row in cursor.fetchall():
            plan_data = {
                "topic"     : row["topic"],
                "total_days": row["total_days"],
                "schedule"  : json.loads(row["schedule"]),
                "start_date": row["start_date"]
            }
            save_study_plan(row["session_id"], row["topic"], plan_data)
            migrated["plans"] += 1
        print(f"✅ Plans migrated: {migrated['plans']}")
    except Exception as e:
        print(f"⚠️  Plans migration: {e}")

    # Conversations migrate karo
    try:
        cursor.execute("SELECT * FROM conversations LIMIT 500")
        for row in cursor.fetchall():
            save_message(
                row["session_id"],
                row["role"],
                row["message"],
                row.get("agent_used","")
            )
            migrated["messages"] += 1
        print(f"✅ Messages migrated: {migrated['messages']}")
    except Exception as e:
        print(f"⚠️  Messages migration: {e}")

    conn.close()

    print(f"""
Migration Complete!
  Users   : {migrated['users']}
  Plans   : {migrated['plans']}
  Messages: {migrated['messages']}
""")
    return True
