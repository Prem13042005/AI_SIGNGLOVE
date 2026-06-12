import os, time, json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_mail import Mail, Message
from dotenv import load_dotenv
load_dotenv()

# Flask config 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///signglove.db")
app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
mail = Mail(app)

db = SQLAlchemy(app)

# ML model 
from ml.predictor import GesturePredictor
predictor = GesturePredictor()

latest_prediction = {
    "text": "",
    "language": "English",
    "confidence": 0.0,
    "response_time": 0.0,
    "sensor": None,
    "timestamp": None
}

# DB models 
class User(db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    first_name    = db.Column(db.String(80))
    last_name     = db.Column(db.String(80))
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    histories     = db.relationship('History', backref='user', lazy=True)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)

class History(db.Model):
    __tablename__ = 'history'
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    gesture_raw     = db.Column(db.Text)
    translated_text = db.Column(db.String(300))
    language        = db.Column(db.String(60))
    confidence      = db.Column(db.Float)
    response_time   = db.Column(db.Float)
    timestamp       = db.Column(db.DateTime, default=datetime.utcnow)

# Auth helpers 
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to continue.", "warning")
            return redirect(url_for('signin'))
        return f(*args, **kwargs)
    return decorated

def current_user():
    uid = session.get('user_id')
    return User.query.get(uid) if uid else None

# Page routes 
@app.route('/')
def index():
    return render_template("index.html", user=current_user())

@app.route('/about')
def about():
    return render_template("aboutus.html", user=current_user())

@app.route('/contact', methods=['GET','POST'])
def contact():

    if request.method == 'POST':

        first_name=request.form.get('first_name')
        last_name=request.form.get('last_name')
        email=request.form.get('email')
        subject=request.form.get('subject')
        message=request.form.get('message')

        try:

            msg=Message(
                subject=f"SignGlove Contact | {subject}",

                sender=app.config['MAIL_USERNAME'],

                recipients=[
                    "premrajrajput1345@gmail.com"
                ]
            )

            msg.body=f"""
New Contact Submission

Name:
{first_name} {last_name}

Email:
{email}

Subject:
{subject}

Message:
{message}
"""

            mail.send(msg)

            flash(
                "Your message has been sent successfully!",
                "success"
            )

        except Exception as e:

            print(e)

            flash(
                f"Email failed: {str(e)}",
                "danger"
            )

    return render_template(
        "contact.html"
    )

@app.route('/live')
@login_required
def live_translation():
    return render_template("live_translation.html", user=current_user())

@app.route('/history')
@login_required
def history_page():
    entries = History.query.filter_by(user_id=session['user_id'])\
                           .order_by(History.timestamp.desc())\
                           .limit(200).all()
    return render_template("history.html", entries=entries, user=current_user())

# History
@app.route('/api/history')
@login_required
def api_history():
    uid     = session['user_id']
    limit   = min(int(request.args.get('limit', 50)), 200)
    entries = History.query.filter_by(user_id=uid)\
                           .order_by(History.timestamp.desc())\
                           .limit(limit).all()
    return jsonify([{
        'id':              e.id,
        'translated_text': e.translated_text,
        'language':        e.language,
        'confidence':      round(e.confidence * 100, 1),
        'response_time':   round(e.response_time * 1000, 1),
        'timestamp':       e.timestamp.strftime('%d %b %Y, %I:%M %p'),
    } for e in entries])

# Sentence Builder
@app.route('/api/save_sentence', methods=['POST'])
@login_required
def save_sentence():
    data     = request.get_json(force=True) or {}
    sentence = data.get('sentence', '').strip()
    language = data.get('language', 'English')
    if not sentence:
        return jsonify({'error': 'Empty sentence'}), 400
    hist = History(
        user_id         = session['user_id'],
        gesture_raw     = json.dumps({'type': 'sentence_builder'}),
        translated_text = sentence,
        language        = language,
        confidence      = 1.0,
        response_time   = 0.0,
        timestamp       = datetime.utcnow()
    )
    db.session.add(hist)
    db.session.commit()
    return jsonify({'ok': True, 'id': hist.id})

@app.route('/profile')
@login_required
def profile():
    from sqlalchemy import func, cast, Date
    uid  = session['user_id']
    user = current_user()

    total_translations = History.query.filter_by(user_id=uid).count()
    avg_confidence     = db.session.query(func.avg(History.confidence)).filter_by(user_id=uid).scalar() or 0
    avg_response_time  = db.session.query(func.avg(History.response_time)).filter_by(user_id=uid).scalar() or 0

    frequent = db.session.query(
        History.translated_text,
        func.count(History.translated_text).label('cnt')
    ).filter_by(user_id=uid)\
     .group_by(History.translated_text)\
     .order_by(func.count(History.translated_text).desc())\
     .limit(5).all()

    days_active = db.session.query(
        func.count(func.distinct(cast(History.timestamp, Date)))
    ).filter_by(user_id=uid).scalar() or 0

    return render_template("profile.html",
        user=user,
        total_translations=total_translations,
        avg_confidence=round(avg_confidence * 100, 1),
        avg_response_time=round(avg_response_time * 1000, 1),
        days_active=days_active,
        frequent=frequent,
    )

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    user = current_user()
    user.first_name = request.form.get('first_name', user.first_name).strip()
    user.last_name  = request.form.get('last_name',  user.last_name).strip()
    db.session.commit()
    flash("Profile updated successfully!", "success")
    return redirect(url_for('profile'))

