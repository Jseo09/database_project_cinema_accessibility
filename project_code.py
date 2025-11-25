#!/usr/bin/env python3
"""
Cinema Accessibility Database Viewer

Requires:
- mysql-connector-python
- tkinterweb
- pillow (PIL)
"""

import webbrowser
import mysql.connector
from mysql.connector import Error
import re, os
import tkinter as tk
from tkinter import ttk, messagebox
from tkinterweb import HtmlFrame
from typing import Optional, Callable
import difflib
from PIL import Image, ImageTk, ImageDraw, ImageFont


APP_DIR = os.path.dirname(os.path.abspath(__file__))


DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "Edit Password HERE",
    "database": "cinema"
}

TABLE_THEATERS = "Theater"
COL_TID = "theater_id"
COL_NAME = "theater_name"
COL_CITY = "city"
COL_STATE = "state"
COL_STATUS = "status"
COL_URL = "website"
COL_ADDR = "address"
COL_T_LAT = "latitude"
COL_T_LON = "longitude"
COL_PHONE = "phone_number"
ROAD_VIEW_DIR = os.path.join(APP_DIR, "image", "road_view")
ROAD_ALLOWED_EXTS = (".png", ".jpg", ".jpeg", ".webp")

TABLE_FEAT = "TheaterFeatures"
COL_WHEEL = "wheel_chair_accessibility"
COL_AL = "assistive_listening"
COL_CC = "caption_device"
COL_AD = "audio_description"
COL_SRC = "info_source"
COL_CONF = "data_confidence"

TABLE_SHOW = "ShowDates"
COL_SHOWID = "show_id"
COL_DT = "show_date"
COL_IS_CC = "is_captioned"
COL_IS_AD = "is_audio_described"

TABLE_MOV = "Movies"
COL_MID = "show_id"
COL_MNAME = "movie_title"

TABLE_TTRANSIT = "TheaterTransit"
TT_THEATER_ID = "theater_id"
TT_STOP_ID = "stop_id"
TT_WALK_M = "walk_distance_m"
TT_WALK_MIN = "walk_time_min"

TABLE_TSTOPS = "TransitStops"
TS_STOP_ID = "stop_id"
TS_NAME = "stop_name"
TS_ACCESSIBLE = "accessibility"
TS_LAT = "latitude"
TS_LON = "longitude"

TABLE_SROUTES = "StopRoutes"
SR_STOP_ID = "stop_id"
SR_ROUTE = "route"


POSTER_DIR = os.path.join(APP_DIR, "image", "movie_poster")
POSTER_DEFAULT = os.path.join(POSTER_DIR, "question.png") 
ALLOWED_EXTS = (".png", ".jpg", ".jpeg", ".webp")


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

def build_list_query(limit=1000):
    return f"""
    SELECT {COL_TID} AS TID,
           {COL_NAME} AS Name,
           {COL_CITY} AS City,
           {COL_STATE} AS State,
           {COL_STATUS} AS Status
    FROM {TABLE_THEATERS}
    ORDER BY City, Name
    LIMIT {limit};
    """.strip()

def build_features_query():
    return f"""
    SELECT {COL_WHEEL}, {COL_AL}, {COL_CC}, {COL_AD}, {COL_SRC}, {COL_CONF}
    FROM {TABLE_FEAT}
    WHERE {COL_TID} = %s
    """.strip()

def build_movies_for_theater_query():
    return f"""
    SELECT s.{COL_SHOWID} AS show_id,
           COALESCE(m.{COL_MNAME}, '(Unknown)') AS movie_title,
           COUNT(*) AS num_shows
    FROM {TABLE_SHOW} s
    LEFT JOIN {TABLE_MOV} m
      ON m.{COL_MID} = s.{COL_SHOWID}
    WHERE s.{COL_TID} = %s
    GROUP BY s.{COL_SHOWID}, m.{COL_MNAME}
    ORDER BY movie_title;
    """.strip()

def build_showdates_for_movie_query():
    return f"""
    SELECT s.{COL_DT}   AS show_date,
           s.{COL_IS_CC} AS is_cc,
           s.{COL_IS_AD} AS is_ad
    FROM {TABLE_SHOW} s
    WHERE s.{COL_TID} = %s
      AND s.{COL_SHOWID} = %s
    ORDER BY s.{COL_DT} ASC;
    """.strip()

def build_showtimes_query():
    return f"""
    SELECT s.{COL_DT} AS show_date,
           COALESCE(m.{COL_MNAME}, '(Unknown)') AS movie_title,
           s.{COL_IS_CC} AS is_cc,
           s.{COL_IS_AD} AS is_ad
    FROM {TABLE_SHOW} s
    LEFT JOIN {TABLE_MOV} m
      ON m.{COL_MID} = s.{COL_SHOWID}
    WHERE s.{COL_TID} = %s
    ORDER BY s.{COL_DT} ASC
    """.strip()

def open_admin_gate(parent: tk.Misc, on_success: Callable[[], None]) -> None:
    dlg = tk.Toplevel(parent)
    dlg.title("Admin Login")
    dlg.transient(parent)
    dlg.grab_set()
    dlg.geometry("380x200")

    frm = ttk.Frame(dlg, padding=16)
    frm.pack(fill="both", expand=True)

    ttk.Label(frm, text="Administrator Login", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))
    ttk.Label(frm, text="Username").grid(row=1, column=0, sticky="e", padx=(0,8), pady=4)
    ent_user = ttk.Entry(frm, width=28)
    ent_user.grid(row=1, column=1, sticky="w", pady=4)

    ttk.Label(frm, text="Password").grid(row=2, column=0, sticky="e", padx=(0,8), pady=4)
    ent_pass = ttk.Entry(frm, width=28, show="*")
    ent_pass.grid(row=2, column=1, sticky="w", pady=4)

    def do_cancel():
        dlg.grab_release()
        dlg.destroy()

    def do_login():
        u = ent_user.get().strip()
        p = ent_pass.get().strip()
        if u == "admin" and p == "admin":
            dlg.grab_release()
            dlg.destroy()
            try:
                on_success()
            except Exception as ex:
                messagebox.showerror("Error", str(ex), parent=parent)
        else:
            messagebox.showerror("Login failed", "Invalid credentials.", parent=dlg)

    btns = ttk.Frame(frm)
    btns.grid(row=3, column=0, columnspan=2, sticky="e", pady=(12,0))
    ttk.Button(btns, text="Cancel", command=do_cancel).grid(row=0, column=0, padx=6)
    ttk.Button(btns, text="Login", command=do_login).grid(row=0, column=1)

    dlg.bind("<Return>", lambda e: do_login())
    dlg.bind("<Escape>", lambda e: do_cancel())
    ent_user.focus_set()


