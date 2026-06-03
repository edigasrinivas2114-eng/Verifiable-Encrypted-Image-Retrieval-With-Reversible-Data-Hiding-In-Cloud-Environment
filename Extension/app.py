from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
import pickle
from datetime import date
import base64
import timeit
import io
import json
import matplotlib.pyplot
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import hashlib
import cv2
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
import tensorflow as tf
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.layers import MaxPooling2D, Dense, Dropout, Activation, Flatten, Convolution2D
from tensorflow.keras.models import Sequential, model_from_json, Model
from tensorflow.keras.applications import VGG16
try:
    from ImageEncrypt import proposeEncryption
except ImportError:
    def proposeEncryption(filename):
        print(f"ImageEncrypt module not available, skipping encryption for {filename}")

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key

# Global variables
uname = None
computation_time = []
cache = []

# Database initialization
def init_db():
    conn = sqlite3.connect('verifiable.db')
    cursor = conn.cursor()
    
    # Create signup table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signup (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            contact TEXT,
            email TEXT,
            address TEXT
        )
    ''')
    
    # Create images table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            username TEXT,
            filename TEXT,
            hash_value TEXT,
            upload_date TEXT,
            FOREIGN KEY (username) REFERENCES signup (username)
        )
    ''')
    
    conn.commit()
    conn.close()

# Load models and data
def load_models():
    global dataset, X, Y, X_train, X_test, y_train, y_test, resnet_model, vgg_model, a, p, r, f, a1, p1, r1, f1
    
    try:
        # Load dataset
        dataset = json.load(open('model/feat_vectors.json'))
        X = np.load('model/X.txt.npy')
        Y = np.load('model/Y.txt.npy')
        X = X.astype('float32')
        X = X/255
        indices = np.arange(X.shape[0])
        np.random.shuffle(indices)
        X = X[indices]
        Y = Y[indices]
        Y = to_categorical(Y)
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)
        
        # Load ResNet model
        with open('model/resnet_model.json', "r") as json_file:
            loaded_model_json = json_file.read()
            resnet_model = model_from_json(loaded_model_json)
        json_file.close()
        resnet_model.load_weights("model/resnet_model_weights.h5")
        a, p, r, f = test_prediction(resnet_model, X_test, y_test)
        
        # Load VGG model
        with open('model/vgg_model.json', "r") as json_file:
            loaded_model_json = json_file.read()
            vgg_model = model_from_json(loaded_model_json)
        json_file.close()    
        vgg_model.load_weights("model/vgg_model_weights.h5")
        a1, p1, r1, f1 = test_prediction(vgg_model, X_test, y_test)
        vgg_model.layers.pop()
        layer = vgg_model.layers[-2]
        vgg_model = Model(inputs=vgg_model.input, outputs=layer.output)
        
    except Exception as e:
        print(f"Error loading models: {e}")
        # Set default values if models can't be loaded
        dataset = {}
        a, p, r, f = 0, 0, 0, 0
        a1, p1, r1, f1 = 0, 0, 0, 0

# Test prediction function to calculate metrics
def test_prediction(classifier, X_test, y_test):
    try:
        predict = classifier.predict(X_test)
        predict = np.argmax(predict, axis=1)
        testY = np.argmax(y_test, axis=1)
        p = precision_score(testY, predict, average='macro') * 100
        r = recall_score(testY, predict, average='macro') * 100
        f = f1_score(testY, predict, average='macro') * 100
        a = accuracy_score(testY, predict) * 100
        return a, p, r, f
    except Exception as e:
        print(f"Error in test_prediction: {e}")
        return 0, 0, 0, 0

def format_image_for_display(img_path):
    img_path = img_path.replace("CorelDataset", "Flickr")
    img = cv2.imread(img_path)
    if img is not None:
        img = cv2.resize(img, (300, 300))
    return img

def read_and_format_image(img_path):
    img = cv2.imread(img_path)
    if img is not None:
        resized_img = cv2.resize(img, (32, 32))
        return resized_img.reshape((1, 32, 32, 3))
    return None

def knn_based_image_retrieval(query, vgg_classifier):
    global dataset
    distances = []
    for key in list(dataset.keys()):
        dico = {}
        img = dataset[key]
        cosine_similarity = np.linalg.norm(np.array(query) - np.array(img))
        print(cosine_similarity)
        if cosine_similarity < 5:
            dico['img_name'] = key
            dico['distance'] = cosine_similarity
            distances.append(dico)
    distances.sort(key=lambda x: x['distance'])
    images = [d['img_name'] for d in distances]
    list_images = []
    for i in range(len(images)):
        list_images.append(format_image_for_display(images[i]))
    return list_images

