from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the CatchARide API!"})

@app.route('/status')
def status():
    return jsonify({"status": "Server is running"})

if __name__ == '__main__':
    app.run(debug=True)