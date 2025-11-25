import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

def bool_mark(v):
    if v is None:
        return "—"
    try:
        iv = int(v)
        return "✔" if iv == 1 else "✖"
    except:
        s = str(v).strip().lower()
        if s in {"1", "true", "yes", "y"}: return "✔"
        if s in {"0", "false", "no", "n"}: return "✖"
        return s


def exec_fetchall(conn, sql, params=None):
    cur = conn.cursor()
    cur.execute(sql, params or ())
    rows = cur.fetchall()
    cur.close()
    return rows

def exec_commit(conn, sql, params=None):
    cur = conn.cursor()
    cur.execute(sql, params or ())
    conn.commit()
    cur.close()