STATUS_CHOICES = ("Open", "Temporarily Closed", "Closed")
US_STATES = (
    "TX","CA","NY","FL","IL","GA","PA","OH","NC","MI",
    "AZ","WA","MA","NJ","VA","IN","TN","MO","MD","WI",
    "CO","MN","SC","AL","LA","KY","OR","OK","CT","UT",
    "IA","NV","AR","MS","KS","NM","NE","WV","ID","HI",
    "NH","ME","RI","MT","DE","SD","ND","AK","VT","DC",
)
def open_add_theater_dialog(
    parent: tk.Misc,
    get_conn: Optional[Callable[[], mysql.connector.MySQLConnection]] = None,
    on_saved: Optional[Callable[[], None]] = None,
) -> None:
    def _default_get_conn():
        return mysql.connector.connect(**DB_CONFIG)
    conn_factory = get_conn or _default_get_conn

    dlg = tk.Toplevel(parent)
    dlg.title("Add Theater")
    dlg.transient(parent)
    dlg.grab_set()
    dlg.geometry("560x700")
    dlg.minsize(540, 680)

    container = ttk.Frame(dlg, padding=16)
    container.pack(fill="both", expand=True)

    ttk.Label(container, text="Theater Details",
              font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=2,
                                                  sticky="w", pady=(0, 10))

    ttk.Label(container, text="Name *").grid(row=1, column=0, sticky="e", padx=(0, 8), pady=4)
    ent_name = ttk.Entry(container, width=40); ent_name.grid(row=1, column=1, sticky="w", pady=4)

    ttk.Label(container, text="City *").grid(row=2, column=0, sticky="e", padx=(0, 8), pady=4)
    ent_city = ttk.Entry(container, width=30); ent_city.grid(row=2, column=1, sticky="w", pady=4)

    ttk.Label(container, text="State *").grid(row=3, column=0, sticky="e", padx=(0, 8), pady=4)
    cmb_state = ttk.Combobox(container, values=US_STATES, width=10, state="readonly")
    cmb_state.grid(row=3, column=1, sticky="w", pady=4)
    if US_STATES: cmb_state.set(US_STATES[0])

    ttk.Label(container, text="Status *").grid(row=4, column=0, sticky="e", padx=(0, 8), pady=4)
    cmb_status = ttk.Combobox(container, values=STATUS_CHOICES, width=20, state="readonly")
    cmb_status.grid(row=4, column=1, sticky="w", pady=4)
    cmb_status.set(STATUS_CHOICES[0])

    ttk.Label(container, text="Website").grid(row=5, column=0, sticky="e", padx=(0, 8), pady=4)
    ent_url = ttk.Entry(container, width=45); ent_url.grid(row=5, column=1, sticky="w", pady=4)

    ttk.Label(container, text="Address *").grid(row=6, column=0, sticky="e", padx=(0, 8), pady=4)
    ent_addr = ttk.Entry(container, width=45); ent_addr.grid(row=6, column=1, sticky="w", pady=4)

    ttk.Label(container, text="Phone").grid(row=7, column=0, sticky="e", padx=(0, 8), pady=4)
    ent_phone = ttk.Entry(container, width=30); ent_phone.grid(row=7, column=1, sticky="w", pady=4)

    ttk.Label(container, text="Latitude *").grid(row=8, column=0, sticky="e", padx=(0, 8), pady=4)
    ent_lat = ttk.Entry(container, width=20); ent_lat.grid(row=8, column=1, sticky="w", pady=4)

    ttk.Label(container, text="Longitude *").grid(row=9, column=0, sticky="e", padx=(0, 8), pady=4)
    ent_lon = ttk.Entry(container, width=20); ent_lon.grid(row=9, column=1, sticky="w", pady=4)

    ttk.Separator(container).grid(row=10, column=0, columnspan=2, sticky="ew", pady=10)
    ttk.Label(container, text="Accessibility Features",
              font=("Segoe UI", 11, "bold")).grid(row=11, column=0, columnspan=2, sticky="w", pady=(0, 8))

    var_wheel = tk.IntVar(value=0)
    var_al = tk.IntVar(value=0)
    var_cc = tk.IntVar(value=0)
    var_ad = tk.IntVar(value=0)

    ttk.Checkbutton(container, text="Wheelchair Accessible", variable=var_wheel)\
        .grid(row=12, column=0, columnspan=2, sticky="w", pady=2)
    ttk.Checkbutton(container, text="Assistive Listening", variable=var_al)\
        .grid(row=13, column=0, columnspan=2, sticky="w", pady=2)
    ttk.Checkbutton(container, text="Caption Device", variable=var_cc)\
        .grid(row=14, column=0, columnspan=2, sticky="w", pady=2)
    ttk.Checkbutton(container, text="Audio Description", variable=var_ad)\
        .grid(row=15, column=0, columnspan=2, sticky="w", pady=2)

    ttk.Label(container, text="Info source (URL or text)")\
        .grid(row=16, column=0, sticky="e", padx=(0, 8), pady=(8, 4))
    ent_src = ttk.Entry(container, width=45)
    ent_src.grid(row=16, column=1, sticky="w", pady=(8, 4))

    ttk.Label(container, text="Confidence")\
        .grid(row=17, column=0, sticky="e", padx=(0, 8), pady=4)
    cmb_conf = ttk.Combobox(container,
                            values=("High", "Medium", "Low", "Unknown"),
                            width=20, state="readonly")
    cmb_conf.grid(row=17, column=1, sticky="w", pady=4)
    cmb_conf.set("High")

    footer = ttk.Frame(dlg, padding=(16, 10))
    footer.pack(fill="x", side="bottom")

    def on_cancel():
        try:
            dlg.grab_release()
        except Exception:
            pass
        dlg.destroy()

    def validate_inputs(name: str, city: str, state: str, status: str) -> Optional[str]:
        if not name.strip(): return "Name is required."
        if not city.strip(): return "City is required."
        if not state.strip(): return "State is required."
        if not status.strip(): return "Status is required."
        return None

    def insert_records():
        name = ent_name.get().strip()
        city = ent_city.get().strip()
        state = (cmb_state.get() or "").strip()
        status = (cmb_status.get() or "").strip()
        url = ent_url.get().strip() or None

        addr = ent_addr.get().strip() or None
        phone = ent_phone.get().strip() or None
        lat_s = ent_lat.get().strip() or None
        lon_s = ent_lon.get().strip() or None

        err = validate_inputs(name, city, state, status)
        if err:
            messagebox.showwarning("Missing data", err, parent=dlg)
            return

        try:
            lat_val = float(lat_s) if lat_s else None
        except ValueError:
            messagebox.showwarning("Invalid", "Latitude must be a number.", parent=dlg)
            return
        try:
            lon_val = float(lon_s) if lon_s else None
        except ValueError:
            messagebox.showwarning("Invalid", "Longitude must be a number.", parent=dlg)
            return

        conn = None
        cur = None
        try:
            conn = conn_factory()
            cur = conn.cursor()

            cur.execute(
                f"SELECT {COL_TID} FROM {TABLE_THEATERS} "
                f"WHERE {COL_NAME}=%s AND {COL_CITY}=%s AND {COL_STATE}=%s LIMIT 1",
                (name, city, state),
            )
            if cur.fetchone():
                messagebox.showerror(
                    "Duplicate",
                    "A theater with the same name, city, and state already exists.",
                    parent=dlg,
                )
                return

            cols = [COL_NAME, COL_CITY, COL_STATE, COL_STATUS]
            vals = [name, city, state, status]
            if COL_URL: cols.append(COL_URL); vals.append(url)
            if COL_ADDR: cols.append(COL_ADDR); vals.append(addr)
            if COL_PHONE: cols.append(COL_PHONE); vals.append(phone)
            if COL_T_LAT: cols.append(COL_T_LAT); vals.append(lat_val)
            if COL_T_LON: cols.append(COL_T_LON); vals.append(lon_val)

            q_ins_t = (
                f"INSERT INTO {TABLE_THEATERS} ({', '.join(cols)}) "
                f"VALUES ({', '.join(['%s'] * len(vals))})"
            )
            cur.execute(q_ins_t, tuple(vals))
            theater_id = cur.lastrowid

            src = (ent_src.get() or "").strip()
            conf = (cmb_conf.get() or "Unknown").strip()

            cols_f = [COL_TID, COL_WHEEL, COL_AL, COL_CC, COL_AD]
            vals_f = [theater_id,
                      int(var_wheel.get()),
                      int(var_al.get()),
                      int(var_cc.get()),
                      int(var_ad.get())]
            if COL_SRC: cols_f.append(COL_SRC); vals_f.append(src)
            if COL_CONF: cols_f.append(COL_CONF); vals_f.append(conf)

            q_ins_f = (
                f"INSERT INTO {TABLE_FEAT} ({', '.join(cols_f)}) "
                f"VALUES ({', '.join(['%s'] * len(vals_f))})"
            )
            cur.execute(q_ins_f, tuple(vals_f))

            conn.commit()
            if callable(on_saved):
                try:
                    on_saved()
                except Exception:
                    pass
            messagebox.showinfo("Success", f"Theater added with ID {theater_id}.", parent=dlg)
            try:
                dlg.grab_release()
            except Exception:
                pass
            dlg.destroy()

        except Error as e:
            try:
                if conn and conn.is_connected():
                    conn.rollback()
            except Exception:
                pass
            messagebox.showerror("Database Error", str(e), parent=dlg)
        finally:
            try:
                if cur:
                    cur.close()
            except Exception:
                pass
            try:
                if conn and hasattr(conn, "is_connected") and conn.is_connected():
                    conn.close()
            except Exception:
                pass

    ttk.Button(footer, text="Cancel", command=on_cancel).pack(side="right", padx=6)
    ttk.Button(footer, text="Save", command=insert_records).pack(side="right")

    dlg.bind("<Escape>", lambda e: on_cancel())
    dlg.bind("<Return>", lambda e: insert_records())
    ent_name.focus_set()



def _exec_fetchall(conn, sql, params=None):
    cur = conn.cursor()
    cur.execute(sql, params or ())
    rows = cur.fetchall()
    cur.close()
    return rows

def _exec_commit(conn, sql, params=None):
    cur = conn.cursor()
    cur.execute(sql, params or ())
    conn.commit()
    cur.close()

