from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient
from flask_cors import CORS
from bson import ObjectId

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS to allow frontend requests

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")  # MongoDB URL
db = client["reading"]  # Database name
collection = db["testing"]  # Collection name

# Route: Serve the frontend
@app.route('/')
def index():
    """
    Serve the main HTML page.
    """
    return render_template("index.html")

# Route: Fetch exam sets from MongoDB
@app.route('/api/exam_sets', methods=['GET'])
def get_exam_sets():
    """
    Fetch exam sets (questions and content) from MongoDB.
    """
    try:
        data = list(collection.find({}))  # Fetch all documents
        for item in data:
            item['_id'] = str(item['_id'])  # Convert ObjectId to string for JSON compatibility
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch exam data: {str(e)}"}), 500

# Route: Submit answers and evaluate
@app.route('/submit', methods=['POST'])
def submit_answers():
    """
    Handle the submission of user answers, compare them with correct answers,
    and return the results.
    """
    try:
        user_data = request.get_json()  # Get JSON data from the frontend
        user_answers = user_data.get('answers', {})

        # Fetch exam data to validate answers
        exam_data = list(collection.find({}))
        correct_answers = {}

        # Extract correct answers
        for exam_set in exam_data:
            for passage in exam_set.get("passages", []):
                for question_group in passage.get("questions", {}).values():
                    for item in question_group.get("items", []):
                        correct_answers[item["question"]] = item["answer"]

        # Compare user answers with correct answers
        results = {}
        for question, correct_answer in correct_answers.items():
            user_answer = user_answers.get(question, "").strip()
            is_correct = user_answer.lower() == correct_answer.lower() if user_answer else False
            results[question] = {
                "user_answer": user_answer if user_answer else None,
                "correct_answer": correct_answer,
                "is_correct": is_correct
            }

        return jsonify({
            "message": "Answers evaluated successfully",
            "results": results
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to process answers: {str(e)}"}), 500

# Start the Flask server
if __name__ == "__main__":
    app.run(debug=True)
