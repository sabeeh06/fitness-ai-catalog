"""
Flask web application for the fitness app.
Provides routes for profile, workouts, history, friends, and analytics.
"""
import os
from urllib.parse import urlencode

from flask import Flask, flash, redirect, render_template, request, session, url_for, g
from werkzeug.utils import secure_filename

import datetime
from collections import defaultdict

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
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Secret key for session management
    app.secret_key = os.environ.get("FITNESS_APP_SECRET_KEY", "dev-secret-key-change-me")
    # Folder for uploaded profile photos
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Load workout catalog once at startup
    workouts_db = load_workouts()

    # Goal mappings (label <-> value)
    goals = get_goals()
    goal_value_to_label = {value: label for _num, label, value in goals}
    goal_label_to_value = {label: value for _num, label, value in goals}

    @app.context_processor
    def inject_user_profile():
        """Inject profile data and theme into all templates."""
        state = _state()
        profile = state.user.profile
        theme = profile.get("theme", "dark")
        # Prefer username for UI display; fall back to full name.
        display_name = (profile.get("username") or "").strip() or (profile.get("full_name") or "").strip()
        return {
            "profile": profile,
            "theme": theme,
            "user_display_name": display_name,
        }

    def _state():
        """Load current app state from disk."""
        return load_state()

    def _persist(state):
        """Save app state to disk."""
        save_state(state)

    def _selected_goal_value():
        """Get the currently selected goal from session."""
        raw = (session.get("goal") or "").strip()
        valid = {value for _n, _l, value in goals}
        return raw if raw in valid else ""

    def _find_workout_by_id(workout_id):
        """Find a workout in the catalog by its ID."""
        wid = str(workout_id).strip()
        for w in workouts_db:
            if str(w.get("id", "")).strip() == wid:
                return w
        return None

    @app.get("/")
    def home():
        """Redirect root to profile page (new home)."""
        # Make Profile the new home page.
        return redirect(url_for("profile"))

    @app.get("/workouts")
    def workouts():
        """Show workout recommendations and daily goal progress."""
        state = _state()
        goal_value = _selected_goal_value()
        recs = get_workouts_by_goal(workouts_db, goal_value) if goal_value else []
        user_rank = state.user.view_rank()
        daily_decay = state.user.get_rank().get_decay()
        today_points = state.user.get_today_points()
        remaining_points = max(daily_decay - today_points, 0)

        return render_template(
            "home.html",
            page="workouts",
            goals=goals,
            goal_value=goal_value,
            goal_label=goal_value_to_label.get(goal_value, ""),
            recommendations=recs,
            rank=user_rank,
            workouts_count=len(state.user.get_history() or []),
            daily_decay=daily_decay,
            today_points=today_points,
            remaining_points=remaining_points,
        )

    @app.post("/goal")
    def set_goal():
        """Save the user's selected fitness goal in session."""
        label = (request.form.get("goal_label") or "").strip()
        goal_value = goal_label_to_value.get(label, "")
        if not goal_value:
            flash("Pick a valid goal.", "error")
            return redirect(url_for("workouts"))
        session["goal"] = goal_value
        flash(f"Goal set to “{label}”.", "success")
        return redirect(url_for("workouts"))

    @app.post("/complete/<workout_id>")
    def complete(workout_id):
        """Complete a workout, award points, and save state."""
        w = _find_workout_by_id(workout_id)
        if not w:
            flash("That workout could not be found.", "error")
            return redirect(url_for("workouts"))

        state = _state()
        pts = complete_workout(state.user, w)
        _persist(state)
        flash(f"Workout completed: +{pts} {'point' if pts == 1 else 'points'}.", "success")
        return redirect(url_for("workouts"))

    @app.get("/history")
    def history():
        """Display workout history with analytics charts."""
        import datetime
        from collections import defaultdict
        state = _state()
        workouts = list(state.user.get_history() or [])
        workouts_sorted = sorted(workouts, key=lambda w: w.get("date", ""))

        # 1. Points per workout
        dates = [w.get("date", "") for w in workouts_sorted]
        points = [w.get("points", 0) for w in workouts_sorted]

        # 2. Cumulative points (ELO)
        cumulative = []
        running = 0
        for p in points:
            running += p
            cumulative.append(running)

        # 3. Weekly frequency (last 8 weeks)
        today = datetime.date.today()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        weeks = []
        week_labels = []
        for i in range(8, 0, -1):
            week_start = start_of_week - datetime.timedelta(weeks=i)
            week_end = week_start + datetime.timedelta(days=6)
            weeks.append((week_start, week_end))
            week_labels.append(week_start.strftime("%b %d"))

        weekly_counts = []
        for ws, we in weeks:
            count = 0
            for w in workouts_sorted:
                if w.get("date"):
                    wd = datetime.date.fromisoformat(w["date"])
                    if ws <= wd <= we:
                        count += 1
            weekly_counts.append(count)

        # 4. Workout distribution by goal (using catalog)
        goal_map = {}
        for cat_w in workouts_db:
            title = cat_w.get("title", "")
            goal = cat_w.get("goal", "Other")
            if title:
                goal_map[title] = goal
        goal_counts = defaultdict(int)
        for w in workouts_sorted:
            title = w.get("title", "")
            goal = goal_map.get(title, "Other")
            goal_counts[goal] += 1
        goal_labels = list(goal_counts.keys())
        goal_values = list(goal_counts.values())

        # 5. Longest streak (consecutive days with at least one workout)
        workout_dates_set = set()
        for w in workouts_sorted:
            if w.get("date"):
                workout_dates_set.add(w["date"])
        sorted_dates = sorted(workout_dates_set)
        longest_streak = 0
        current_streak = 0
        prev_date = None
        for d_str in sorted_dates:
            d = datetime.date.fromisoformat(d_str)
            if prev_date is None:
                current_streak = 1
            elif (d - prev_date).days == 1:
                current_streak += 1
            else:
                current_streak = 1
            longest_streak = max(longest_streak, current_streak)
            prev_date = d

        # 6. Additional stats
        total_workouts = len(workouts)
        total_points = sum(points)
        avg_points = total_points / total_workouts if total_workouts > 0 else 0

        chart_data = {
            "dates": dates,
            "points": points,
            "cumulative": cumulative,
            "week_labels": week_labels,
            "weekly_counts": weekly_counts,
            "goal_labels": goal_labels,
            "goal_values": goal_values,
            "total_workouts": total_workouts,
            "total_points": total_points,
            "avg_points": round(avg_points, 1),
            "longest_streak": longest_streak,
            "current_rank": state.user.view_rank()["tier"],
        }

        history_display = workouts[::-1]
        return render_template(
            "history.html",
            page="history",
            rank=state.user.view_rank(),
            history=history_display,
            chart_data=chart_data,
        )


    @app.get("/friends")
    def friends():
        """Show friends leaderboard."""
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
        """Add a friend by name and optional ELO."""
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
        """Remove a friend from the list."""
        name = (request.form.get("name") or "").strip()
        if not name or name == "You":
            return redirect(url_for("friends"))

        state = _state()
        state.friends = [f for f in state.friends if f.name != name]
        _persist(state)
        flash("Friend removed.", "success")
        return redirect(url_for("friends"))

    @app.get("/profile")
    def profile():
        """Show user profile page with stats."""
        state = _state()
        workouts = list(state.user.get_history() or [])
        total_workouts = len(workouts)
        total_points = sum(w.get("points", 0) for w in workouts)
        return render_template(
            "profile.html",
            page="profile",
            rank=state.user.view_rank(),
            total_workouts=total_workouts,
            total_points=total_points,
        )

    @app.post("/profile")
    def update_profile():
        """Update user profile information, including photo upload."""
        state = _state()
        photo_url = request.form.get("photo_url", "")
        uploaded = request.files.get("photo_file")
        if uploaded and uploaded.filename:
            filename = secure_filename(uploaded.filename)
            # Keep a small safety net even after secure_filename.
            if filename:
                save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                uploaded.save(save_path)
                photo_url = url_for("static", filename=f"uploads/{filename}")

        updates = {
            "username": request.form.get("username", ""),
            "full_name": request.form.get("full_name", ""),
            "email": request.form.get("email", ""),
            "photo_url": photo_url,
            "bio": request.form.get("bio", ""),
            "height_cm": request.form.get("height_cm"),
            "weight_kg": request.form.get("weight_kg"),
            "age": request.form.get("age"),
            "gender": request.form.get("gender", ""),
            "target_weight_kg": request.form.get("target_weight_kg"),
            "activity_level": request.form.get("activity_level", "moderate"),
            "chest_cm": request.form.get("chest_cm"),
            "waist_cm": request.form.get("waist_cm"),
            "hips_cm": request.form.get("hips_cm"),
            "theme": request.form.get("theme", "dark"),
        }
        state.user.update_profile(updates)
        _persist(state)
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile"))

    @app.get("/health")
    def health():
        """Health check endpoint for monitoring."""
        return {"ok": True, "workouts_loaded": len(workouts_db)}

    return app


app = create_app()

if __name__ == "__main__":
    # `flask run` works too, but this keeps it simple for class projects.
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=True)