# Auth routes
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user     = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('live_translation'))
        return render_template("signin.html", error="Invalid email or password.")
    return render_template("signin.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name       = request.form.get('first_name', '').strip()
        last_name        = request.form.get('last_name',  '').strip()
        email            = request.form.get('email',      '').strip().lower()
        password         = request.form.get('password',  '')
        confirm_password = request.form.get('confirm_password', '')

        if not all([first_name, last_name, email, password]):
            return render_template("signup.html", error="All fields are required.")
        if password != confirm_password:
            return render_template("signup.html", error="Passwords do not match.")
        if len(password) < 6:
            return render_template("signup.html", error="Password must be at least 6 characters.")
        if User.query.filter_by(email=email).first():
            return render_template("signup.html", error="Email already registered. Please sign in.")

        user = User(first_name=first_name, last_name=last_name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully! Please sign in.", "success")
        return redirect(url_for('signin'))
    return render_template("signup.html")

# Analytics
@app.route('/analytics')
@login_required
def analytics():
    from sqlalchemy import func, cast, Date
    uid = session['user_id']

    total       = History.query.filter_by(user_id=uid).count()
    avg_conf    = db.session.query(func.avg(History.confidence)).filter_by(user_id=uid).scalar() or 0
    avg_rt      = db.session.query(func.avg(History.response_time)).filter_by(user_id=uid).scalar() or 0
    days_active = db.session.query(
        func.count(func.distinct(cast(History.timestamp, Date)))
    ).filter_by(user_id=uid).scalar() or 0

    gesture_counts = [[r[0], r[1]] for r in db.session.query(
        History.translated_text, func.count(History.translated_text)
    ).filter_by(user_id=uid)\
     .group_by(History.translated_text)\
     .order_by(func.count(History.translated_text).desc())\
     .limit(8).all()]

    lang_counts = [[r[0], r[1]] for r in db.session.query(
        History.language, func.count(History.language)
    ).filter_by(user_id=uid).group_by(History.language).all()]

    # Confidence over time with real timestamps
    recent = History.query.filter_by(user_id=uid)\
                          .order_by(History.timestamp.desc())\
                          .limit(20).all()
    recent = list(reversed(recent))
    conf_over_time    = [round(h.confidence * 100, 1) for h in recent]
    conf_time_labels  = [h.timestamp.strftime('%d %b %H:%M') for h in recent]

    return render_template('analytics.html',
        user=current_user(),
        total=total,
        avg_conf=round(avg_conf * 100, 1),
        avg_rt=round(avg_rt * 1000, 1),
        days_active=days_active,
        gesture_counts=gesture_counts,
        lang_counts=lang_counts,
        conf_over_time=conf_over_time,
        conf_time_labels=conf_time_labels,
    )

# Export
@app.route('/export_history')
@login_required
def export_history():
    import csv, io
    uid     = session['user_id']
    entries = History.query.filter_by(user_id=uid).order_by(History.timestamp.desc()).all()
    output  = io.StringIO()
    writer  = csv.writer(output)
    writer.writerow(['Timestamp', 'Translated Text', 'Language', 'Confidence', 'Response Time (ms)'])
    for e in entries:
        writer.writerow([
            e.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            e.translated_text, e.language,
            round(e.confidence * 100, 1),
            round(e.response_time * 1000, 1)
        ])
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=signglove_history.csv'}
    )

# Hardware ingest 
@app.route('/hardware_ingest', methods=['POST'])
def hardware_ingest():
    global latest_prediction

    data     = request.get_json(force=True) or {}
    language = data.get("language", "English")
    start    = time.time()

    try:
        features = [
            data["F4"],  
            data["F3"],  
            data["F2"],  
            data["AX"],
            data["AY"],
            data["AZ"],
            data["GX"],
            data["GY"]
        ]
        text, confidence = predictor.predict(features, language=language)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    response_time = time.time() - start
    now           = datetime.utcnow()

    if latest_prediction["text"] == text:
        return jsonify({"ok": True, "duplicate": True})

    latest_prediction = {
        "text":          text,
        "language":      language,
        "confidence":    round(confidence, 3),
        "response_time": round(response_time, 4),
        "sensor":        data,
        "timestamp":     now.isoformat()
    }

    user_id = session.get('user_id') or data.get('user_id')
    if user_id:
        hist = History(
            user_id         = int(user_id),
            gesture_raw     = json.dumps(data),
            translated_text = text,
            language        = language,
            confidence      = confidence,
            response_time   = response_time,
            timestamp       = now
        )
        db.session.add(hist)
        db.session.commit()

    return jsonify({
        "ok":            True,
        "text":          text,
        "language":      language,
        "confidence":    round(confidence, 3),
        "response_time": round(response_time, 4),
        "timestamp":     now.isoformat()
    })

@app.route('/latest_prediction', methods=['GET'])
def latest_prediction_api():
    return jsonify(latest_prediction)

# Other routes 
@app.route('/settings')
@login_required
def settings():
    return render_template("settings.html", user=current_user())

@app.route('/signout')
def signout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for('signin'))

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    flash("Your message has been sent successfully!", "success")
    return redirect(url_for('contact'))

# Run 
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0",port=5000,debug=True)
