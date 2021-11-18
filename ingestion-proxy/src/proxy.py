from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
app.config['TARGET_URL'] = 'http://localhost:5001/invocations'


@app.route("/invocations", methods=["POST"])
def index():
    response = requests.post(
        app.config['TARGET_URL'], json=request.json, timeout=30)

    if response.status_code == 200:
        print(request.json)
        print(response.json())

    return jsonify(response.json())


if __name__ == "__main__":
    app.run()
