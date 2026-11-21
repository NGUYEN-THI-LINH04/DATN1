from flask import Blueprint, abort, redirect, render_template, url_for


preview_bp = Blueprint("preview", __name__)


PAGES = {
    "student": {
        "lesson",
        "exercise",
        "result",
        "learning_history",
        "progress",
        "vocabulary",
        "flashcards",
        "chatbot",
        "profile",
        "feedback",
    },
    "auth": {
        "login",
        "register",
        "forgot_password",
        "reset_password",
        "admin_login",
    },
    "admin": {
        "dashboard",
        "users",
        "courses",
        "lessons",
        "vocabulary",
        "exercises",
        "questions",
        "media",
        "chatbot_knowledge",
        "chatbot_settings",
        "feedback",
        "statistics",
    },
}


@preview_bp.get("/giao-dien/<group>/<page>")
def show(group, page):
    if group not in PAGES or page not in PAGES[group]:
        abort(404)

    if group == "admin":
        if page == "statistics":
            return redirect(
                url_for("admin_statistics.index")
            )
        if page == "users":
            return redirect(url_for("admin_users.index"))

        if page == "courses":
            return redirect(url_for("admin_courses.index"))
    if group == "admin" and page == "lessons":
        return redirect(url_for("admin_lessons.index"))

    if group == "student" and page == "lesson":
        return redirect(url_for("lessons.index"))
    return render_template(f"{group}/{page}.html")