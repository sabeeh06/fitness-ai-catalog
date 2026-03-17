import tkinter as tk
from tkinter import messagebox, ttk

from fitness_app import (
    AppState,
    Friend,
    complete_workout,
    get_goals,
    get_workouts_by_goal,
    load_state,
    load_workouts,
    save_state,
)


class FitnessAppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fitness App")
        # Desktop window that contains a centered "phone" frame.
        self.minsize(920, 720)

        self.state = load_state()
        self.user = self.state.user
        self.workouts_db = load_workouts()
        if not self.workouts_db:
            messagebox.showerror(
                "Missing catalog",
                "Could not load fitness_catalog.csv.\n\nMake sure it is in the same folder as gui.py.",
            )

        self.goals = get_goals()
        self.goal_label_to_value = {label: value for _, label, value in self.goals}
        self.goal_var = tk.StringVar(value=self.goals[0][1])

        self.selected_workout = None
        self.recommendations = []
        self.current_page = tk.StringVar(value="home")

        self._setup_style()
        self._build_ui()
        self._refresh_rank()
        self._refresh_history()
        self._refresh_recommendations()
        self._refresh_friends()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        bg = "#0b1220"        # app background
        phone = "#0f172a"     # phone body
        card = "#111c33"      # card background
        text = "#e6edf3"      # primary text
        muted = "#9fb0c0"     # secondary text
        accent = "#3b82f6"    # blue
        border = "#24324a"

        self._colors = {
            "bg": bg,
            "phone": phone,
            "card": card,
            "text": text,
            "muted": muted,
            "accent": accent,
            "border": border,
        }

        self.configure(background=bg)

        style.configure(".", font=("Segoe UI", 10))
        style.configure("App.TFrame", background=bg)
        style.configure("Phone.TFrame", background=phone)
        style.configure("Card.TFrame", background=card)
        style.configure("Title.TLabel", background=phone, foreground=text, font=("Segoe UI", 15, "bold"))
        style.configure("Sub.TLabel", background=phone, foreground=muted, font=("Segoe UI", 10))
        style.configure("CardTitle.TLabel", background=card, foreground=text, font=("Segoe UI", 11, "bold"))
        style.configure("CardText.TLabel", background=card, foreground=muted)

        style.configure("TLabel", background=phone, foreground=text)
        style.configure("TButton", padding=(14, 10))
        style.map("TButton", foreground=[("disabled", muted)])

        style.configure("Primary.TButton", padding=(14, 10), background=accent, foreground="white")
        style.map("Primary.TButton", background=[("active", "#2563eb")])

        style.configure("TCombobox", padding=(8, 8))

        # Treeview polish
        style.configure(
            "Treeview",
            background=card,
            fieldbackground=card,
            foreground=text,
            rowheight=34,
            borderwidth=0,
        )
        style.map("Treeview", background=[("selected", "#1d4ed8")])
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def _build_ui(self):
        root = ttk.Frame(self, style="App.TFrame", padding=18)
        root.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Phone frame (centered)
        self.phone_w = 410
        self.phone_h = 780

        phone_outer = ttk.Frame(root, style="Phone.TFrame")
        phone_outer.place(relx=0.5, rely=0.5, anchor="center", width=self.phone_w, height=self.phone_h)

        phone_outer.columnconfigure(0, weight=1)
        phone_outer.rowconfigure(1, weight=1)

        # Top app bar
        appbar = ttk.Frame(phone_outer, style="Phone.TFrame", padding=(16, 14))
        appbar.grid(row=0, column=0, sticky="ew")
        appbar.columnconfigure(0, weight=1)

        ttk.Label(appbar, text="Fitness", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        self.rank_var = tk.StringVar(value="Bronze • 0 ELO")
        ttk.Label(appbar, textvariable=self.rank_var, style="Sub.TLabel").grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Pages container
        self.pages = ttk.Frame(phone_outer, style="Phone.TFrame", padding=(14, 0, 14, 0))
        self.pages.grid(row=1, column=0, sticky="nsew")
        self.pages.columnconfigure(0, weight=1)
        self.pages.rowconfigure(0, weight=1)

        self.page_home = ttk.Frame(self.pages, style="Phone.TFrame")
        self.page_history = ttk.Frame(self.pages, style="Phone.TFrame")
        self.page_friends = ttk.Frame(self.pages, style="Phone.TFrame")

        for p in (self.page_home, self.page_history, self.page_friends):
            p.grid(row=0, column=0, sticky="nsew")

        # Home page
        self._build_home(self.page_home)
        self._build_history(self.page_history)
        self._build_friends(self.page_friends)

        # Bottom nav
        nav = ttk.Frame(phone_outer, style="Phone.TFrame", padding=(12, 10))
        nav.grid(row=2, column=0, sticky="ew")
        nav.columnconfigure(0, weight=1)
        nav.columnconfigure(1, weight=1)
        nav.columnconfigure(2, weight=1)

        ttk.Button(nav, text="Home", command=lambda: self._show_page("home")).grid(row=0, column=0, sticky="ew", padx=4)
        ttk.Button(nav, text="History", command=lambda: self._show_page("history")).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(nav, text="Friends", command=lambda: self._show_page("friends")).grid(row=0, column=2, sticky="ew", padx=4)

        self._show_page("home")

    def _build_home(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(3, weight=1)

        # Goal selector card
        goal_card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        goal_card.grid(row=0, column=0, sticky="ew", pady=(14, 12))
        goal_card.columnconfigure(0, weight=1)

        ttk.Label(goal_card, text="Your goal", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        goal_combo = ttk.Combobox(
            goal_card,
            state="readonly",
            textvariable=self.goal_var,
            values=[label for _, label, _ in self.goals],
        )
        goal_combo.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        goal_combo.bind("<<ComboboxSelected>>", lambda _e: self._refresh_recommendations())

        # Programs card
        rec_card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        rec_card.grid(row=1, column=0, sticky="nsew", pady=(0, 12))
        rec_card.columnconfigure(0, weight=1)
        rec_card.rowconfigure(1, weight=1)

        ttk.Label(rec_card, text="Recommended", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.tree = ttk.Treeview(rec_card, columns=("title", "days"), show="headings", selectmode="browse", height=10)
        self.tree.heading("title", text="Program")
        self.tree.heading("days", text="Days")
        self.tree.column("title", width=270, anchor="w")
        self.tree.column("days", width=60, anchor="center")
        self.tree.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        self.tree.bind("<<TreeviewSelect>>", self._on_select_workout)

        tree_scroll = ttk.Scrollbar(rec_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.grid(row=1, column=1, sticky="ns", pady=(10, 0))

        # Details card
        details_card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        details_card.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        details_card.columnconfigure(0, weight=1)

        ttk.Label(details_card, text="Details", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.details = tk.Text(
            details_card,
            height=8,
            wrap="word",
            state="disabled",
            relief="flat",
            background=self._colors["card"],
            foreground=self._colors["text"],
            insertbackground=self._colors["text"],
        )
        self.details.grid(row=1, column=0, sticky="ew", pady=(10, 12))

        self.complete_btn = ttk.Button(details_card, text="Complete workout", style="Primary.TButton", command=self._complete_selected)
        self.complete_btn.grid(row=2, column=0, sticky="ew")

    def _build_history(self, parent):
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        card.grid(row=0, column=0, sticky="nsew", pady=(14, 12))
        card.columnconfigure(0, weight=1)
        card.rowconfigure(1, weight=1)

        ttk.Label(card, text="Workout history", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.history_list = tk.Listbox(
            card,
            relief="flat",
            highlightthickness=0,
            background=self._colors["card"],
            foreground=self._colors["text"],
            selectbackground="#1d4ed8",
            selectforeground="white",
        )
        self.history_list.grid(row=1, column=0, sticky="nsew", pady=(10, 0))

    def _build_friends(self, parent):
        parent.columnconfigure(0, weight=1)

        add_card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        add_card.grid(row=0, column=0, sticky="ew", pady=(14, 12))
        add_card.columnconfigure(0, weight=1)

        ttk.Label(add_card, text="Friends", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(add_card, text="Name + optional ELO", style="CardText.TLabel").grid(row=1, column=0, sticky="w", pady=(6, 10))

        add_row = ttk.Frame(add_card, style="Card.TFrame")
        add_row.grid(row=2, column=0, sticky="ew")
        add_row.columnconfigure(0, weight=1)
        self.friend_name_var = tk.StringVar()
        self.friend_elo_var = tk.StringVar()
        ttk.Entry(add_row, textvariable=self.friend_name_var).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Entry(add_row, textvariable=self.friend_elo_var, width=7).grid(row=0, column=1, sticky="e", padx=(0, 8))
        ttk.Button(add_row, text="Add", command=self._add_friend).grid(row=0, column=2, sticky="e")

        lb_card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        lb_card.grid(row=1, column=0, sticky="nsew", pady=(0, 12))
        lb_card.columnconfigure(0, weight=1)
        lb_card.rowconfigure(1, weight=1)

        ttk.Label(lb_card, text="Leaderboard", style="CardTitle.TLabel").grid(row=0, column=0, sticky="w")
        self.friends_tree = ttk.Treeview(lb_card, columns=("name", "tier", "elo"), show="headings", height=10)
        self.friends_tree.heading("name", text="Name")
        self.friends_tree.heading("tier", text="Tier")
        self.friends_tree.heading("elo", text="ELO")
        self.friends_tree.column("name", width=190, anchor="w")
        self.friends_tree.column("tier", width=70, anchor="center")
        self.friends_tree.column("elo", width=70, anchor="center")
        self.friends_tree.grid(row=1, column=0, sticky="nsew", pady=(10, 0))

        friends_scroll = ttk.Scrollbar(lb_card, orient="vertical", command=self.friends_tree.yview)
        self.friends_tree.configure(yscrollcommand=friends_scroll.set)
        friends_scroll.grid(row=1, column=1, sticky="ns", pady=(10, 0))

        ttk.Button(lb_card, text="Remove selected", command=self._remove_selected_friend).grid(row=2, column=0, sticky="ew", pady=(12, 0))

    def _show_page(self, page):
        self.current_page.set(page)
        if page == "home":
            self.page_home.tkraise()
        elif page == "history":
            self.page_history.tkraise()
        else:
            self.page_friends.tkraise()

    def _refresh_recommendations(self):
        self.tree.delete(*self.tree.get_children())
        self.selected_workout = None
        self._set_details("")

        goal_label = self.goal_var.get()
        goal_value = self.goal_label_to_value.get(goal_label)
        self.recommendations = get_workouts_by_goal(self.workouts_db, goal_value)

        for i, w in enumerate(self.recommendations):
            title = w.get("title", "")
            level = w.get("level", "")
            days = w.get("days_per_week", "")
            self.tree.insert("", "end", iid=str(i), values=(f"{title} • {level}", days))

        if not self.recommendations:
            self._set_details("No programs found for this goal.\n\nTry a different goal.")

    def _on_select_workout(self, _event):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        if idx < 0 or idx >= len(self.recommendations):
            return

        self.selected_workout = self.recommendations[idx]
        self._set_details(self._format_workout(self.selected_workout))

    def _format_workout(self, w):
        lines = [
            f"Title: {w.get('title', '')}",
            f"Goal: {w.get('goal', '')}",
            f"Level: {w.get('level', '')}",
            f"Days/week: {w.get('days_per_week', '')}",
            f"Equipment: {w.get('equipment', '')}",
            "",
            "Description:",
            w.get("description", ""),
        ]
        return "\n".join(lines).strip()

    def _set_details(self, text):
        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        self.details.insert("1.0", text)
        self.details.configure(state="disabled")

    def _refresh_rank(self):
        info = self.user.view_rank()
        self.rank_var.set(f"{info['tier']} • {info['elo']} ELO")

    def _refresh_history(self):
        self.history_list.delete(0, "end")
        history = self.user.get_history()
        if not history:
            self.history_list.insert("end", "No workouts completed yet.")
            return
        for w in history[::-1]:
            self.history_list.insert("end", f"{w.get('date', '')} — {w.get('title', '')} (+{w.get('points', 0)} pts)")

    def _complete_selected(self):
        if not self.selected_workout:
            messagebox.showinfo("Select a program", "Pick a program from the list first.")
            return
        pts = complete_workout(self.user, self.selected_workout)
        messagebox.showinfo("Workout completed", f"Nice work! +{pts} points.")
        self._refresh_rank()
        self._refresh_history()
        self._persist()

    def _persist(self):
        self.state.user = self.user
        save_state(self.state)

    def _on_close(self):
        try:
            self._persist()
        finally:
            self.destroy()

    def _refresh_friends(self):
        self.friends_tree.delete(*self.friends_tree.get_children())
        rows = []

        me = self.user.view_rank()
        rows.append(("You", me["tier"], me["elo"]))

        for f in self.state.friends:
            r = f.rank.view()
            rows.append((f.name, r["tier"], r["elo"]))

        rows.sort(key=lambda x: int(x[2]), reverse=True)
        for i, (name, tier, elo) in enumerate(rows, 1):
            self.friends_tree.insert("", "end", iid=str(i), values=(name, tier, elo))

    def _add_friend(self):
        name = self.friend_name_var.get().strip()
        if not name:
            messagebox.showinfo("Friend name required", "Enter a friend name.")
            return

        # Optional: allow entering ELO to compare
        elo_raw = self.friend_elo_var.get().strip()
        if elo_raw:
            try:
                elo = int(elo_raw)
            except ValueError:
                messagebox.showinfo("Invalid ELO", "ELO must be a number.")
                return
        else:
            elo = 0

        for f in self.state.friends:
            if f.name.lower() == name.lower():
                messagebox.showinfo("Already added", "That friend is already in your list.")
                return

        self.state.friends.append(Friend(name=name, elo=elo))
        self.friend_name_var.set("")
        self.friend_elo_var.set("")
        self._refresh_friends()
        self._persist()

    def _remove_selected_friend(self):
        sel = self.friends_tree.selection()
        if not sel:
            return
        # Find by name (ignore "You")
        item = self.friends_tree.item(sel[0])
        name = (item.get("values") or [""])[0]
        if name == "You":
            return
        self.state.friends = [f for f in self.state.friends if f.name != name]
        self._refresh_friends()
        self._persist()


if __name__ == "__main__":
    app = FitnessAppGUI()
    app.mainloop()

