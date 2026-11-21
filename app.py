from flask import Flask
from flask_wtf.csrf import CSRFProtect

from config import Config
from routes.auth import auth_bp
from routes.preview import preview_bp
from routes.student.courses import courses_bp
from routes.student.home import home_bp
from routes.student.shadowing import shadowing_bp
from routes.student.shadowing_results import shadowing_results_bp
from routes.admin.users import admin_users_bp
from routes.admin.courses import admin_courses_bp
from routes.admin.lessons import admin_lessons_bp
from routes.student.lessons import lessons_bp
from routes.student.foundation import foundation_bp
from routes.student.review import review_bp
from routes.admin.dashboard import admin_dashboard_bp
from routes.admin.vocabulary import admin_vocabulary_bp
from routes.admin.materials import admin_materials_bp
from routes.admin.grammar import admin_grammar_bp
from routes.admin.hanzi import admin_hanzi_bp
from routes.admin.pinyin import admin_pinyin_bp
from routes.admin.radicals import admin_radicals_bp
from routes.admin.pronunciation_rules import (
    admin_pronunciation_rules_bp,
)
from routes.admin.media import admin_media_bp
from routes.admin.exercises import admin_exercises_bp
from routes.admin.questions import admin_questions_bp
from routes.admin.shadowing import admin_shadowing_bp
from routes.admin.statistics import admin_statistics_bp
from routes.student.progress import progress_bp
from routes.student.vocabulary_review import vocabulary_review_bp
from routes.student.exercises import student_exercises_bp
from routes.admin.chatbot import admin_chatbot_bp
from routes.student.chatbot import student_chatbot_bp
from routes.admin.chatbot_knowledge_manage import admin_chatbot_knowledge_bp
from routes.student.dictionary import student_dictionary_bp
from routes.student.feedback import student_feedback_bp
from routes.admin.feedback import admin_feedback_bp
from routes.student.luyen_thi import student_luyen_thi_bp
from routes.admin.luyen_thi_manage import admin_luyen_thi_bp
from routes.student.profile import profile_bp
app = Flask(__name__)
app.config.from_object(Config)

if (
    not app.config["SECRET_KEY"]
    or app.config["SECRET_KEY"] == "DAN_CHUOI_VUA_TAO_VAO_DAY"
):
    raise RuntimeError(
        "Ban chua dien SECRET_KEY hop le trong file .env."
    )

csrf = CSRFProtect(app)

app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(shadowing_bp)
app.register_blueprint(shadowing_results_bp)
app.register_blueprint(courses_bp)
app.register_blueprint(preview_bp)
app.register_blueprint(admin_users_bp)
app.register_blueprint(admin_courses_bp)
app.register_blueprint(admin_lessons_bp)
app.register_blueprint(lessons_bp)
app.register_blueprint(foundation_bp)
app.register_blueprint(review_bp)
app.register_blueprint(admin_dashboard_bp)
app.register_blueprint(admin_vocabulary_bp)
app.register_blueprint(admin_materials_bp)
app.register_blueprint(admin_grammar_bp)
app.register_blueprint(admin_hanzi_bp)
app.register_blueprint(admin_pinyin_bp)
app.register_blueprint(admin_radicals_bp)
app.register_blueprint(admin_pronunciation_rules_bp)
app.register_blueprint(admin_media_bp)
app.register_blueprint(admin_shadowing_bp)
app.register_blueprint(admin_statistics_bp)
app.register_blueprint(admin_exercises_bp)
app.register_blueprint(admin_questions_bp)
app.register_blueprint(progress_bp)
app.register_blueprint(vocabulary_review_bp)
app.register_blueprint(student_exercises_bp)
app.register_blueprint(admin_chatbot_bp)
app.register_blueprint(student_chatbot_bp)
app.register_blueprint(admin_chatbot_knowledge_bp)
app.register_blueprint(student_dictionary_bp)
app.register_blueprint(student_feedback_bp)
app.register_blueprint(admin_feedback_bp)
app.register_blueprint(student_luyen_thi_bp)
app.register_blueprint(admin_luyen_thi_bp)
app.register_blueprint(profile_bp)
if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )