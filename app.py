from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import base64  # For handling the image data from the camera.

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Directory to store uploaded photos (make sure this exists!)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size (adjust as needed)


# Ensure upload directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

messages = []  # Simple in-memory storage for messages (replace with a database in a real app)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        message_text = request.form.get('message')  # Get text from a regular text input
        uploaded_photo = request.files.get('photo')  # Get file from a standard file input
        photo_data = request.form.get('photoData')  # Get base64 encoded data from the camera


        if message_text:
             messages.append({'text': message_text, 'image': None})


        if uploaded_photo and uploaded_photo.filename != '':
            # Handle file upload from the standard file input
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_photo.filename)
            uploaded_photo.save(filepath)  # Save the uploaded photo
            messages.append({'text': None, 'image': url_for('static', filename='uploads/' + uploaded_photo.filename)})

        elif photo_data:
            # Handle camera image data (base64 encoded)
            try:
                # Extract the base64 encoded image data (remove the "data:image/jpeg;base64," prefix)
                image_data = photo_data.split(',', 1)[1]
                image_bytes = base64.b64decode(image_data)

                # Create a unique filename (using a timestamp is a simple way)
                import time
                filename = f"camera_image_{int(time.time())}.jpg"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
                messages.append({'text': None, 'image': url_for('static', filename='uploads/' + filename)})

            except Exception as e:
                print(f"Error processing camera image: {e}")  # Log the error
                return "Error processing image", 400 # Return a 400 Bad Request error
        return redirect(url_for('index'))  # Redirect to avoid form resubmission


    return render_template('index.html', messages=messages)

@app.route('/get_messages')
def get_messages():
    return jsonify(messages)

@app.route('/clear_messages', methods=['POST'])
def clear_messages():
    global messages
    messages = []

    # Clear the uploads folder
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) # added host and port
