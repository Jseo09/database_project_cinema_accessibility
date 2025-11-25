import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
from typing import Optional, Callable

from config import (
    APP_DIR, DB_CONFIG,
    TABLE_THEATERS, COL_TID, COL_NAME, COL_CITY, COL_STATE, COL_STATUS,
    COL_URL, COL_ADDR, COL_T_LAT, COL_T_LON, COL_PHONE,
    TABLE_FEAT, COL_WHEEL, COL_AL, COL_CC, COL_AD, COL_SRC, COL_CONF,
    TABLE_SHOW, COL_SHOWID, COL_DT, COL_IS_CC, COL_IS_AD,
    TABLE_MOV, COL_MID, COL_MNAME,
    TABLE_TSTOPS, TS_STOP_ID, TS_NAME, TS_ACCESSIBLE, TS_LAT, TS_LON,
    US_STATES, STATUS_CHOICES,
)

from db_utils import exec_fetchall, exec_commit

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
        rows = exec_fetchall(conn, f"SELECT {COL_TID},{COL_NAME},{COL_CITY},{COL_STATE},{COL_STATUS},{COL_URL} FROM {TABLE_THEATERS} ORDER BY {COL_CITY},{COL_NAME}")
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
            exec_commit(conn, f"UPDATE {TABLE_THEATERS} SET {COL_NAME}=%s,{COL_CITY}=%s,{COL_STATE}=%s,{COL_STATUS}=%s,{COL_URL}=%s WHERE {COL_TID}=%s",
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
            exec_commit(conn, f"DELETE FROM {TABLE_THEATERS} WHERE {COL_TID}=%s", (tid,))
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
        rows = exec_fetchall(conn, f"SELECT {TS_STOP_ID},{TS_NAME},{TS_ACCESSIBLE},{TS_LAT},{TS_LON} FROM {TABLE_TSTOPS} ORDER BY {TS_NAME}")
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

            exec_commit(
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
            exec_commit(conn, f"UPDATE {TABLE_TSTOPS} SET {TS_NAME}=%s,{TS_ACCESSIBLE}=%s,{TS_LAT}=%s,{TS_LON}=%s WHERE {TS_STOP_ID}=%s",
                         (e_nm.get().strip(), c_acc.get().strip(), (e_lat.get().strip() or None), (e_lon.get().strip() or None), sid))
            dlg.destroy(); refresh_ts()
        ttk.Button(btns,text='Cancel',command=dlg.destroy).grid(row=0,column=0,padx=6)
        ttk.Button(btns,text='Save',command=save).grid(row=0,column=1)

    def del_ts():
        sel=tv_ts.selection()
        if not sel: messagebox.showinfo("Delete Stop","Select a stop.",parent=win); return
        sid=tv_ts.item(sel[0],"values")[0]
        if not messagebox.askyesno("Confirm", f"Delete stop {sid}?", parent=win): return
        exec_commit(conn, f"DELETE FROM {TABLE_TSTOPS} WHERE {TS_STOP_ID}=%s", (sid,)); refresh_ts()

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
        rows = exec_fetchall(conn, f"SELECT {COL_MID},{COL_MNAME} FROM {TABLE_MOV} ORDER BY {COL_MNAME}")
        for r in rows: tv_mv.insert('', 'end', values=r)
        refresh_sd()

    def refresh_sd(show_id=None):
        tv_sd.delete(*tv_sd.get_children())
        if show_id is None:
            rows = exec_fetchall(conn, f"SELECT {COL_SHOWID},{COL_TID},{COL_DT},{COL_IS_CC},{COL_IS_AD} FROM {TABLE_SHOW} ORDER BY {COL_DT} DESC LIMIT 200")
        else:
            rows = exec_fetchall(conn, f"SELECT {COL_SHOWID},{COL_TID},{COL_DT},{COL_IS_CC},{COL_IS_AD} FROM {TABLE_SHOW} WHERE {COL_SHOWID}=%s ORDER BY {COL_DT} DESC", (show_id,))
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
            exec_commit(conn, f"UPDATE {TABLE_MOV} SET {COL_MNAME}=%s WHERE {COL_MID}=%s", (e_t.get().strip(), sid))
            dlg.destroy(); refresh_mv()
        ttk.Button(btns,text='Cancel',command=dlg.destroy).grid(row=0,column=0,padx=6)
        ttk.Button(btns,text='Save',command=save).grid(row=0,column=1)

    def del_mv():
        sel=tv_mv.selection()
        if not sel: messagebox.showinfo('Delete Movie','Select a movie.',parent=win); return
        sid=tv_mv.item(sel[0],'values')[0]
        if not messagebox.askyesno('Confirm', f'Delete movie {sid}? (Make sure SHOWDATES are handled)', parent=win): return
        exec_commit(conn, f"DELETE FROM {TABLE_MOV} WHERE {COL_MID}=%s", (sid,)); refresh_mv()
    
    def add_sd():
        dlg = tk.Toplevel(win)
        dlg.title('Add ShowDate')
        dlg.transient(win)
        dlg.grab_set()

        f = ttk.Frame(dlg, padding=12)
        f.pack(fill='both', expand=True)

        mv_rows = exec_fetchall(conn, f"SELECT {COL_MID}, {COL_MNAME} FROM {TABLE_MOV} ORDER BY {COL_MNAME}")
        th_rows = exec_fetchall(conn, f"SELECT {COL_TID}, {COL_NAME}, {COL_CITY}, {COL_STATE} FROM {TABLE_THEATERS} ORDER BY {COL_CITY},{COL_NAME}")

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
                exec_commit(conn, f"INSERT INTO {TABLE_MOV} ({COL_MNAME}) VALUES (%s)", (title,))
                new_rows = exec_fetchall(conn, f"SELECT {COL_MID}, {COL_MNAME} FROM {TABLE_MOV} ORDER BY {COL_MNAME}")
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

            exec_commit(
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
            exec_commit(conn, f"UPDATE {TABLE_SHOW} SET {COL_TID}=%s,{COL_DT}=%s,{COL_IS_CC}=%s,{COL_IS_AD}=%s WHERE {COL_SHOWID}=%s AND {COL_TID}=%s AND {COL_DT}=%s",
                         (e_tid.get().strip(), e_dt.get().strip(), int(c_cc.get()), int(c_ad.get()), sid, tid, dt))
            dlg.destroy(); refresh_mv()
        ttk.Button(btns,text='Cancel',command=dlg.destroy).grid(row=0,column=0,padx=6)
        ttk.Button(btns,text='Save',command=save).grid(row=0,column=1)

    def del_sd():
        sel=tv_sd.selection()
        if not sel: messagebox.showinfo('Delete ShowDate','Select a row.',parent=win); return
        sid,tid,dt,cc,ad = tv_sd.item(sel[0],'values')
        if not messagebox.askyesno('Confirm', f'Delete showdate for show {sid} at theater {tid} on {dt}?', parent=win): return
        exec_commit(conn, f"DELETE FROM {TABLE_SHOW} WHERE {COL_SHOWID}=%s AND {COL_TID}=%s AND {COL_DT}=%s", (sid, tid, dt))
        refresh_mv()

    tbar3=ttk.Frame(frm_mv); tbar3.pack(fill='x', pady=(6,0))
    ttk.Button(tbar3,text='Add Movie',command=add_mv).pack(side='left',padx=3)
    ttk.Button(tbar3,text='Edit Movie',command=edit_mv).pack(side='left',padx=3)
    ttk.Button(tbar3,text='Delete Movie',command=del_mv).pack(side='left',padx=3)
    ttk.Button(tbar3,text='Add ShowDate',command=add_sd).pack(side='left',padx=14)
    ttk.Button(tbar3,text='Edit ShowDate',command=edit_sd).pack(side='left',padx=3)
    ttk.Button(tbar3,text='Delete ShowDate',command=del_sd).pack(side='left',padx=3)

    refresh_th(); refresh_ts(); refresh_mv()

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
