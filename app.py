from together import Together
from flask import Flask, render_template, jsonify, request, send_file, send_from_directory, flash, redirect, url_for, request
import os
import PyPDF2
import pyttsx3  # For text-to-speech functionality
# Example import for video generation (use any video generation library or API)
import moviepy.editor as mp  # For generating a basic video using text-to-speech
from flask_login import current_user, login_required, logout_user, login_user
from app import db, bcrypt
from models import User
from forms import RegistrationForm, LoginForm
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"

# Initialize Flask app
app = Flask(__name__)
# Define paths
VIDEO_DIRECTORY = r"C:\Users\Salome\Desktop\Fahamu Haki Zako"
AUDIO_DIRECTORY = r"C:\Users\Salome\Desktop\Fahamu Haki Zako"

@app.route('/video/<filename>')
def serve_video(filename):
    return send_from_directory(VIDEO_DIRECTORY, filename)

# Initialize the client with API key
client = Together(api_key="e3ab4476326269947afb85e9c0b0ed5fe9ae2949e27ed3a38ee4913d8f807b3e")

# Define delivery methods
def get_summary_persona(delivery_method, pdf_text):
    personas = {
        "text": "You are a helpful assistant who explains legal documents in simple terms. Summarize the following document, organizing the summary into easy-to-understand sections with clear headings, and highlighting the main points and any important terms. Replace the asterics with html tags for headings",
        "visual": "You are a helpful assistant who explains legal documents in simple terms. Summarize the following document by organizing the content into easy-to-understand sections with clear headings, and suggest visuals that could help clarify the concepts.",
        "audio": "You are a helpful assistant who explains legal documents in simple terms. Summarize the following document clearly, focusing on the main ideas and using straightforward language to ensure it's suitable for an audio presentation.",
        "video": "You are a helpful assistant who explains legal documents in simple terms. Summarize the following document, organizing it into well-defined sections with headings, and ensuring the summary is suitable for video presentation."
    }


    prompt = personas.get(delivery_method, "Please select a valid delivery method.")

    # Handle text, visual, and audio requests as before
    if delivery_method in ["text", "visual"]:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": f"Summarize the following document:\n{pdf_text}"
                }
            ],
            max_tokens=512,
            temperature=0.7,
            top_p=0.7,
            top_k=50,
            repetition_penalty=1,
            stop=["<|eot_id|>", "<|eom_id|>"],
        )

        if response.choices:
            return response.choices[0].message.content
        else:
            return None
    elif delivery_method == "audio":
        summary = f"Audio Summary of the Document:\n{pdf_text[:200]}..."  # First 200 characters for audio
        return summary
    elif delivery_method == "video":
        summary = f"Video Summary of the Document:\n{pdf_text[:200]}..."  # First 200 characters for video
        return summary
    else:
        return "Invalid delivery method selected."


def generate_video(summary_text):
    # Generate a basic video using moviepy or any other video generation tool
    tts_engine = pyttsx3.init()
    audio_file = "summary_audio.mp3"
    video_file = "summary_video.mp4"

    # Create audio from text using pyttsx3
    tts_engine.save_to_file(summary_text, audio_file)
    tts_engine.runAndWait()

    # Generate a video (simple video with text and audio)
    # You can customize this section for more sophisticated video generation
    video_clip = mp.TextClip(summary_text, fontsize=24, color='white', bg_color='black', size=(1280, 720))
    video_clip = video_clip.set_duration(10)
    video_clip = video_clip.set_audio(mp.AudioFileClip(audio_file))

    # Save the video
    video_clip.write_videofile(video_file, fps=24)
    
    return video_file


@app.route('/')
def index():
    return render_template('index.html')

def format_summary_for_html(summary):
    # Split the summary into sections based on headings
    sections = summary.split("\n")
    formatted_summary = ""

    for section in sections:
        if section.strip():  # Ensure the section is not empty
            # Check if the section is a heading (this can be adjusted for your specific headings)
            if section.strip().upper() in ["OVERVIEW", "KEY OBJECTIVES", "KEY PROVISIONS", "KEY PRINCIPLES"]:
                formatted_summary += f"<strong>{section.strip()}</strong><br>"  # Bold heading
            else:
                # If it's not a heading, treat it as a bullet point
                formatted_summary += f"<li>{section.strip()}</li>"

    # Wrap bullet points in an unordered list
    formatted_summary = "<ul>" + formatted_summary + "</ul>"
    
    return formatted_summary


@app.route('/summarize', methods=['POST'])
def summarize_pdf():
    pdf_file_path = r'C:\Users\Salome\Desktop\Fahamu Haki Zako\static\Kampala_Convention.pdf'
    print("Checking for PDF file...")

    if os.path.exists(pdf_file_path):
        print("PDF file found. Reading content...")

        # Read PDF content
        pdf_reader = PyPDF2.PdfReader(pdf_file_path)
        pdf_text = ''
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                pdf_text += page_text + '\n'
            else:
                print(f"Failed to extract text from page {page_num}")

        if not pdf_text.strip():
            return jsonify({"error": "No text found in the PDF."}), 400

        delivery_method = request.json.get('delivery_method', 'text')
        summary = get_summary_persona(delivery_method, pdf_text)

        if summary:
            print("Summary generated successfully.")
            formatted_summary = format_summary_for_html(summary)

            if delivery_method == "audio":
                engine = pyttsx3.init()
                engine.save_to_file(summary, os.path.join(AUDIO_DIRECTORY, "summary_audio.mp3"))
                engine.runAndWait()

            if delivery_method == "video":
                video_file_path = generate_video(summary)
                video_url = f"/video/{os.path.basename(video_file_path)}"
                return jsonify({"video_url": video_url}), 200

            return jsonify({"summary": summary}), 200
        else:
            return jsonify({"error": "No summary generated."}), 500
    else:
        return jsonify({"error": "PDF file not found."}), 404
@app.route('/chat', methods=['POST'])
def chat():
    # Get the user's message from the request
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({"error": "No message provided."}), 400

    # Example: Simple AI chatbot response using your Together client
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant knowledgeable in African human rights instruments. replace the astretics with html heading tags"},
            {"role": "user", "content": user_message}
        ],
        max_tokens=512,
        temperature=0.7
    )

    # If the API responds with a valid reply, return it
    if response and response.choices:
        bot_reply = response.choices[0].message.content
        return jsonify({"reply": bot_reply}), 200

    return jsonify({"reply": "I'm sorry, I couldn't process that. Could you rephrase?"}), 500

url_for = ...
redirect = ...
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return render_template('index.html')
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created successfully! You are now able to log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred. {str(e)} Please try again.', 'danger')
    return render_template('register.html', title='Register', form=form)




if __name__ == '__main__':
    app.run(debug=True)