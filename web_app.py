import os
from urllib.parse import urlencode

from flask import Flask, flash, redirect, render_template, request, session, url_for

from fitness_app import (
    Friend,
    complete_workout,
    get_goals,
    get_workouts_by_goal,
    load_state,
    load_workouts,
    save_state,
)


def create_app():
    app = Flask(__name__)

    # Dev-friendly default; override in production via env var.
    app.secret_key = os.environ.get("FITNESS_APP_SECRET_KEY", "dev-secret-key-change-me")

    workouts_db = load_workouts()

    goals = get_goals()
    goal_value_to_label = {value: label for _num, label, value in goals}
    goal_label_to_value = {label: value for _num, label, value in goals}

    def _state():
        return load_state()

    def _persist(state):
        save_state(state)

    def _selected_goal_value():
        raw = (session.get("goal") or "").strip()
        valid = {value for _n, _l, value in goals}
        return raw if raw in valid else ""

    def _find_workout_by_id(workout_id):
        wid = str(workout_id).strip()
        for w in workouts_db:
            if str(w.get("id", "")).strip() == wid:
                return w
        return None

    @app.get("/")
    def home():
        state = _state()
        goal_value = _selected_goal_value()
        recs = get_workouts_by_goal(workouts_db, goal_value) if goal_value else []
        user_rank = state.user.view_rank()
        daily_decay = state.user.get_rank().get_decay()
        today_points = state.user.get_today_points()
        remaining_points = max(daily_decay - today_points, 0)

        return render_template(
            "home.html",
            page="home",
            goals=goals,
            goal_value=goal_value,
            goal_label=goal_value_to_label.get(goal_value, ""),
            recommendations=recs,
            rank=user_rank,
            workouts_count=len(state.user.get_history() or []),
            daily_decay=daily_decay,
            today_points = today_points,
            remaining_points = remaining_points
        )

    @app.post("/goal")
    def set_goal():
        label = (request.form.get("goal_label") or "").strip()
        goal_value = goal_label_to_value.get(label, "")
        if not goal_value:
            flash("Pick a valid goal.", "error")
            return redirect(url_for("home"))
        session["goal"] = goal_value
        flash(f"Goal set to “{label}”.", "success")
        return redirect(url_for("home"))

    @app.post("/complete/<workout_id>")
    def complete(workout_id):
        w = _find_workout_by_id(workout_id)
        if not w:
            flash("That workout could not be found.", "error")
            return redirect(url_for("home"))

        state = _state()
        pts = complete_workout(state.user, w)
        _persist(state)
        flash(f"Workout completed: +{pts} {'point' if pts == 1 else 'points'}.", "success")
        return redirect(url_for("home"))

    @app.get("/history")
    def history():
        state = _state()
        items = list(state.user.get_history() or [])
        items = items[::-1]
        return render_template(
            "history.html",
            page="history",
            rank=state.user.view_rank(),
            history=items,
        )

    @app.get("/friends")
    def friends():
        state = _state()
        me = state.user.view_rank()
        rows = [("You", me["tier"], me["elo"])]
        for f in state.friends:
            r = f.rank.view()
            rows.append((f.name, r["tier"], r["elo"]))
        rows.sort(key=lambda x: int(x[2]), reverse=True)

        return render_template(
            "friends.html",
            page="friends",
            rank=me,
            leaderboard=rows,
        )

    @app.post("/friends/add")
    def add_friend():
        name = (request.form.get("name") or "").strip()
        elo_raw = (request.form.get("elo") or "").strip()

        if not name:
            flash("Enter a friend name.", "error")
            return redirect(url_for("friends"))

        elo = 0
        if elo_raw:
            try:
                elo = int(elo_raw)
            except ValueError:
                flash("ELO must be a number.", "error")
                return redirect(url_for("friends"))

        state = _state()
        for f in state.friends:
            if f.name.lower() == name.lower():
                flash("That friend is already in your list.", "error")
                return redirect(url_for("friends"))

        state.friends.append(Friend(name=name, elo=elo))
        _persist(state)
        flash("Friend added.", "success")
        return redirect(url_for("friends"))

    @app.post("/friends/remove")
    def remove_friend():
        name = (request.form.get("name") or "").strip()
        if not name or name == "You":
            return redirect(url_for("friends"))

        state = _state()
        state.friends = [f for f in state.friends if f.name != name]
        _persist(state)
        flash("Friend removed.", "success")
        return redirect(url_for("friends"))

    @app.get("/health")
    def health():
        return {"ok": True, "workouts_loaded": len(workouts_db)}

    return app


app = create_app()

if __name__ == "__main__":
    # `flask run` works too, but this keeps it simple for class projects.
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=True)

