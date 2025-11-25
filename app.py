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

# NEW: import our config + helpers + admin UI
from config import (
    APP_DIR, DB_CONFIG,
    TABLE_THEATERS, COL_TID, COL_NAME, COL_CITY, COL_STATE, COL_STATUS,
    COL_URL, COL_ADDR, COL_T_LAT, COL_T_LON, COL_PHONE,
    ROAD_VIEW_DIR, ROAD_ALLOWED_EXTS,
    TABLE_FEAT, COL_WHEEL, COL_AL, COL_CC, COL_AD, COL_SRC, COL_CONF,
    TABLE_SHOW, COL_SHOWID, COL_DT, COL_IS_CC, COL_IS_AD,
    TABLE_MOV, COL_MID, COL_MNAME,
    TABLE_TTRANSIT, TT_THEATER_ID, TT_STOP_ID, TT_WALK_M, TT_WALK_MIN,
    TABLE_TSTOPS, TS_STOP_ID, TS_NAME, TS_ACCESSIBLE, TS_LAT, TS_LON,
    TABLE_SROUTES, SR_STOP_ID, SR_ROUTE,
    POSTER_DIR, POSTER_DEFAULT, ALLOWED_EXTS,
    US_STATES, STATUS_CHOICES,
)

from db_utils import (
    bool_mark,
    exec_fetchall,
    exec_commit,
)
from query_builder import (
    build_list_query,
    build_features_query,
    build_movies_for_theater_query,
    build_showdates_for_movie_query,
    build_showtimes_query,
)


from admin_ui import open_admin_gate, open_add_theater_dialog, open_admin_panel

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