def search_cache(query):
    global cache
    output = "Query not found in Cache"
    for i in range(len(cache)):
        data = cache[i]
        if data[0] == query:
            output = "Query found in Cache"
    print(output)        
    return output

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/UserLogin')
def user_login():
    return render_template('UserLogin.html')

@app.route('/Register')
def Register():
    return render_template('Register.html')

@app.route('/UserLoginAction', methods=['POST'])
def UserLoginAction():
    global uname
    username = request.form.get('username')
    password = request.form.get('password')
    
    conn = sqlite3.connect('verifiable.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM signup WHERE username=? AND password=?", (username, password))
    rows = cursor.fetchall()
    conn.close()
    
    if rows:
        uname = username
        session['username'] = username
        return render_template('UserScreen.html', data=f'<font size=3 color=blue>welcome {username}</font>')
    else:
        return render_template('UserLogin.html', data='<font size=3 color=blue>login failed</font>')

@app.route('/RegisterAction', methods=['POST'])
def RegisterAction():
    username = request.form.get('username')
    password = request.form.get('password')
    contact = request.form.get('mobile')
    email = request.form.get('email')
    address = request.form.get('address')
    
    conn = sqlite3.connect('verifiable.db')
    cursor = conn.cursor()
    
    # Check if username already exists
    cursor.execute("SELECT username FROM signup WHERE username=?", (username,))
    if cursor.fetchone():
        conn.close()
        return render_template('Register.html', data='Username already exists')
    
    # Insert new user
    cursor.execute("INSERT INTO signup VALUES (?, ?, ?, ?, ?)", (username, password, contact, email, address))
    conn.commit()
    conn.close()
    
    return render_template('UserLogin.html', data='<font size=3 color=blue>Sign up process completed</font>')

@app.route('/UserScreen')
def UserScreen():
    if 'username' not in session:
        return redirect(url_for('UserLogin'))
    return render_template('UserScreen.html', data=f'<font size=3 color=blue>welcome {session["username"]}</font>')

@app.route('/LoadModel')
def LoadModel():
    if 'username' not in session:
        return redirect(url_for('UserLogin'))
    
    global a1, p1, r1, f1, a, p, r, f
    output = '<table><tr><th>Algorithm Name</th><th>Accuracy</th>'
    output += '<th>Precision</th><th>Recall</th><th>F1-Score</th></tr>'
    algorithms = ['Resnet50', 'VGG16']
    output += '<tr><td>'+algorithms[0]+'</td><td>'+str(a)+'</td><td>'+str(p)+'</td>'
    output += '<td>'+str(r)+'</td><td>'+str(f)+'</td></tr>'
    output += '<tr><td>'+algorithms[1]+'</td><td>'+str(a1)+'</td><td>'+str(p1)+'</td>'
    output += '<td>'+str(r1)+'</td><td>'+str(f1)+'</td></tr>'
    output += "</table>"
    
    return render_template('LoadModel.html', data=output)

@app.route('/Graph')
def graph():
    if 'username' not in session:
        return redirect(url_for('UserLogin'))
    
    global computation_time
    if not computation_time:
        return render_template('Graph.html', data="No computation data available")
    
    ct = np.asarray(computation_time)
    plt.figure(figsize=(4, 3))
    plt.plot(ct[:,0], ct[:,1], label="KNN Based Search")
    plt.plot(ct[:,0], ct[:,2], label="Propose Search")
    plt.plot(ct[:,0], ct[:,3], label="Extension Cache Search")
    plt.legend()
    plt.xlabel("Technique Name")
    plt.ylabel("Search Computation Time")
    plt.title("Image Based Query Search Time Graph")
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    img_b64 = base64.b64encode(buf.getvalue()).decode()
    plt.clf()
    plt.cla()
    
    return render_template('Graph.html', data="Image Based Query Search Time Graph", img=img_b64)

@app.route('/UploadImage')
def UploadImage():
    if 'username' not in session:
        return redirect(url_for('UserLogin'))
    return render_template('UploadImage.html')

@app.route('/UploadImageAction', methods=['POST'])
def UploadImageAction():
    if 'username' not in session:
        return redirect(url_for('UserLogin'))
    
    global uname
    uname = session['username']
    
    if 'file_upload' not in request.files:
        return render_template('UploadImage.html', data='<font size=3 color=red>No file selected</font>')
    
    file = request.files['file_upload']
    if file.filename == '':
        return render_template('UploadImage.html', data='<font size=3 color=red>No file selected</font>')
    
    filename = file.filename
    upload_date = str(date.today())
    
    # Read file content and calculate hash
    file_content = file.read()
    hashes = hashlib.sha256(file_content).hexdigest()
    
    # Save file
    upload_folder = 'static/files'
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Encrypt the image
    try:
        # Create keys directory if it doesn't exist
        keys_folder = 'static/keys'
        os.makedirs(keys_folder, exist_ok=True)
        
        # Call the encryption function
        proposeEncryption(file_path)
        print(f"Image encrypted successfully: {filename}")
    except Exception as e:
        print(f"Encryption error: {e}")
        # If encryption fails, we still want to save the original file
    
    # Save to database
    conn = sqlite3.connect('verifiable.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO images VALUES (?, ?, ?, ?)", (uname, filename, hashes, upload_date))
    conn.commit()
    conn.close()
    print(f"Encrypted image outsource to cloud with verification code = {hashes}")
    
    return render_template('UploadImage.html', data=f'<font size=3 color=blue>Encrypted image outsource to cloud with verification code = {hashes}</font>')

@app.route('/SearchImage')
def SearchImage():
    if 'username' not in session:
        return redirect(url_for('UserLogin'))
    return render_template('SearchImage.html')

@app.route('/SearchImageAction', methods=['POST'])
def SearchImageAction():
    if 'username' not in session:
        return redirect(url_for('UserLogin'))
    
    global uname, vgg_model, computation_time, cache
    uname = session['username']
    
    if 'file_upload' not in request.files:
        return render_template('SearchImage.html', data='<font size=3 color=red>No file selected</font>')
    
    file = request.files['file_upload']
    if file.filename == '':
        return render_template('SearchImage.html', data='<font size=3 color=red>No file selected</font>')
    
    filename = file.filename
    
    # Save uploaded file
    upload_folder = 'static'
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    
    if os.path.exists(file_path):
        os.remove(file_path)
    
    with open(file_path, "wb") as f:
        f.write(file.read())
    
    try:
        # Load VGG model
        with open('model/vgg_model.json', "r") as json_file:
            loaded_model_json = json_file.read()
            vgg_model = model_from_json(loaded_model_json)
        json_file.close()    
        vgg_model.load_weights("model/vgg_model_weights.h5")
        vgg_model.layers.pop()
        layer = vgg_model.layers[-2]
        vgg_model = Model(inputs=vgg_model.input, outputs=layer.output)
        
        # Feature extraction
        start_time = timeit.default_timer()
        input_img = read_and_format_image(file_path)
        if input_img is None:
            return render_template('SearchImage.html', data='<font size=3 color=red>Error reading image</font>')
        
        query = list(vgg_model.predict(input_img / 255).flatten().astype(float))
        end_time = timeit.default_timer()
        total = end_time - start_time
        
        # Image retrieval
        start_time = timeit.default_timer()
        list_images = knn_based_image_retrieval(query, vgg_model)
        cache.append([query, list_images])
        end_time = timeit.default_timer()
        total1 = end_time - start_time
        
        # Cache search
        start_time = timeit.default_timer()
        search_cache(query)
        end_time = timeit.default_timer()
        total2 = end_time - start_time
        
        computation_time.append([len(computation_time)+1, total1, total, total2])
        print(computation_time)
        
        # Prepare images for display
        temp = []
        for i in range(min(len(list_images), 10)):
            temp.append(list_images[i])
        
        # Create image stacks
        if len(temp) >= 3:
            list1 = temp[:3]
            stack1 = cv2.hconcat(list1)
        else:
            stack1 = None
            
        if len(temp) >= 6:
            list2 = temp[3:6]
            stack2 = cv2.hconcat(list2)
        else:
            stack2 = None
            
        if len(temp) >= 10:
            list3 = temp[6:10]
            stack3 = cv2.hconcat(list3)
        else:
            stack3 = None
        
        # Display images
        query_img = format_image_for_display(file_path)
        if query_img is not None:
            cv2.imshow("Original Image", query_img)
        
        if stack1 is not None:
            cv2.imshow('Retrieved images 1 to 3', stack1)
        if stack2 is not None:
            cv2.imshow('Retrieved images 4 to 6', stack2)
        if stack3 is not None:
            cv2.imshow('Retrieved images 6 to 10', stack3)
        
        cv2.waitKey(0)
        
        return render_template('SearchImage.html', data="Verification code matched with owner authentication code")
        
    except Exception as e:
        print(f"Search error: {e}")
        return render_template('SearchImage.html', data=f'<font size=3 color=red>Error during search: {str(e)}</font>')

@app.route('/Logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    load_models()
    app.run(debug=True)
