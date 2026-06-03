from flask import Flask, render_template, request
import os
import numpy as np
import cv2
import base64
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def decrypt_from_npy_to_base64(npy_path):
    K, encrypted, w, h, channel = np.load(npy_path, allow_pickle=True)

    encrypted = np.array(encrypted).astype(np.int64)
    K = np.array(K).astype(np.int64)

    I0 = encrypted.ravel()

    decrypted = []
    for i in range(len(I0)):
        decrypted.append(I0[i] ^ K[i])

    decrypted = np.array(decrypted, dtype=np.uint8)
    decrypted = np.reshape(decrypted, (w, h, channel))

    ok, buffer = cv2.imencode(".png", decrypted)
    if not ok:
        raise Exception("Image encode failed")

    img_base64 = base64.b64encode(buffer).decode("utf-8")
    return img_base64


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/decrypt", methods=["POST"])
def decrypt():
    if "keyfile" not in request.files:
        return render_template("index.html", message="Please upload .npy file")

    file = request.files["keyfile"]

    if file.filename == "":
        return render_template("index.html", message="No file selected")

    filename = secure_filename(file.filename)

    if not filename.lower().endswith(".npy"):
        return render_template("index.html", message="Only .npy file allowed")

    npy_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(npy_path)

    try:
        decrypted_image_base64 = decrypt_from_npy_to_base64(npy_path)
        return render_template(
            "index.html",
            message="Decryption completed successfully",
            decrypted_image=decrypted_image_base64
        )
    except Exception as e:
        return render_template("index.html", message="Error: " + str(e))


if __name__ == "__main__":
    app.run(debug=True)