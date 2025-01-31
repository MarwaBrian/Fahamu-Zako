from flask import Flask, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
import os
import PyPDF2
import pyttsx3
import moviepy.editor as mp
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from together import Together
from forms import RegistrationForm, LoginForm
from models import User, db  # Import User and db from models.py

os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance\site.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/User/Videos/wakatime/fahamu/fahamu-zako/instance/site.sqlite'
app.config['SECRET_KEY'] = 'd74999cbb56a7040fd3fd6e1bb558896a38931f19f18baf6'

# Initialize db and bcrypt
db.init_app(app)
bcrypt = Bcrypt(app)

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)

client = Together(api_key="e3ab4476326269947afb85e9c0b0ed5fe9ae2949e27ed3a38ee4913d8f807b3e")

VIDEO_DIRECTORY = r"C:\Users\Salome\Desktop\Fahamu Haki Zako"
AUDIO_DIRECTORY = r"C:\Users\Salome\Desktop\Fahamu Haki Zako"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/video/<filename>')
def serve_video(filename):
    return send_from_directory(VIDEO_DIRECTORY, filename)

def get_summary_persona(delivery_method, pdf_text):
    personas = {
        "text": "Summarize the following document...",
        "visual": "Summarize with visuals...",
        "audio": "Summarize for audio...",
        "video": "Summarize for video..."
    }

    prompt = personas.get(delivery_method, "Invalid method.")

    if delivery_method in ["text", "visual"]:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
            messages=[{"role": "system", "content": prompt},
                      {"role": "user", "content": f"Summarize this document:\n{pdf_text}"}],
            max_tokens=512
        )
        return response.choices[0].message.content if response.choices else None
    elif delivery_method in ["audio", "video"]:
        return pdf_text[:200] + "..."
    return "Invalid method."

def generate_video(summary_text):
    tts_engine = pyttsx3.init()
    audio_file = "summary_audio.mp3"
    video_file = "summary_video.mp4"

    tts_engine.save_to_file(summary_text, audio_file)
    tts_engine.runAndWait()

    video_clip = mp.TextClip(summary_text, fontsize=24, color='white', bg_color='black', size=(1280, 720))
    video_clip = video_clip.set_duration(10).set_audio(mp.AudioFileClip(audio_file))
    video_clip.write_videofile(video_file, fps=24)

    return video_file

@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/summarize', methods=['POST'])
def summarize_pdf():
    pdf_file_path = r'./static/Kampala_Convention.pdf'
    if not os.path.exists(pdf_file_path):
        return jsonify({"error": "PDF not found."}), 404

    pdf_text = ""
    pdf_reader = PyPDF2.PdfReader(pdf_file_path)
    for page in pdf_reader.pages:
        try:
            pdf_text += (page.extract_text() or "") + '\n'
        except Exception as e:
            print(f"Error extracting text: {e}")

    if not pdf_text.strip():
        return jsonify({"error": "No text found in PDF."}), 400

    delivery_method = request.json.get('delivery_method', 'text')
    summary = get_summary_persona(delivery_method, pdf_text)

    if delivery_method == "audio":
        tts_engine = pyttsx3.init()
        tts_engine.save_to_file(summary, os.path.join(AUDIO_DIRECTORY, "summary_audio.mp3"))
        tts_engine.runAndWait()

    if delivery_method == "video":
        video_file_path = generate_video(summary)
        return jsonify({"video_url": f"/video/{os.path.basename(video_file_path)}"}), 200

    return jsonify({"summary": summary}), 200

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No message provided."}), 400

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
        messages=[{"role": "system", "content": "You are an assistant."},
                  {"role": "user", "content": user_message}],
        max_tokens=512
    )

    return jsonify({"reply": response.choices[0].message.content if response.choices else "Error"}), 200

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Create the user object without the password
            user = User(username=form.username.data, email=form.email.data)

            # Use the set_password method to hash and set the password
            user.set_password(form.password.data)

            # Add the new user to the database and commit the transaction
            db.session.add(user)
            db.session.commit()

            # Log in the user right after registration
            login_user(user)
            return redirect(url_for('index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template('register.html', title='Register', form=form)

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
    
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         try:
#             hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
#             user = User(username=form.username.data, email=form.email.data, password=hashed_password)
#             db.session.add(user)
#             db.session.commit()
#             login_user(user)
#             return redirect(url_for('index'))
#         except Exception as e:
#             db.session.rollback()
#             flash(f'Error: {str(e)}', 'danger')

#     return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid email or password.', 'danger')

    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/my_account')
@login_required
def my_account():
    return render_template('my_account.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
