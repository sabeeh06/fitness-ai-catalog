import tkinter as tk
from tkinter import messagebox, ttk

from fitness_app import User, complete_workout, get_goals, get_workouts_by_goal, load_workouts


class FitnessAppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fitness App")
        self.minsize(900, 560)

        self.user = User()
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

        self._build_ui()
        self._refresh_rank()
        self._refresh_history()
        self._refresh_recommendations()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, padding=12)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(3, weight=1)

        ttk.Label(header, text="Goal:").grid(row=0, column=0, sticky="w")
        goal_combo = ttk.Combobox(
            header,
            state="readonly",
            textvariable=self.goal_var,
            values=[label for _, label, _ in self.goals],
            width=28,
        )
        goal_combo.grid(row=0, column=1, sticky="w", padx=(8, 16))
        goal_combo.bind("<<ComboboxSelected>>", lambda _e: self._refresh_recommendations())

        ttk.Button(header, text="Refresh", command=self._refresh_recommendations).grid(row=0, column=2, sticky="w")

        self.rank_var = tk.StringVar(value="Tier: Bronze | ELO: 0")
        ttk.Label(header, textvariable=self.rank_var).grid(row=0, column=4, sticky="e")

        body = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        body.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

        left = ttk.Frame(body, padding=10)
        right = ttk.Frame(body, padding=10)
        body.add(left, weight=2)
        body.add(right, weight=3)

        # Left: recommendations
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        ttk.Label(left, text="Recommended programs", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w")

        self.tree = ttk.Treeview(left, columns=("level", "days"), show="headings", selectmode="browse")
        self.tree.heading("level", text="Level")
        self.tree.heading("days", text="Days/week")
        self.tree.column("level", width=120, anchor="w")
        self.tree.column("days", width=110, anchor="center")
        self.tree.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        self.tree.bind("<<TreeviewSelect>>", self._on_select_workout)

        tree_scroll = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.grid(row=1, column=1, sticky="ns", pady=(8, 0))

        # Right: details + history
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        right.rowconfigure(4, weight=1)

        ttk.Label(right, text="Program details", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w")

        self.details = tk.Text(right, height=10, wrap="word", state="disabled")
        self.details.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

        btn_row = ttk.Frame(right)
        btn_row.grid(row=2, column=0, sticky="ew", pady=10)
        btn_row.columnconfigure(1, weight=1)

        self.complete_btn = ttk.Button(btn_row, text="Complete workout", command=self._complete_selected)
        self.complete_btn.grid(row=0, column=0, sticky="w")

        ttk.Separator(right).grid(row=3, column=0, sticky="ew", pady=(6, 10))

        ttk.Label(right, text="Workout history", font=("Segoe UI", 11, "bold")).grid(row=4, column=0, sticky="nw")

        self.history_list = tk.Listbox(right, height=8)
        self.history_list.grid(row=5, column=0, sticky="nsew", pady=(8, 0))

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
            self.tree.insert("", "end", iid=str(i), values=(f"{title} ({level})", days))

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
        self.rank_var.set(f"Tier: {info['tier']} | ELO: {info['elo']}")

    def _refresh_history(self):
        self.history_list.delete(0, "end")
        history = self.user.get_history()
        if not history:
            self.history_list.insert("end", "No workouts completed yet.")
            self.history_list.configure(state="disabled")
            return
        self.history_list.configure(state="normal")
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


if __name__ == "__main__":
    app = FitnessAppGUI()
    app.mainloop()