def open_admin_panel(app: tk.Misc, conn):
    win = tk.Toplevel(app)
    win.title("Admin Panel — Manage Data")
    win.geometry("980x640")

    nb = ttk.Notebook(win)
    nb.pack(fill="both", expand=True)
    def _treeview_sort(tv: ttk.Treeview, col: str, numeric: bool = False):
            """Treeview를 col 기준으로 오름/내림 토글 정렬"""
            cols = list(tv["columns"])
            try:
                idx = cols.index(col)
            except ValueError:
                return

            items = []
            for iid in tv.get_children(""):
                vals = tv.item(iid, "values")
                if idx >= len(vals):
                    key = ""
                else:
                    v = vals[idx]
                    if numeric:
                        try:
                            key = float(v)
                        except Exception:
                            key = 0.0
                    else:
                        key = str(v).lower()
                items.append((key, iid))

            if not hasattr(tv, "_sort_reverse"):
                tv._sort_reverse = {}
            reverse = tv._sort_reverse.get(col, False)

            items.sort(reverse=reverse)

            for pos, (_, iid) in enumerate(items):
                tv.move(iid, "", pos)

            tv._sort_reverse[col] = not reverse

    def _make_col_sortable(tv: ttk.Treeview, col: str, *, numeric: bool = False, text: str | None = None):
            """해당 컬럼 헤더를 클릭하면 정렬되도록 설정"""
            label = text if text is not None else col.upper()
            tv.heading(
                col,
                text=label,
                command=lambda c=col, n=numeric, t=tv: _treeview_sort(t, c, n),
            )


    frm_th = ttk.Frame(nb, padding=8); nb.add(frm_th, text="Theaters")
    tv_th = ttk.Treeview(frm_th, columns=("id","name","city","state","status","url"), show="headings")
    for c,w in ("id",80), ("name",260), ("city",140), ("state",70), ("status",140), ("url",260):
        tv_th.heading(c, text=c.upper())
        tv_th.column(c, width=w, anchor="w")
    tv_th.pack(side="left", fill="both", expand=True)
    sb_th = ttk.Scrollbar(frm_th, orient="vertical", command=tv_th.yview)
    sb_th.pack(side="left", fill="y")
    tv_th.configure(yscrollcommand=sb_th.set)

    _make_col_sortable(tv_th, "id",   numeric=True,  text="ID")
    _make_col_sortable(tv_th, "name", numeric=False, text="NAME")

    def refresh_th():
        tv_th.delete(*tv_th.get_children())
        rows = _exec_fetchall(conn, f"SELECT {COL_TID},{COL_NAME},{COL_CITY},{COL_STATE},{COL_STATUS},{COL_URL} FROM {TABLE_THEATERS} ORDER BY {COL_CITY},{COL_NAME}")
        for r in rows: tv_th.insert("", "end", values=r)


    def add_th():
        open_add_theater_dialog(
            app,
            get_conn=lambda: mysql.connector.connect(**DB_CONFIG),
            on_saved=lambda: (
                refresh_th(),
                getattr(app, "_load_theaters", lambda: None)()
            )
        )

    def edit_th():
        sel = tv_th.selection()
        if not sel:
            messagebox.showinfo("Edit Theater", "Select a theater first.", parent=win); return
        tid, name, city, state, status, url = tv_th.item(sel[0], "values")
        dlg = tk.Toplevel(win); dlg.title(f"Edit Theater #{tid}"); dlg.transient(win); dlg.grab_set()
        f = ttk.Frame(dlg, padding=12); f.pack(fill="both", expand=True)
        e_name = ttk.Entry(f, width=40); e_name.insert(0, name)
        e_city = ttk.Entry(f, width=30); e_city.insert(0, city)
        c_state = ttk.Combobox(f, values=US_STATES, width=10, state="readonly"); c_state.set(state)
        c_status= ttk.Combobox(f, values=STATUS_CHOICES, width=22, state="readonly"); c_status.set(status)
        e_url = ttk.Entry(f, width=48); e_url.insert(0, url or "")
        for i,(lab,widget) in enumerate((('Name',e_name),('City',e_city),('State',c_state),('Status',c_status),('URL',e_url))):
            ttk.Label(f, text=lab).grid(row=i, column=0, sticky='e', padx=(0,8), pady=4)
            widget.grid(row=i, column=1, sticky='w', pady=4)
        btns=ttk.Frame(f); btns.grid(row=6,column=0,columnspan=2,sticky='e',pady=(12,0))
        def save():
            _exec_commit(conn, f"UPDATE {TABLE_THEATERS} SET {COL_NAME}=%s,{COL_CITY}=%s,{COL_STATE}=%s,{COL_STATUS}=%s,{COL_URL}=%s WHERE {COL_TID}=%s",
                         (e_name.get().strip(), e_city.get().strip(), c_state.get().strip(), c_status.get().strip(), (e_url.get().strip() or None), tid))
            dlg.destroy(); refresh_th()
        ttk.Button(btns, text="Cancel", command=dlg.destroy).grid(row=0,column=0,padx=6)
        ttk.Button(btns, text="Save", command=save).grid(row=0,column=1)

    def del_th():
        sel = tv_th.selection()
        if not sel:
            messagebox.showinfo("Delete Theater", "Select a theater first.", parent=win); return
        tid = tv_th.item(sel[0], "values")[0]
        if not messagebox.askyesno("Confirm", f"Delete theater #{tid}? (Check FK cascades.)", parent=win): return
        try:
            _exec_commit(conn, f"DELETE FROM {TABLE_THEATERS} WHERE {COL_TID}=%s", (tid,))
            refresh_th()
        except Error as e:
            messagebox.showerror("DB Error", str(e), parent=win)

    tbar = ttk.Frame(frm_th); tbar.pack(fill="x", pady=(6,0))
    ttk.Button(tbar, text="Add", command=add_th).pack(side="left", padx=3)
    ttk.Button(tbar, text="Edit", command=edit_th).pack(side="left", padx=3)
    ttk.Button(tbar, text="Delete", command=del_th).pack(side="left", padx=3)

    frm_ts = ttk.Frame(nb, padding=8); nb.add(frm_ts, text="Transit Stops")
    tv_ts = ttk.Treeview(frm_ts, columns=("stop_id","name","acc","lat","lon"), show="headings")
    for c,w in ("stop_id",100),("name",320),("acc",90),("lat",120),("lon",120):
        tv_ts.heading(c, text=c.upper()); tv_ts.column(c, width=w, anchor='w')
    tv_ts.pack(side="left", fill="both", expand=True)
    ttk.Scrollbar(frm_ts, orient="vertical", command=tv_ts.yview).pack(side="left", fill="y")
    _make_col_sortable(tv_ts, "stop_id", numeric=True,  text="STOP_ID")
    _make_col_sortable(tv_ts, "name",    numeric=False, text="NAME")

    def refresh_ts():
        tv_ts.delete(*tv_ts.get_children())
        rows = _exec_fetchall(conn, f"SELECT {TS_STOP_ID},{TS_NAME},{TS_ACCESSIBLE},{TS_LAT},{TS_LON} FROM {TABLE_TSTOPS} ORDER BY {TS_NAME}")
        for r in rows: tv_ts.insert("", "end", values=r)

    def add_ts():
        dlg = tk.Toplevel(win)
        dlg.title("Add Transit Stop")
        dlg.transient(win)
        dlg.grab_set()

        f = ttk.Frame(dlg, padding=12)
        f.pack(fill="both", expand=True)

        ttk.Label(f, text="Stop Name *").grid(row=0, column=0, sticky="e", padx=(0,8), pady=4)
        e_name = ttk.Entry(f, width=40)
        e_name.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(f, text="Accessible (0 or 1)").grid(row=1, column=0, sticky="e", padx=(0,8), pady=4)
        c_acc = ttk.Combobox(f, values=("0", "1"), width=5, state="readonly")
        c_acc.grid(row=1, column=1, sticky="w", pady=4)
        c_acc.set("0")

        ttk.Label(f, text="Latitude").grid(row=2, column=0, sticky="e", padx=(0,8), pady=4)
        e_lat = ttk.Entry(f, width=20)
        e_lat.grid(row=2, column=1, sticky="w", pady=4)

        ttk.Label(f, text="Longitude").grid(row=3, column=0, sticky="e", padx=(0,8), pady=4)
        e_lon = ttk.Entry(f, width=20)
        e_lon.grid(row=3, column=1, sticky="w", pady=4)

        btns = ttk.Frame(f)
        btns.grid(row=5, column=0, columnspan=2, sticky="e", pady=(12,0))

        def save():
            name = e_name.get().strip()
            acc = int(c_acc.get())
            lat = e_lat.get().strip() or None
            lon = e_lon.get().strip() or None

            if not name:
                messagebox.showwarning("Missing", "Stop name is required.", parent=dlg)
                return

            lat_v = None
            lon_v = None
            try:
                if lat: lat_v = float(lat)
                if lon: lon_v = float(lon)
            except:
                messagebox.showwarning("Invalid", "Latitude/Longitude must be numbers.", parent=dlg)
                return

            _exec_commit(
                conn,
                f"INSERT INTO {TABLE_TSTOPS} ({TS_NAME}, {TS_ACCESSIBLE}, {TS_LAT}, {TS_LON}) VALUES (%s, %s, %s, %s)",
                (name, acc, lat_v, lon_v)
            )
            dlg.destroy()
            refresh_ts()
            messagebox.showinfo("Added", f"Stop added successfully.", parent=win)

        ttk.Button(btns, text="Cancel", command=dlg.destroy).grid(row=0, column=0, padx=6)
        ttk.Button(btns, text="Save", command=save).grid(row=0, column=1)

        e_name.focus_set()


    def edit_ts():
        sel=tv_ts.selection()
        if not sel: messagebox.showinfo("Edit Stop","Select a stop.",parent=win); return
        sid,name,acc,lat,lon=tv_ts.item(sel[0],"values")
        dlg = tk.Toplevel(win); dlg.title(f"Edit Stop {sid}"); dlg.transient(win); dlg.grab_set()
        f=ttk.Frame(dlg,padding=12); f.pack(fill='both',expand=True)
        e_nm=ttk.Entry(f,width=38); e_nm.insert(0,name)
        c_acc=ttk.Combobox(f,values=("0","1"),state='readonly',width=6); c_acc.set(str(acc))
        e_lat=ttk.Entry(f,width=18); e_lat.insert(0,lat or "")
        e_lon=ttk.Entry(f,width=18); e_lon.insert(0,lon or "")
        for i,(lab,w) in enumerate((('Name',e_nm),('Accessible(0/1)',c_acc),('Latitude',e_lat),('Longitude',e_lon))):
            ttk.Label(f,text=lab).grid(row=i,column=0,sticky='e',padx=(0,8),pady=4); w.grid(row=i,column=1,sticky='w',pady=4)
        btns=ttk.Frame(f); btns.grid(row=6,column=0,columnspan=2,sticky='e',pady=(12,0))
        def save():
            _exec_commit(conn, f"UPDATE {TABLE_TSTOPS} SET {TS_NAME}=%s,{TS_ACCESSIBLE}=%s,{TS_LAT}=%s,{TS_LON}=%s WHERE {TS_STOP_ID}=%s",
                         (e_nm.get().strip(), c_acc.get().strip(), (e_lat.get().strip() or None), (e_lon.get().strip() or None), sid))
            dlg.destroy(); refresh_ts()
        ttk.Button(btns,text='Cancel',command=dlg.destroy).grid(row=0,column=0,padx=6)
        ttk.Button(btns,text='Save',command=save).grid(row=0,column=1)

    def del_ts():
        sel=tv_ts.selection()
        if not sel: messagebox.showinfo("Delete Stop","Select a stop.",parent=win); return
        sid=tv_ts.item(sel[0],"values")[0]
        if not messagebox.askyesno("Confirm", f"Delete stop {sid}?", parent=win): return
        _exec_commit(conn, f"DELETE FROM {TABLE_TSTOPS} WHERE {TS_STOP_ID}=%s", (sid,)); refresh_ts()

    tbar2=ttk.Frame(frm_ts); tbar2.pack(fill='x',pady=(6,0))
    ttk.Button(tbar2,text='Add',command=add_ts).pack(side='left',padx=3)
    ttk.Button(tbar2,text='Edit',command=edit_ts).pack(side='left',padx=3)
    ttk.Button(tbar2,text='Delete',command=del_ts).pack(side='left',padx=3)

    frm_mv = ttk.Frame(nb, padding=8); nb.add(frm_mv, text="Movies & ShowDates")

    ttk.Label(frm_mv, text='Movies', font=("Segoe UI",11,'bold')).pack(anchor='w')
    tv_mv = ttk.Treeview(frm_mv, columns=("show_id","title"), show='headings', height=8)
    for c,w in ("show_id",120),("title",420):
        tv_mv.heading(c, text=c.upper())
        tv_mv.column(c, width=w, anchor='w')
    tv_mv.pack(fill='x')

    _make_col_sortable(tv_mv, "show_id", numeric=True,  text="SHOW_ID")
    _make_col_sortable(tv_mv, "title",   numeric=False, text="TITLE")


    ttk.Label(frm_mv, text='ShowDates', font=("Segoe UI",11,'bold')).pack(anchor='w', pady=(8,0))
    tv_sd = ttk.Treeview(frm_mv, columns=("show_id","theater_id","date","cc","ad"), show='headings')
    for c,w in ("show_id",100),("theater_id",100),("date",200),("cc",60),("ad",60):
        tv_sd.heading(c, text=c.upper()); tv_sd.column(c, width=w, anchor='w')
    tv_sd.pack(fill='both', expand=True)

    def refresh_mv():
        tv_mv.delete(*tv_mv.get_children())
        rows = _exec_fetchall(conn, f"SELECT {COL_MID},{COL_MNAME} FROM {TABLE_MOV} ORDER BY {COL_MNAME}")
        for r in rows: tv_mv.insert('', 'end', values=r)
        refresh_sd()

    def refresh_sd(show_id=None):
        tv_sd.delete(*tv_sd.get_children())
        if show_id is None:
            rows = _exec_fetchall(conn, f"SELECT {COL_SHOWID},{COL_TID},{COL_DT},{COL_IS_CC},{COL_IS_AD} FROM {TABLE_SHOW} ORDER BY {COL_DT} DESC LIMIT 200")
        else:
            rows = _exec_fetchall(conn, f"SELECT {COL_SHOWID},{COL_TID},{COL_DT},{COL_IS_CC},{COL_IS_AD} FROM {TABLE_SHOW} WHERE {COL_SHOWID}=%s ORDER BY {COL_DT} DESC", (show_id,))
        for r in rows: tv_sd.insert('', 'end', values=r)

    def on_mv_select(_e):
        sel = tv_mv.selection()
        show_id = tv_mv.item(sel[0], 'values')[0] if sel else None
        refresh_sd(show_id)
    tv_mv.bind('<<TreeviewSelect>>', on_mv_select)

    def add_mv():
        dlg = tk.Toplevel(win); dlg.title('Add Movie'); dlg.transient(win); dlg.grab_set()
        f = ttk.Frame(dlg, padding=12); f.pack(fill='both', expand=True)

        e_title = ttk.Entry(f, width=44)
        ttk.Label(f, text='Title').grid(row=0, column=0, sticky='e', padx=(0,8), pady=4)
        e_title.grid(row=0, column=1, sticky='w', pady=4)

        btns = ttk.Frame(f); btns.grid(row=2, column=0, columnspan=2, sticky='e', pady=(12,0))

        def save():
            title = e_title.get().strip()
            if not title:
                messagebox.showwarning("Missing", "Title is required.", parent=dlg); return
            cur = conn.cursor()
            cur.execute(f"INSERT INTO {TABLE_MOV} ({COL_MNAME}) VALUES (%s)", (title,))
            new_id = cur.lastrowid
            conn.commit()
            cur.close()
            dlg.destroy()
            refresh_mv()
            messagebox.showinfo("Added", f"Movie added with show_id={new_id}", parent=win)

        ttk.Button(btns, text='Cancel', command=dlg.destroy).grid(row=0, column=0, padx=6)
        ttk.Button(btns, text='Save', command=save).grid(row=0, column=1)

    def edit_mv():
        sel=tv_mv.selection()
        if not sel: messagebox.showinfo('Edit Movie','Select a movie.',parent=win); return
        sid,title=tv_mv.item(sel[0],'values')
        dlg=tk.Toplevel(win); dlg.title(f'Edit Movie {sid}'); dlg.transient(win); dlg.grab_set()
        f=ttk.Frame(dlg,padding=12); f.pack(fill='both',expand=True)
        e_t=ttk.Entry(f,width=44); e_t.insert(0,title)
        ttk.Label(f,text='Title').grid(row=0,column=0,sticky='e',padx=(0,8),pady=4); e_t.grid(row=0,column=1,sticky='w',pady=4)
        btns=ttk.Frame(f); btns.grid(row=2,column=0,columnspan=2,sticky='e',pady=(12,0))
        def save():
            _exec_commit(conn, f"UPDATE {TABLE_MOV} SET {COL_MNAME}=%s WHERE {COL_MID}=%s", (e_t.get().strip(), sid))
            dlg.destroy(); refresh_mv()
        ttk.Button(btns,text='Cancel',command=dlg.destroy).grid(row=0,column=0,padx=6)
        ttk.Button(btns,text='Save',command=save).grid(row=0,column=1)

    def del_mv():
        sel=tv_mv.selection()
        if not sel: messagebox.showinfo('Delete Movie','Select a movie.',parent=win); return
        sid=tv_mv.item(sel[0],'values')[0]
        if not messagebox.askyesno('Confirm', f'Delete movie {sid}? (Make sure SHOWDATES are handled)', parent=win): return
        _exec_commit(conn, f"DELETE FROM {TABLE_MOV} WHERE {COL_MID}=%s", (sid,)); refresh_mv()
    
    def add_sd():
        dlg = tk.Toplevel(win)
        dlg.title('Add ShowDate')
        dlg.transient(win)
        dlg.grab_set()

        f = ttk.Frame(dlg, padding=12)
        f.pack(fill='both', expand=True)

        mv_rows = _exec_fetchall(conn, f"SELECT {COL_MID}, {COL_MNAME} FROM {TABLE_MOV} ORDER BY {COL_MNAME}")
        th_rows = _exec_fetchall(conn, f"SELECT {COL_TID}, {COL_NAME}, {COL_CITY}, {COL_STATE} FROM {TABLE_THEATERS} ORDER BY {COL_CITY},{COL_NAME}")

        mv_labels = []
        mv_map = {}
        for sid, title in mv_rows:
            label = f"{sid} — {title}"
            mv_labels.append(label)
            mv_map[label] = sid

        th_labels = []
        th_map = {}
        for tid, tname, city, state in th_rows:
            label = f"{tid} — {tname} ({city}, {state})"
            th_labels.append(label)
            th_map[label] = tid

        cmb_mv = ttk.Combobox(f, values=mv_labels, width=50, state='readonly')
        cmb_th = ttk.Combobox(f, values=th_labels, width=50, state='readonly')

        e_dt = ttk.Entry(f, width=22)
        c_cc = ttk.Combobox(f, values=('0','1'), width=5, state='readonly'); c_cc.set('0')
        c_ad = ttk.Combobox(f, values=('0','1'), width=5, state='readonly'); c_ad.set('0')

        rows = (
            ('Movie', cmb_mv),
            ('Theater', cmb_th),
            ('Date (YYYY-MM-DD HH:MM:SS)', e_dt),
            ('CC (0/1)', c_cc),
            ('AD (0/1)', c_ad),
        )
        for i, (lab, w) in enumerate(rows):
            ttk.Label(f, text=lab).grid(row=i, column=0, sticky='e', padx=(0,8), pady=4)
            w.grid(row=i, column=1, sticky='w', pady=4)

        btn_inline = ttk.Frame(f)
        btn_inline.grid(row=len(rows), column=0, columnspan=2, sticky='w', pady=(6,0))
        def add_new_movie_inline():
            m = tk.Toplevel(dlg)
            m.title("Add Movie")
            m.transient(dlg); m.grab_set()
            fm = ttk.Frame(m, padding=10); fm.pack(fill='both', expand=True)
            e_title = ttk.Entry(fm, width=44)
            ttk.Label(fm, text="Title").grid(row=0, column=0, sticky='e', padx=(0,8), pady=4)
            e_title.grid(row=0, column=1, sticky='w', pady=4)
            def save_movie():
                title = e_title.get().strip()
                if not title:
                    messagebox.showwarning("Missing", "Title is required.", parent=m); return
                _exec_commit(conn, f"INSERT INTO {TABLE_MOV} ({COL_MNAME}) VALUES (%s)", (title,))
                new_rows = _exec_fetchall(conn, f"SELECT {COL_MID}, {COL_MNAME} FROM {TABLE_MOV} ORDER BY {COL_MNAME}")
                mv_labels.clear(); mv_map.clear()
                for sid, t in new_rows:
                    lab = f"{sid} — {t}"
                    mv_labels.append(lab); mv_map[lab] = sid
                cmb_mv.configure(values=mv_labels)
                m.destroy()
            bmf = ttk.Frame(fm); bmf.grid(row=2, column=0, columnspan=2, sticky='e', pady=(10,0))
            ttk.Button(bmf, text="Cancel", command=m.destroy).grid(row=0, column=0, padx=6)
            ttk.Button(bmf, text="Save", command=save_movie).grid(row=0, column=1)
            e_title.focus_set()
        ttk.Button(btn_inline, text="＋ Add New Movie", command=add_new_movie_inline).pack(side='left')

        btns = ttk.Frame(f)
        btns.grid(row=len(rows)+1, column=0, columnspan=2, sticky='e', pady=(12,0))

        def save():
            mv_label = cmb_mv.get().strip()
            th_label = cmb_th.get().strip()
            dt = e_dt.get().strip()
            if not mv_label or not th_label or not dt:
                messagebox.showwarning("Missing", "Movie/Theater/Date are required.", parent=dlg); return

            sid = mv_map.get(mv_label, None)
            tid = th_map.get(th_label, None)
            if sid is None or tid is None:
                messagebox.showerror("Invalid", "Please select valid Movie and Theater.", parent=dlg); return

            _exec_commit(
                conn,
                f"INSERT INTO {TABLE_SHOW} ({COL_SHOWID},{COL_TID},{COL_DT},{COL_IS_CC},{COL_IS_AD}) VALUES (%s,%s,%s,%s,%s)",
                (sid, tid, dt, int(c_cc.get()), int(c_ad.get()))
            )
            dlg.destroy()
            refresh_mv()
            messagebox.showinfo("Added", f"ShowDate added: show_id={sid}, theater_id={tid}", parent=win)

        ttk.Button(btns, text='Cancel', command=dlg.destroy).grid(row=0, column=0, padx=6)
        ttk.Button(btns, text='Save', command=save).grid(row=0, column=1)

        if mv_labels: cmb_mv.current(0)
        if th_labels: cmb_th.current(0)
        e_dt.focus_set()


    def edit_sd():
        sel=tv_sd.selection()
        if not sel: messagebox.showinfo('Edit ShowDate','Select a row.',parent=win); return
        sid,tid,dt,cc,ad = tv_sd.item(sel[0],'values')
        dlg=tk.Toplevel(win); dlg.title(f'Edit ShowDate {sid}/{tid}'); dlg.transient(win); dlg.grab_set()
        f=ttk.Frame(dlg,padding=12); f.pack(fill='both',expand=True)
        e_tid=ttk.Entry(f,width=12); e_tid.insert(0,tid)
        e_dt=ttk.Entry(f,width=20); e_dt.insert(0,dt)
        c_cc=ttk.Combobox(f,values=('0','1'),width=5,state='readonly'); c_cc.set(str(cc))
        c_ad=ttk.Combobox(f,values=('0','1'),width=5,state='readonly'); c_ad.set(str(ad))
        for i,(lab,w) in enumerate((('Theater ID',e_tid),('Date (YYYY-MM-DD HH:MM:SS)',e_dt),('CC(0/1)',c_cc),('AD(0/1)',c_ad))):
            ttk.Label(f,text=lab).grid(row=i,column=0,sticky='e',padx=(0,8),pady=4); w.grid(row=i,column=1,sticky='w',pady=4)
        btns=ttk.Frame(f); btns.grid(row=6,column=0,columnspan=2,sticky='e',pady=(12,0))
        def save():
            _exec_commit(conn, f"UPDATE {TABLE_SHOW} SET {COL_TID}=%s,{COL_DT}=%s,{COL_IS_CC}=%s,{COL_IS_AD}=%s WHERE {COL_SHOWID}=%s AND {COL_TID}=%s AND {COL_DT}=%s",
                         (e_tid.get().strip(), e_dt.get().strip(), int(c_cc.get()), int(c_ad.get()), sid, tid, dt))
            dlg.destroy(); refresh_mv()
        ttk.Button(btns,text='Cancel',command=dlg.destroy).grid(row=0,column=0,padx=6)
        ttk.Button(btns,text='Save',command=save).grid(row=0,column=1)

    def del_sd():
        sel=tv_sd.selection()
        if not sel: messagebox.showinfo('Delete ShowDate','Select a row.',parent=win); return
        sid,tid,dt,cc,ad = tv_sd.item(sel[0],'values')
        if not messagebox.askyesno('Confirm', f'Delete showdate for show {sid} at theater {tid} on {dt}?', parent=win): return
        _exec_commit(conn, f"DELETE FROM {TABLE_SHOW} WHERE {COL_SHOWID}=%s AND {COL_TID}=%s AND {COL_DT}=%s", (sid, tid, dt))
        refresh_mv()

    tbar3=ttk.Frame(frm_mv); tbar3.pack(fill='x', pady=(6,0))
    ttk.Button(tbar3,text='Add Movie',command=add_mv).pack(side='left',padx=3)
    ttk.Button(tbar3,text='Edit Movie',command=edit_mv).pack(side='left',padx=3)
    ttk.Button(tbar3,text='Delete Movie',command=del_mv).pack(side='left',padx=3)
    ttk.Button(tbar3,text='Add ShowDate',command=add_sd).pack(side='left',padx=14)
    ttk.Button(tbar3,text='Edit ShowDate',command=edit_sd).pack(side='left',padx=3)
    ttk.Button(tbar3,text='Delete ShowDate',command=del_sd).pack(side='left',padx=3)

    refresh_th(); refresh_ts(); refresh_mv()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cinema — Theaters")
        self.geometry("1200x720")
        self.minsize(1100, 640)

        self.conn = None
        self.cur = None

        self._build_ui()
        self._ensure_default_poster()
        self._connect_db()
        self._load_theaters()


    def _open_osm_link(self):
        if getattr(self, "_last_osm_link", None):
            webbrowser.open(self._last_osm_link)

    def _load_poster_into(self, target_label: ttk.Label, movie_title: str):
        """Load poster into the given ttk.Label (keeps a reference to avoid GC)."""
        path = self._find_poster_path(movie_title)
        if not path or not os.path.exists(path):
            target_label.configure(image="", text="(No poster)")
            target_label.image = None
            return
        try:
            im = Image.open(path)
            im.thumbnail((300, 450))
            tk_img = ImageTk.PhotoImage(im, master=target_label)
            target_label.configure(image=tk_img, text="")
            target_label.image = tk_img
            print(f"[poster] loaded into movies pane: {path}")
        except Exception as e:
            print(f"[poster] PIL failed to open {path}: {e}")
            target_label.configure(image="", text="(No poster)")
            target_label.image = None


    def _find_poster_path(self, movie_title: str) -> str:
        """
        Return a best-guess file path for the poster, or '' if nothing found.
        Tries:
        1) Exact: "<title>.<ext>" (as-is)
        2) Normalized: "<normalized>.<ext>"
        3) Case-insensitive / fuzzy scan in POSTER_DIR
        4) default.png
        """
        title_as_is = movie_title.strip()
        safe = self._normalize_filename(title_as_is)

        for ext in ALLOWED_EXTS:
            p1 = os.path.join(POSTER_DIR, title_as_is + ext)
            if os.path.exists(p1):
                print(f"[poster] exact-as-is match: {p1}")
                return p1

        for ext in ALLOWED_EXTS:
            p2 = os.path.join(POSTER_DIR, safe + ext)
            if os.path.exists(p2):
                print(f"[poster] exact-normalized match: {p2}")
                return p2

        if not os.path.isdir(POSTER_DIR):
            print(f"[poster] POSTER_DIR missing: {POSTER_DIR}")
            default_path = os.path.join(POSTER_DIR, "default.png")
            return default_path if os.path.exists(default_path) else ""

        files = [f for f in os.listdir(POSTER_DIR)
                if os.path.splitext(f)[1].lower() in ALLOWED_EXTS]

        lower_title = title_as_is.lower()
        for fname in files:
            if os.path.splitext(fname)[0].lower() == lower_title:
                p = os.path.join(POSTER_DIR, fname)
                print(f"[poster] case-insensitive direct: {p}")
                return p

        normalized_map = {}
        basenames = []
        for fname in files:
            root, ext = os.path.splitext(fname)
            norm = self._normalize_filename(root)
            normalized_map[norm] = os.path.join(POSTER_DIR, fname)
            basenames.append(norm)

        for norm, path in normalized_map.items():
            if safe in norm or norm in safe:
                print(f"[poster] loose containment: {path}")
                return path

        match = difflib.get_close_matches(safe, basenames, n=1, cutoff=0.66)
        if match:
            p = normalized_map[match[0]]
            print(f"[poster] fuzzy match: {p}")
            return p

        self._ensure_default_poster()
        if os.path.exists(POSTER_DEFAULT):
            print(f"[poster] fallback default: {POSTER_DEFAULT}")
            return POSTER_DEFAULT

        print(f"[poster] not found for title={movie_title!r}")
        return ""



    def _normalize_filename(self, name: str) -> str:
        """Convert a movie title into a safe lowercase filename."""
        base = name.lower()
        base = re.sub(r"[^a-z0-9]+", "_", base)
        base = base.strip("_")
        return base
    def _ensure_default_poster(self):
        """
        Ensure POSTER_DIR exists and a default 'question.png' poster is available.
        If not present, generate a simple 600x900 image with a centered '?'.
        """
        try:
            os.makedirs(POSTER_DIR, exist_ok=True)
            if not os.path.exists(POSTER_DEFAULT):
                w, h = 600, 900
                img = Image.new("RGB", (w, h), color=(220, 220, 220))
                draw = ImageDraw.Draw(img)

                font = None
                for cand in [
                    "arial.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    "/Library/Fonts/Arial.ttf",
                    "C:\\Windows\\Fonts\\arial.ttf",
                ]:
                    try:
                        font = ImageFont.truetype(cand, size=360)
                        break
                    except Exception:
                        pass
                if font is None:
                    font = ImageFont.load_default()

                text = "?"
                tw, th = draw.textbbox((0, 0), text, font=font)[2:]
                x = (w - tw) // 2
                y = (h - th) // 2 - 30
                draw.text((x+4, y+6), text, fill=(80, 80, 80), font=font)
                draw.text((x, y), text, fill=(30, 30, 30), font=font)

                cap = "No Poster"
                cap_font = None
                try:
                    cap_font = ImageFont.truetype(font.path if hasattr(font, "path") else "DejaVuSans.ttf", 48)
                except Exception:
                    cap_font = ImageFont.load_default()
                cw, ch = draw.textbbox((0,0), cap, font=cap_font)[2:]
                draw.text(((w - cw)//2, h - ch - 40), cap, fill=(60,60,60), font=cap_font)

                img.save(POSTER_DEFAULT, format="PNG")
        except Exception as e:
            print(f"[poster] Failed creating default poster: {e}")
    def _load_roadview_into(self, target_label: ttk.Label, theater_name: str):
        """Show road-view screenshot in the given label; fallback to question.png."""
        path = self._find_roadview_path(theater_name)
        self._ensure_default_poster()
        if not path or not os.path.exists(path):
            target_label.configure(image="", text="(No road view)")
            try:
                im = Image.open(POSTER_DEFAULT)
                im.thumbnail((600, 360))
                tk_img = ImageTk.PhotoImage(im, master=target_label)
                target_label.configure(image=tk_img, text="")
                target_label.image = tk_img
            except Exception:
                target_label.image = None
            return

        try:
            im = Image.open(path)
            im.thumbnail((600, 360))
            tk_img = ImageTk.PhotoImage(im, master=target_label)
            target_label.configure(image=tk_img, text="")
            target_label.image = tk_img
            print(f"[roadview] loaded: {path}")
        except Exception as e:
            print(f"[roadview] PIL failed to open {path}: {e}")
            target_label.configure(image="", text="(No road view)")
            target_label.image = None

    def _find_roadview_path(self, theater_name: str) -> str:
        """Find best-guess path for a road-view screenshot like 'image/road_view/<theater_name>.jpg'."""
        if not theater_name:
            return ""
        title_as_is = theater_name.strip()
        safe = self._normalize_filename(title_as_is)

        for ext in ROAD_ALLOWED_EXTS:
            p = os.path.join(ROAD_VIEW_DIR, title_as_is + ext)
            if os.path.exists(p): return p

        for ext in ROAD_ALLOWED_EXTS:
            p = os.path.join(ROAD_VIEW_DIR, safe + ext)
            if os.path.exists(p): return p

        if os.path.isdir(ROAD_VIEW_DIR):
            files = [f for f in os.listdir(ROAD_VIEW_DIR) if os.path.splitext(f)[1].lower() in ROAD_ALLOWED_EXTS]
            lt = title_as_is.lower()
            for f in files:
                if os.path.splitext(f)[0].lower() == lt:
                    return os.path.join(ROAD_VIEW_DIR, f)

        return ""
    def _fetch_theater_address(self, tid):
        if not COL_ADDR:
            return None
        try:
            cur = self.conn.cursor()
            cur.execute(f"SELECT {COL_ADDR} FROM {TABLE_THEATERS} WHERE {COL_TID}=%s", (tid,))
            r = cur.fetchone()
            return r[0] if r and r[0] else None
        except:
            return None
    def _update_right_panel_from_selection(self):
        tid, tname = self._get_selected_tid_and_name()
        self._current_tid = tid
        self._current_tname = tname
        if not tid:
            self._set_right_panel(None)
            return

        self._current_url = self._fetch_theater_url(tid)
        self.link_website.configure(text="Open theater website" if self._current_url else "")

        row = self._fetch_features(tid)
        self._set_right_panel(row)

        self._current_addr = self._fetch_theater_address(tid)

        self._load_transit_and_map(tid)

        if self._current_tname:
            self._load_roadview_into(self.roadview_label, self._current_tname)

        lat, lon = self._fetch_theater_coords(tid)
        can_gmaps = (lat is not None and lon is not None) or (self._current_tname or self._current_addr)
        if can_gmaps:
            self.btn_open_gmaps_top.state(["!disabled"])
            self.btn_open_gmaps_bottom.state(["!disabled"])
        else:
            self.btn_open_gmaps_top.state(["disabled"])
            self.btn_open_gmaps_bottom.state(["disabled"])

    def _open_google_maps(self):
        """
        Open Google Maps either by coordinates (if available) or by 'name + address' search.
        """
        lat, lon = self._fetch_theater_coords(self._current_tid) if self._current_tid else (None, None)
        url = None
        if lat is not None and lon is not None:
            url = f"https://www.google.com/maps/search/?api=1&query={lat:.6f}%2C{lon:.6f}"
        else:
            q_parts = []
            if self._current_tname: q_parts.append(self._current_tname)
            if self._current_addr: q_parts.append(self._current_addr)
            if q_parts:
                import urllib.parse
                q = urllib.parse.quote_plus(" ".join(q_parts))
                url = f"https://www.google.com/maps/search/?api=1&query={q}"
        if url:
            webbrowser.open(url)
    def _show_map_placeholder(self):
        """Hide web map and show a question-image placeholder in the same slot."""
        try:
            self._ensure_default_poster()
            if os.path.exists(POSTER_DEFAULT):
                im = Image.open(POSTER_DEFAULT)
                im.thumbnail((800, 450))
                tk_img = ImageTk.PhotoImage(im, master=self.map_placeholder)
                self.map_placeholder.configure(image=tk_img, text="")
                self.map_placeholder.image = tk_img
            else:
                self.map_placeholder.configure(image="", text="(No map)")
                self.map_placeholder.image = None
        except Exception as e:
            print(f"[map] placeholder load failed: {e}")
            self.map_placeholder.configure(image="", text="(No map)")
            self.map_placeholder.image = None

        try:
            self.map_frame.grid_remove()
        except Exception:
            pass
        self.map_placeholder.grid()

        self._last_osm_link = None
        self.btn_open_osm.state(["disabled"])
        self.btn_open_gmaps_top.state(["disabled"])
        self.btn_open_gmaps_bottom.state(["disabled"])

    def _hide_map_placeholder(self):
        """Show the web map and hide the placeholder."""
        try:
            self.map_placeholder.grid_remove()
        except Exception:
            pass
        self.map_frame.grid()
    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=8)

        self.lbl_status = ttk.Label(top, text="Not connected", foreground="#b00")
        self.lbl_status.pack(side="left")

        ttk.Button(top, text="Reconnect", command=self._reconnect).pack(side="right", padx=4)
        ttk.Button(top, text="Refresh", command=self._load_theaters).pack(side="right", padx=4)

        split = ttk.Panedwindow(self, orient="horizontal")
        split.pack(fill="both", expand=True, padx=10, pady=(0,10))

        left = ttk.Frame(split)
        split.add(left, weight=3)

        ttk.Label(left, text="Theaters (single-click: preview, double-click: movies)").pack(anchor="w", pady=(0,6))

        self.tree = ttk.Treeview(left, columns=("TID","Name","City","State","Status"), show="headings", selectmode="browse")
        for col, w in (("TID",1), ("Name",420), ("City",180), ("State",80), ("Status",120)):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="w")
        self.tree["displaycolumns"] = ("Name","City","State","Status")
        self.tree.pack(side="left", fill="both", expand=True)

        vs = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        hs = ttk.Scrollbar(left, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        vs.pack(side="right", fill="y")
        hs.pack(side="bottom", fill="x")

        self.tree.bind("<<TreeviewSelect>>", self._on_select_single)
        self.tree.bind("<Double-1>", self._on_double_click)

        right = ttk.Frame(split, padding=10)
        split.add(right, weight=2)

        ttk.Label(right, text="Accessibility", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        self.link_website = ttk.Label(right, text="", foreground="#06c", cursor="hand2")
        self.link_website.grid(row=0, column=1, sticky="e")
        self.link_website.bind("<Button-1>", lambda e: self._open_theater_url())

        ttk.Separator(right).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6,12))
        ttk.Separator(right).grid(row=16, column=0, columnspan=2, sticky="ew", pady=(8,6))
        ttk.Label(right, text="Movie Poster", font=("Segoe UI", 11, "bold")).grid(row=19, column=0, sticky="w")

        self.poster_label = ttk.Label(right, anchor="center", relief="solid", text="(No poster)")
        self.poster_label.grid(row=18, column=0, columnspan=2, sticky="nsew")
        right.rowconfigure(18, weight=1)

        self.lbl_wheel = ttk.Label(right, text="Wheelchair: —")
        self.lbl_al = ttk.Label(right, text="Assistive listening: —")
        self.lbl_cc = ttk.Label(right, text="Caption device: —")
        self.lbl_ad = ttk.Label(right, text="Audio description: —")
        self.lbl_conf = ttk.Label(right, text="Data confidence: —")

        self.lbl_wheel.grid(row=2, column=0, sticky="w", pady=3)
        self.lbl_al.grid(row=3, column=0, sticky="w", pady=3)
        self.lbl_cc.grid(row=4, column=0, sticky="w", pady=3)
        self.lbl_ad.grid(row=5, column=0, sticky="w", pady=3)
        self.lbl_conf.grid(row=6, column=0, sticky="w", pady=3)

        ttk.Label(right, text="Info source:").grid(row=7, column=0, sticky="w", pady=(8,3))
        self.link_source = ttk.Label(right, text="", foreground="#06c", cursor="hand2")
        self.link_source.grid(row=8, column=0, columnspan=2, sticky="w")
        self.link_source.bind("<Button-1>", lambda e: self._open_info_source())

        ttk.Separator(right).grid(row=9, column=0, columnspan=2, sticky="ew", pady=(10,6))
        ttk.Label(right, text="Nearby Transit (walk)", font=("Segoe UI", 11, "bold")).grid(row=10, column=0, sticky="w")

        self.tv_transit = ttk.Treeview(
            right,
            columns=("Stop","Routes","Walk","Acc"),
            show="headings",
            height=6
        )
        self.tv_transit.heading("Stop", text="Stop")
        self.tv_transit.heading("Routes",text="Routes")
        self.tv_transit.heading("Walk", text="Walk")
        self.tv_transit.heading("Acc", text="Accessible")
        self.tv_transit.column("Stop", width=180, anchor="w")
        self.tv_transit.column("Routes", width=140, anchor="w")
        self.tv_transit.column("Walk", width=80, anchor="w")
        self.tv_transit.column("Acc", width=90, anchor="w")
        self.tv_transit.grid(row=11, column=0, columnspan=2, sticky="nsew", pady=(4,6))
        right.rowconfigure(14, weight=1)
        right.columnconfigure(0, weight=1)
        ttk.Separator(right).grid(row=12, column=0, columnspan=2, sticky="ew", pady=(8,6))
        ttk.Label(right, text="Location Map", font=("Segoe UI", 11, "bold")).grid(row=13, column=0, sticky="w")

        self.map_frame = HtmlFrame(right)
        self.map_frame.grid(row=14, column=0, columnspan=2, sticky="nsew")
        right.rowconfigure(14, weight=1)
        right.columnconfigure(0, weight=1)

        self.map_placeholder = ttk.Label(right, anchor="center", relief="solid", text="(No map)")
        self.map_placeholder.grid(row=14, column=0, columnspan=2, sticky="nsew")
        self.map_placeholder.grid_remove()

        self.btn_open_osm = ttk.Button(right, text="Open in OpenStreetMap", command=self._open_osm_link)
        self.btn_open_osm.grid(row=15, column=0, columnspan=2, sticky="w", pady=(6, 0))
        self.btn_open_osm.state(["disabled"])
        self._last_osm_link = None

        self.btn_open_gmaps_top = ttk.Button(right, text="Open in Google Maps", command=self._open_google_maps)
        self.btn_open_gmaps_top.grid(row=15, column=1, sticky="e", pady=(6, 0))
        self.btn_open_gmaps_top.state(["disabled"])

        ttk.Label(right, text="Road View", font=("Segoe UI", 11, "bold")).grid(row=16, column=0, sticky="w", pady=(10, 0))
        self.roadview_label = ttk.Label(right, anchor="center", relief="solid", text="(No road view)")
        self.roadview_label.grid(row=17, column=0, columnspan=2, sticky="nsew", pady=(4, 0))

        self.btn_open_gmaps_bottom = ttk.Button(right, text="Open in Google Maps", command=self._open_google_maps)
        self.btn_open_gmaps_bottom.grid(row=18, column=0, columnspan=2, sticky="w", pady=(6, 0))
        self.btn_open_gmaps_bottom.state(["disabled"])
        self._current_tid = None
        self._current_url = None
        self._current_tname = None  
        self._current_addr = None
        self._current_src = None
        ttk.Button(
            top,
            text="Advanced Filter",
            command=self._open_analytical_queries_window,
        ).pack(side="right", padx=4)

        ttk.Button(
            top,
            text="Admin Panel",
            command=lambda: open_admin_gate(
                self,
                lambda: open_admin_panel(self, self.conn if (self.conn and self.cur) else mysql.connector.connect(**DB_CONFIG))
            )
        ).pack(side="right", padx=4)


    def _connect_db(self):
        self._close_db()
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.cur = self.conn.cursor()
            self._set_status(True, f"Connected: {DB_CONFIG['user']}@{DB_CONFIG['host']} / {DB_CONFIG['database']}")
            self.conn.autocommit = True
        except Error as e:
            self._set_status(False, f"Connection failed: {e}")
            messagebox.showerror("DB Error", f"Failed to connect:\n{e}")
        
    def _reconnect(self):
        self._connect_db()
        self._load_theaters()

    def _close_db(self):
        try:
            if self.cur: self.cur.close()
        except:
            pass
        try:
            if self.conn: self.conn.close()
        except:
            pass
        self.cur = None
        self.conn = None

    def _set_status(self, ok: bool, msg: str):
        self.lbl_status.configure(text=msg, foreground=("#2a7" if ok else "#b00"))

    def _load_theaters(self):
        if not (self.conn and self.cur):
            self._connect_db()
            if not (self.conn and self.cur):
                return
        try:
            self.cur.execute(build_list_query())
            rows = self.cur.fetchall()
            for i in self.tree.get_children():
                self.tree.delete(i)
            for r in rows:
                self.tree.insert("", "end", values=r)
            self._set_status(True, f"Loaded {len(rows)} theaters. Single-click to preview, double-click for movies.")
            if rows:
                first = self.tree.get_children()[0]
                self.tree.selection_set(first)
                self.tree.focus(first)
                self._update_right_panel_from_selection()
        except Error as e:
            self._set_status(False, f"Query failed: {e}")
            messagebox.showerror("Query Error", f"{e}")

    def _on_select_single(self, _event):
        self._update_right_panel_from_selection()

    def _on_double_click(self, _event):
        tid, name = self._get_selected_tid_and_name()
        if not tid:
            return
        self._open_movies_window(tid, name)

    def _get_selected_tid_and_name(self):
        sel = self.tree.selection()
        if not sel:
            return None, None
        vals = self.tree.item(sel[0], "values")
        return vals[0], vals[1]


    def _fetch_theater_url(self, tid):
        if not COL_URL:
            return None
        try:
            cur = self.conn.cursor()
            cur.execute(f"SELECT {COL_URL} FROM {TABLE_THEATERS} WHERE {COL_TID} = %s", (tid,))
            r = cur.fetchone()
            return r[0] if r and r[0] else None
        except:
            return None

    def _fetch_features(self, tid):
        try:
            cur = self.conn.cursor()
            cur.execute(build_features_query(), (tid,))
            return cur.fetchone()
        except Error as e:
            messagebox.showerror("DB Error", f"Failed to load accessibility:\n{e}")
            return None

    def _set_right_panel(self, feat_row):
        if feat_row:
            wheel, al, cc, ad, src, conf = feat_row
            self.lbl_wheel.configure(text=f"Wheelchair: {bool_mark(wheel)}")
            self.lbl_al.configure(text=f"Assistive listening: {bool_mark(al)}")
            self.lbl_cc.configure(text=f"Caption device: {bool_mark(cc)}")
            self.lbl_ad.configure(text=f"Audio description: {bool_mark(ad)}")
            self.lbl_conf.configure(text=f"Data confidence: {conf if conf is not None else '—'}")

            self._current_src = src if src else None
            self.link_source.configure(text=(src or ""))
        else:
            self.lbl_wheel.configure(text="Wheelchair: —")
            self.lbl_al.configure(text="Assistive listening: —")
            self.lbl_cc.configure(text="Caption device: —")
            self.lbl_ad.configure(text="Audio description: —")
            self.lbl_conf.configure(text="Data confidence: —")
            self._current_src = None
            self.link_source.configure(text="")

    def _open_movies_window(self, tid, tname):
        """선택한 극장에서 상영 중인 영화 목록(더블클릭: 상영일/CC/AD). Single-click shows poster on the right."""
        try:
            cur = self.conn.cursor()
            cur.execute(build_movies_for_theater_query(), (tid,))
            rows = cur.fetchall()
        except Error as e:
            messagebox.showerror("DB Error", f"Failed to load movies:\n{e}")
            return

        win = tk.Toplevel(self)
        win.title(f"Movies — {tname} (ID {tid})")
        win.geometry("820x520")
        win.minsize(780, 460)

        pw = ttk.Panedwindow(win, orient="horizontal")
        pw.pack(fill="both", expand=True, padx=8, pady=8)

        left = ttk.Frame(pw)
        pw.add(left, weight=3)

        cols = ("Title", "Shows")
        tv = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse", height=18)
        tv.heading("Title", text="Title")
        tv.heading("Shows", text="#Shows")
        tv.column("Title", width=420, anchor="w")
        tv.column("Shows", width=80, anchor="e")
        tv.pack(side="left", fill="both", expand=True)

        vs = ttk.Scrollbar(left, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=vs.set)
        vs.pack(side="left", fill="y")

        for show_id, title, cnt in rows:
            iid = f"S{show_id}"
            tv.insert("", "end", iid=iid, values=(title, cnt))

        right = ttk.Frame(pw, padding=(10, 0, 0, 0))
        pw.add(right, weight=2)
        ttk.Label(right, text="Poster", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))
        poster_holder = ttk.Label(right, anchor="center", relief="solid", text="(No poster)")
        poster_holder.pack(fill="both", expand=True)

        def on_select(_e=None):
            sel = tv.selection()
            if not sel:
                return
            iid = sel[0]
            title = tv.item(iid, "values")[0]
            self._load_poster_into(poster_holder, title)

        tv.bind("<<TreeviewSelect>>", on_select)

        def on_movie_dclick(evt):
            row_id = tv.identify_row(evt.y) or (tv.selection()[0] if tv.selection() else "")
            if not row_id:
                return
            iid = row_id
            show_id = iid[1:] if iid.startswith("S") else tv.item(iid, "values")[0]
            title = tv.item(iid, "values")[0]
            self._open_showdates_window(tid, show_id, title)

        tv.bind("<Double-1>", on_movie_dclick)

        first = tv.get_children()
        if first:
            tv.selection_set(first[0])
            tv.focus(first[0])
            on_select()


    def _open_showdates_window(self, tid, show_id, movie_title):
        """특정 극장+영화(show_id)의 상영일/CC/AD"""
        try:
            cur = self.conn.cursor()
            cur.execute(build_showdates_for_movie_query(), (tid, show_id))
            rows = cur.fetchall()
        except Error as e:
            messagebox.showerror("DB Error", f"Failed to load show dates:\n{e}")
            return

        win = tk.Toplevel(self)
        win.title(f"Showtimes — {movie_title} @ Theater {tid} (show_id={show_id})")
        win.geometry("620x480")
        win.minsize(560, 420)

        cols = ("Date/Time", "CC", "AD")
        tv = ttk.Treeview(win, columns=cols, show="headings", selectmode="browse")
        tv.heading("Date/Time", text="Date/Time")
        tv.heading("CC", text="CC")
        tv.heading("AD", text="AD")
        tv.column("Date/Time", width=380, anchor="w")
        tv.column("CC", width=80, anchor="center")
        tv.column("AD", width=80, anchor="center")
        tv.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        vs = ttk.Scrollbar(win, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=vs.set)
        vs.pack(side="right", fill="y")

        for dt, iscc, isad in rows:
            tv.insert("", "end", values=(dt, "✔" if iscc else "✖", "✔" if isad else "✖"))

    def _open_showtimes_window(self, tid, tname):
        try:
            cur = self.conn.cursor()
            cur.execute(build_showtimes_query(), (tid,))
            rows = cur.fetchall()
        except Error as e:
            messagebox.showerror("DB Error", f"Failed to load showtimes:\n{e}")
            return

        win = tk.Toplevel(self)
        win.title(f"Showtimes — {tname} (ID {tid})")
        win.geometry("800x520")
        win.minsize(720, 460)

        cols = ("Date/Time","Movie","CC","AD")
        tv = ttk.Treeview(win, columns=cols, show="headings")
        for c, w in (("Date/Time",220), ("Movie",280), ("CC",60), ("AD",60)):
            tv.heading(c, text=c)
            tv.column(c, width=w, anchor="w")
        tv.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        vs = ttk.Scrollbar(win, orient="vertical", command=tv.yview)
        tv.configure(yscrollcommand=vs.set)
        vs.pack(side="right", fill="y")

        for dt, mname, iscc, isad in rows:
            tv.insert("", "end", values=(dt, mname, "✔" if iscc else "✖", "✔" if isad else "✖"))   
    def _open_analytical_queries_window(self):
        win = tk.Toplevel(self)
        win.title("Advanced Filter")
        win.geometry("920x520")
        win.minsize(880, 480)

        query_meta = [
            {
                "id": 1,
                "title": "1. Short average walk time (by city)",
                "desc": (
                    "For a given city, list theaters that are connected to at least one "
                    "accessible transit stop where the AVERAGE walking time is below "
                    "a user-entered threshold (in minutes)."
                ),
            },
            {
                "id": 2,
                "title": "2. Accessible showings in the next N days",
                "desc": (
                    "List all movies that will be shown in the next N days that are "
                    "either captioned OR audio-described. Optionally filter by city."
                ),
            },
            {
                "id": 3,
                "title": "3. Theaters with at least K accessibility features (by city)",
                "desc": (
                    "For a given city, find theaters where the total number of enabled "
                    "accessibility features (wheelchair, assistive listening, captions, "
                    "audio description) is greater than or equal to a user-entered K."
                ),
            },
            {
                "id": 4,
                "title": "4. City-level accessibility summary (by state)",
                "desc": (
                    "For a given state, compute per-city summary: total theaters, "
                    "number of wheelchair-accessible theaters, and average walking "
                    "distance to accessible transit stops (in meters)."
                ),
            },
            {
                "id": 5,
                "title": "5. Transit routes serving at least K theaters",
                "desc": (
                    "Find transit routes that serve accessible stops which are linked "
                    "to at least K different theaters."
                ),
            },
        ]

        current_query_id = tk.IntVar(value=query_meta[0]["id"])
        param_widgets = {}

        pw = ttk.Panedwindow(win, orient="horizontal")
        pw.pack(fill="both", expand=True, padx=8, pady=8)

        left = ttk.Frame(pw, padding=(0, 0, 8, 0))
        pw.add(left, weight=1)

        tv = ttk.Treeview(left, columns=("title",), show="headings", selectmode="browse", height=15)
        tv.heading("title", text="Query")
        tv.column("title", width=260, anchor="w")
        tv.pack(fill="both", expand=True)

        for idx, meta in enumerate(query_meta):
            tv.insert("", "end", iid=f"Q{idx}", values=(meta["title"],))

        right = ttk.Frame(pw)
        pw.add(right, weight=2)

        ttk.Label(right, text="Description", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        txt_desc = tk.Text(right, height=4, wrap="word")
        txt_desc.pack(fill="x", expand=False, pady=(0, 6))

        ttk.Label(right, text="Parameters", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        param_frame = ttk.Frame(right)
        param_frame.pack(fill="x", expand=False, pady=(2, 6))

        btn_frame = ttk.Frame(right)
        btn_frame.pack(fill="x", pady=(6, 0))

        def build_param_ui(qid: int):
            """쿼리 ID에 따라 파라미터 입력 위젯를 다시 구성."""
            nonlocal param_widgets
            for child in param_frame.winfo_children():
                child.destroy()
            param_widgets = {}

            if qid == 1:
                ttk.Label(param_frame, text="City:").grid(row=0, column=0, sticky="e", padx=(0, 8), pady=4)
                e_city = ttk.Entry(param_frame, width=24)
                e_city.grid(row=0, column=1, sticky="w", pady=4)
                ttk.Label(param_frame, text="Max average walk time (minutes):").grid(
                    row=1, column=0, sticky="e", padx=(0, 8), pady=4
                )
                e_max = ttk.Entry(param_frame, width=10)
                e_max.grid(row=1, column=1, sticky="w", pady=4)
                e_max.insert(0, "3")
                param_widgets["city"] = e_city
                param_widgets["max_min"] = e_max

            elif qid == 2:
                ttk.Label(param_frame, text="Days ahead (N):").grid(row=0, column=0, sticky="e", padx=(0, 8), pady=4)
                e_days = ttk.Entry(param_frame, width=10)
                e_days.grid(row=0, column=1, sticky="w", pady=4)
                e_days.insert(0, "7")

                ttk.Label(param_frame, text="City (optional, blank = ALL):").grid(
                    row=1, column=0, sticky="e", padx=(0, 8), pady=4
                )
                e_city = ttk.Entry(param_frame, width=24)
                e_city.grid(row=1, column=1, sticky="w", pady=4)

                param_widgets["days"] = e_days
                param_widgets["city"] = e_city

            elif qid == 3:
                ttk.Label(param_frame, text="City:").grid(row=0, column=0, sticky="e", padx=(0, 8), pady=4)
                e_city = ttk.Entry(param_frame, width=24)
                e_city.grid(row=0, column=1, sticky="w", pady=4)

                ttk.Label(param_frame, text="Min feature count (1-4):").grid(
                    row=1, column=0, sticky="e", padx=(0, 8), pady=4
                )
                e_min = ttk.Entry(param_frame, width=10)
                e_min.grid(row=1, column=1, sticky="w", pady=4)
                e_min.insert(0, "2")

                param_widgets["city"] = e_city
                param_widgets["min_features"] = e_min

            elif qid == 4:
                ttk.Label(param_frame, text="State:").grid(row=0, column=0, sticky="e", padx=(0, 8), pady=4)
                cmb_state = ttk.Combobox(param_frame, values=US_STATES, width=8, state="readonly")
                cmb_state.grid(row=0, column=1, sticky="w", pady=4)
                if US_STATES:
                    cmb_state.set(US_STATES[0])
                param_widgets["state"] = cmb_state

            elif qid == 5:
                ttk.Label(param_frame, text="Min theater count per route:").grid(
                    row=0, column=0, sticky="e", padx=(0, 8), pady=4
                )
                e_min = ttk.Entry(param_frame, width=10)
                e_min.grid(row=0, column=1, sticky="w", pady=4)
                e_min.insert(0, "1")
                param_widgets["min_theaters"] = e_min

        def on_select(_e=None):
            sel = tv.selection()
            if not sel:
                return
            iid = sel[0]
            idx = int(iid[1:])
            meta = query_meta[idx]
            qid = meta["id"]
            current_query_id.set(qid)

            txt_desc.delete("1.0", "end")
            txt_desc.insert("1.0", meta["desc"])

            build_param_ui(qid)

        tv.bind("<<TreeviewSelect>>", on_select)

        def run_query():
            qid = current_query_id.get()

            if qid == 1:
                city = param_widgets["city"].get().strip()
                max_min_s = param_widgets["max_min"].get().strip()
                if not city or not max_min_s:
                    messagebox.showwarning("Missing", "Please enter city and max average minutes.", parent=win)
                    return
                try:
                    max_min = float(max_min_s)
                except ValueError:
                    messagebox.showwarning("Invalid", "Max average minutes must be a number.", parent=win)
                    return

                sql = f"""
SELECT
    t.{COL_NAME} AS theater_name,
    t.{COL_ADDR} AS address,
    t.{COL_CITY} AS city,
    t.{COL_STATE} AS state,
    MIN(tt.{TT_WALK_M}) AS min_walk_distance_m,
    AVG(tt.{TT_WALK_MIN}) AS avg_walk_time_min
FROM {TABLE_THEATERS} AS t
JOIN {TABLE_TTRANSIT} AS tt
  ON t.{COL_TID} = tt.{TT_THEATER_ID}
JOIN {TABLE_TSTOPS} AS ts
  ON ts.{TS_STOP_ID} = tt.{TT_STOP_ID}
WHERE t.{COL_CITY} = %s
  AND ts.{TS_ACCESSIBLE} = 1
GROUP BY t.{COL_TID}, t.{COL_NAME}, t.{COL_ADDR}, t.{COL_CITY}, t.{COL_STATE}
HAVING AVG(tt.{TT_WALK_MIN}) <= %s
ORDER BY avg_walk_time_min ASC;
""".strip()

                self._execute_and_show_query(
                    win,
                    f"Q1 — Theaters in {city} with avg walk ≤ {max_min} min",
                    sql,
                    (city, max_min),
                )

            elif qid == 2:
                days_s = param_widgets["days"].get().strip()
                city = param_widgets["city"].get().strip()
                if not days_s:
                    messagebox.showwarning("Missing", "Please enter number of days.", parent=win)
                    return
                try:
                    days = int(days_s)
                except ValueError:
                    messagebox.showwarning("Invalid", "Days must be an integer.", parent=win)
                    return

                sql = f"""
SELECT
    m.{COL_MNAME} AS movie_title,
    t.{COL_NAME} AS theater_name,
    t.{COL_CITY} AS city,
    t.{COL_STATE} AS state,
    sd.{COL_DT} AS show_date,
    sd.{COL_IS_CC} AS is_captioned,
    sd.{COL_IS_AD} AS is_audio_described
FROM {TABLE_MOV} AS m
JOIN {TABLE_SHOW} AS sd
  ON m.{COL_MID} = sd.{COL_SHOWID}
JOIN {TABLE_THEATERS} AS t
  ON t.{COL_TID} = sd.{COL_TID}
WHERE sd.{COL_DT} BETWEEN CURDATE()
                      AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
  AND (sd.{COL_IS_CC} = 1 OR sd.{COL_IS_AD} = 1)
  AND (%s = '' OR t.{COL_CITY} = %s)
ORDER BY sd.{COL_DT}, m.{COL_MNAME};
""".strip()

                params = (days, city, city)
                title = f"Q2 — Accessible showings in next {days} days"
                if city:
                    title += f" (city = {city})"

                self._execute_and_show_query(win, title, sql, params)

            elif qid == 3:
                city = param_widgets["city"].get().strip()
                min_f_s = param_widgets["min_features"].get().strip()
                if not city or not min_f_s:
                    messagebox.showwarning("Missing", "Please enter city and min feature count.", parent=win)
                    return
                try:
                    min_f = int(min_f_s)
                except ValueError:
                    messagebox.showwarning("Invalid", "Min feature count must be an integer.", parent=win)
                    return

                sql = f"""
SELECT
    t.{COL_NAME} AS theater_name,
    t.{COL_CITY} AS city,
    t.{COL_STATE} AS state,
    (tf.{COL_WHEEL} +
     tf.{COL_AL} +
     tf.{COL_CC} +
     tf.{COL_AD}) AS feature_count
FROM {TABLE_THEATERS} AS t
JOIN {TABLE_FEAT} AS tf
  ON t.{COL_TID} = tf.{COL_TID}
WHERE t.{COL_CITY} = %s
  AND (tf.{COL_WHEEL} +
       tf.{COL_AL} +
       tf.{COL_CC} +
       tf.{COL_AD}) >= %s
ORDER BY feature_count DESC, t.{COL_NAME};
""".strip()

                self._execute_and_show_query(
                    win,
                    f"Q3 — Theaters in {city} with ≥ {min_f} accessibility features",
                    sql,
                    (city, min_f),
                )

            elif qid == 4:
                state = param_widgets["state"].get().strip()
                if not state:
                    messagebox.showwarning("Missing", "Please select a state.", parent=win)
                    return

                sql = f"""
SELECT
    t.{COL_CITY} AS city,
    COUNT(DISTINCT t.{COL_TID}) AS total_theaters,
    SUM(tf.{COL_WHEEL}) AS wheelchair_theaters,
    AVG(tt.{TT_WALK_M}) AS avg_walk_distance_m
FROM {TABLE_THEATERS} AS t
JOIN {TABLE_FEAT} AS tf
  ON t.{COL_TID} = tf.{COL_TID}
LEFT JOIN {TABLE_TTRANSIT} AS tt
  ON t.{COL_TID} = tt.{TT_THEATER_ID}
LEFT JOIN {TABLE_TSTOPS} AS ts
  ON ts.{TS_STOP_ID} = tt.{TT_STOP_ID}
  AND ts.{TS_ACCESSIBLE} = 1
WHERE t.{COL_STATE} = %s
GROUP BY t.{COL_CITY}
ORDER BY total_theaters DESC;
""".strip()

                self._execute_and_show_query(
                    win,
                    f"Q4 — City-level summary for state {state}",
                    sql,
                    (state,),
                )

            elif qid == 5:
                min_t_s = param_widgets["min_theaters"].get().strip()
                if not min_t_s:
                    messagebox.showwarning("Missing", "Please enter minimum theater count.", parent=win)
                    return
                try:
                    min_t = int(min_t_s)
                except ValueError:
                    messagebox.showwarning("Invalid", "Minimum theater count must be an integer.", parent=win)
                    return

                sql = f"""
SELECT
    sr.{SR_ROUTE} AS route,
    COUNT(DISTINCT tt.{TT_THEATER_ID}) AS accessible_theater_count
FROM {TABLE_SROUTES} AS sr
JOIN {TABLE_TTRANSIT} AS tt
  ON sr.{SR_STOP_ID} = tt.{TT_STOP_ID}
JOIN {TABLE_TSTOPS} AS ts
  ON ts.{TS_STOP_ID} = sr.{SR_STOP_ID}
WHERE ts.{TS_ACCESSIBLE} = 1
GROUP BY sr.{SR_ROUTE}
HAVING accessible_theater_count >= %s
ORDER BY accessible_theater_count DESC;
""".strip()

                self._execute_and_show_query(
                    win,
                    f"Q5 — Routes with ≥ {min_t} theaters reachable via accessible stops",
                    sql,
                    (min_t,),
                )

        ttk.Button(btn_frame, text="Run Query", command=run_query).pack(side="right")

        children = tv.get_children()
        if children:
            tv.selection_set(children[0])
            tv.focus(children[0])
            on_select()
    
    def _execute_and_show_query(self, parent, title: str, sql: str, params: tuple):
        """
        주어진 SQL과 파라미터를 실행하고, 결과를 새 창(Treeview)으로 보여준다.
        """
        if not (self.conn and self.cur):
            self._connect_db()
            if not (self.conn and self.cur):
                return

        try:
            cur = self.conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description] if cur.description else []
            cur.close()
        except Error as e:
            messagebox.showerror("DB Error", f"Failed to run query:\n{e}", parent=parent)
            return

        res = tk.Toplevel(self)
        res.title(title)
        res.geometry("900x450")

        tv_res = ttk.Treeview(res, columns=cols, show="headings")
        for c in cols:
            tv_res.heading(c, text=c)
            tv_res.column(c, width=140, anchor="w")
        tv_res.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        sb = ttk.Scrollbar(res, orient="vertical", command=tv_res.yview)
        tv_res.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        for r in rows:
            tv_res.insert("", "end", values=r)

    def _load_transit_and_map(self, theater_id: int, limit: int = 8):
        """Load nearest transit stops and update the map."""
        for item in self.tv_transit.get_children():
            self.tv_transit.delete(item)

        theater_lat, theater_lon = self._fetch_theater_coords(theater_id)

        latlon_select = ""
        group_by_extra = ""
        if TS_LAT and TS_LON:
            latlon_select = f", ts.{TS_LAT} AS stop_lat, ts.{TS_LON} AS stop_lon"
            group_by_extra = f", ts.{TS_LAT}, ts.{TS_LON}"
        
        q = f"""
            SELECT ts.{TS_NAME} AS stop_name,
                   COALESCE(GROUP_CONCAT(sr.{SR_ROUTE} ORDER BY sr.{SR_ROUTE} SEPARATOR ', '), '') AS routes,
                   tt.{TT_WALK_MIN} AS walk_min,
                   ts.{TS_ACCESSIBLE} AS acc
                   {latlon_select}
            FROM {TABLE_TTRANSIT} tt
            JOIN {TABLE_TSTOPS} ts ON ts.{TS_STOP_ID} = tt.{TT_STOP_ID}
            LEFT JOIN {TABLE_SROUTES} sr ON sr.{SR_STOP_ID} = ts.{TS_STOP_ID}
            WHERE tt.{TT_THEATER_ID} = %s
            GROUP BY ts.{TS_STOP_ID}, ts.{TS_NAME}, tt.{TT_WALK_MIN}, ts.{TS_ACCESSIBLE}{group_by_extra}
            ORDER BY tt.{TT_WALK_MIN} ASC
            LIMIT {limit};
        """

        stops = []
        try:
            cur = self.conn.cursor()
            cur.execute(q, (theater_id,))
            rows = cur.fetchall()
            idx_stop = 0
            idx_routes = 1
            idx_walk = 2
            idx_acc = 3
            idx_lat = 4 if TS_LAT and TS_LON else None
            idx_lon = 5 if TS_LAT and TS_LON else None

            for r in rows:
                stop_name = r[idx_stop]
                routes = r[idx_routes] or ""
                walk_min = r[idx_walk]
                acc = r[idx_acc]
                acc_disp = "✔" if (str(acc).strip().lower() in {"1","true","yes","y"}) else "✖"

                self.tv_transit.insert("", "end", values=(stop_name, routes, f"{walk_min}m", acc_disp))

                if idx_lat is not None and r[idx_lat] is not None and r[idx_lon] is not None:
                    stops.append({
                        "name": stop_name,
                        "routes": routes,
                        "lat": float(r[idx_lat]),
                        "lon": float(r[idx_lon]),
                        "walk": walk_min,
                        "acc": bool(str(acc).strip().lower() in {"1","true","yes","y"}),
                    })
        except Error as e:
            messagebox.showerror("DB Error", f"Failed to load transit:\n{e}")
            stops = []

        self._render_map_leaflet(theater_lat, theater_lon, stops)

    def _fetch_theater_coords(self, theater_id: int):
        if not COL_T_LAT or not COL_T_LON:
            return None, None
        try:
            cur = self.conn.cursor()
            cur.execute(
                f"SELECT {COL_T_LAT}, {COL_T_LON} FROM {TABLE_THEATERS} WHERE {COL_TID}=%s",
                (theater_id,)
            )
            row = cur.fetchone()
            if row and row[0] is not None and row[1] is not None:
                return float(row[0]), float(row[1])
        except:
            pass
        return None, None

    def _render_map_leaflet(self, theater_lat, theater_lon, stops: list):
        has_theater = theater_lat is not None and theater_lon is not None
        stops_with_coords = [s for s in stops if s.get("lat") is not None and s.get("lon") is not None]
        has_stops = len(stops_with_coords) > 0

        if not has_theater and not has_stops:
            self._show_map_placeholder()
            return

        self._hide_map_placeholder()

        if has_theater:
            clat, clon = float(theater_lat), float(theater_lon)
        else:
            first = stops_with_coords[0]
            clat, clon = float(first['lat']), float(first['lon'])

        zoom = 15
        map_url = f"https://www.openstreetmap.org/?mlat={clat:.6f}&mlon={clon:.6f}#map={zoom}/{clat:.6f}/{clon:.6f}"

        try:
            self.map_frame.load_url(map_url)
        except Exception as e:
            print(f"[map] HtmlFrame load failed: {e}")
            self._show_map_placeholder()
            return

        self._last_osm_link = map_url
        self.btn_open_osm.state(["!disabled"])

        can_gmaps = True
        if can_gmaps:
            self.btn_open_gmaps_top.state(["!disabled"])
            self.btn_open_gmaps_bottom.state(["!disabled"])


    def _open_theater_url(self):
        if self._current_url:
            webbrowser.open(self._current_url)

    def _open_info_source(self):
        if self._current_src:
            webbrowser.open(self._current_src)

    def destroy(self):
        try:
            if self.cur: self.cur.close()
            if self.conn: self.conn.close()
        finally:
            super().destroy()


if __name__ == "__main__":

    App().mainloop()
