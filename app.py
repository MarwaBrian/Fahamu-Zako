from together import Together
from flask import Flask, render_template, jsonify, request
import os
import PyPDF2
import pyttsx3  # For text-to-speech functionality (optional)

# Initialize Flask app
app = Flask(__name__)

# Initialize the client with API key
client = Together(api_key="e3ab4476326269947afb85e9c0b0ed5fe9ae2949e27ed3a38ee4913d8f807b3e")

# Define delivery methods
def get_summary_persona(delivery_method, pdf_text):
    # Define prompt personas based on delivery method
    personas = {
        "text": "You are a helpful assistant. Provide a concise summary using bullet points.",
        "visual": "You are a helpful assistant. Use bullet points and suggest visuals to enhance understanding.",
        "audio": "You are a helpful assistant. Provide a brief summary suitable for audio presentation."
    }

    prompt = personas.get(delivery_method, "Please select a valid delivery method.")

    if delivery_method == "text" or delivery_method == "visual":
        # Create a chat completion request to summarize the PDF content
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
        # Return a simplified audio summary (in text format)
        summary = f"Audio Summary of the Document:\n{pdf_text[:200]}..."  # Use only the first 200 characters
        return summary

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize_pdf():
    # Update the path to your PDF file
    pdf_file_path = r'C:\Users\Salome\Desktop\Fahamu Haki Zako\static\Kampala_Convention.pdf'  # Path to your PDF file
    print("Checking for PDF file...")  # Debugging statement

    if os.path.exists(pdf_file_path):
        print("PDF file found. Reading content...")  # Debugging statement
        
        # Read the PDF content
        pdf_reader = PyPDF2.PdfReader(pdf_file_path)
        pdf_text = ''
        
        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:  # Check if text extraction is successful
                pdf_text += page_text + '\n'  # Extract text from each page
            else:
                print(f"Failed to extract text from page {page_num}")  # Use page_num instead of index

        if not pdf_text.strip():
            print("No text extracted from the PDF.")  # Debugging statement
            return jsonify({"error": "No text found in the PDF."}), 400

        # Get delivery method from the request (add to your HTML form)
        delivery_method = request.json.get('delivery_method', 'text')  # Default to text if not provided
        
        # Get summary based on selected delivery method
        summary = get_summary_persona(delivery_method, pdf_text)

        if summary:
            print("Summary generated successfully.")  # Debugging statement
            
            # If audio delivery method is selected, you can use a text-to-speech library to read the summary
            if delivery_method == "audio":
                engine = pyttsx3.init()
                engine.say(summary)
                engine.runAndWait()
            
            return jsonify({"summary": summary}), 200
        else:
            print("No summary generated.")  # Debugging statement
            return jsonify({"error": "No summary generated."}), 500
    else:
        print("PDF file not found.")  # Debugging statement
        return jsonify({"error": "PDF file not found."}), 404

if __name__ == '__main__':
    app.run(debug=True)
