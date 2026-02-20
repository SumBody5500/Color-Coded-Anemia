import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
from werkzeug.utils import secure_filename
import random

app = Flask(__name__, static_folder='build', static_url_path='')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_interpretation(score: float) -> str:
    if score < 25:
        return "Low risk"
    elif score < 50:
        return "Mild concern"
    elif score < 75:
        return "Moderate concern"
    else:
        return "High concern"

""""
def analyze_eye_color(image_path: str) -> dict:
    Analyze eye conjunctiva color for anemia detection.
    Heuristic:
      - Lower red channel and lower R/G ratio → more pallor → higher anemia score.
    try:
        img = cv2.imread(image_path)
        if img is None:
            return {"error": "Failed to load image", "score": 0}

        # Convert to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Focus on central region (approx conjunctiva ROI)
        h, w = img_rgb.shape[:2]
        center_region = img_rgb[int(h * 0.3):int(h * 0.7), int(w * 0.3):int(w * 0.7)]

        # Mean RGB
        mean_r = np.mean(center_region[:, :, 0])
        mean_g = np.mean(center_region[:, :, 1])
        mean_b = np.mean(center_region[:, :, 2])

        rg_ratio = mean_r / (mean_g + 1e-6)

        score = 0.0

        # Red channel (40%)
        if mean_r < 100:
            score += 40
        elif mean_r < 130:
            score += 30
        elif mean_r < 160:
            score += 15

        # R/G ratio (40%)
        if rg_ratio < 0.9:
            score += 40
        elif rg_ratio < 1.0:
            score += 30
        elif rg_ratio < 1.1:
            score += 15

        # Brightness (20%)
        brightness = (mean_r + mean_g + mean_b) / 3.0
        if brightness < 100:
            score += 20
        elif brightness < 140:
            score += 10

        score = min(score, 100)

        return {
            "score": float(score),
            "mean_r": float(mean_r),
            "mean_g": float(mean_g),
            "mean_b": float(mean_b),
            "rg_ratio": float(rg_ratio),
            "brightness": float(brightness),
            "interpretation": get_interpretation(score),
        }
    except Exception as e:
        return {"error": str(e), "score": 0}


def analyze_tongue_color(image_path: str) -> dict:
    
    Analyze tongue color for anemia detection.
    Heuristic:
      - Healthy tongue: pink/red, higher R and saturation, R > G.
      - Anemic: pale, low R, low saturation, R ≈ G.
    
    try:
        img = cv2.imread(image_path)
        if img is None:
            return {"error": "Failed to load image", "score": 0}

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        h, w = img_rgb.shape[:2]
        center_region_rgb = img_rgb[int(h * 0.25):int(h * 0.75), int(w * 0.25):int(w * 0.75)]
        center_region_hsv = img_hsv[int(h * 0.25):int(h * 0.75), int(w * 0.25):int(w * 0.75)]

        mean_r = np.mean(center_region_rgb[:, :, 0])
        mean_g = np.mean(center_region_rgb[:, :, 1])
        mean_b = np.mean(center_region_rgb[:, :, 2])
        mean_saturation = np.mean(center_region_hsv[:, :, 1]) / 255.0

        score = 0.0

        # Red channel (35%)
        if mean_r < 100:
            score += 35
        elif mean_r < 130:
            score += 25
        elif mean_r < 160:
            score += 12

        # Saturation (35%)
        if mean_saturation < 0.15:
            score += 35
        elif mean_saturation < 0.25:
            score += 25
        elif mean_saturation < 0.35:
            score += 12

        # R - G (30%)
        r_g_diff = mean_r - mean_g
        if r_g_diff < 5:
            score += 30
        elif r_g_diff < 15:
            score += 20
        elif r_g_diff < 25:
            score += 10

        score = min(score, 100)

        return {
            "score": float(score),
            "mean_r": float(mean_r),
            "mean_g": float(mean_g),
            "mean_b": float(mean_b),
            "saturation": float(mean_saturation),
            "r_g_diff": float(r_g_diff),
            "interpretation": get_interpretation(score),
        }
    except Exception as e:
        return {"error": str(e), "score": 0}


def analyze_nail_color(image_path: str) -> dict:
    
    Analyze fingernail color for anemia detection.
    Heuristic:
      - Healthy nail bed: pink (R > G,B), decent saturation.
      - Anemic: pale/whitish, low R, low saturation, R close to B.
    
    try:
        img = cv2.imread(image_path)
        if img is None:
            return {"error": "Failed to load image", "score": 0}

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        h, w = img_rgb.shape[:2]
        center_region_rgb = img_rgb[int(h * 0.3):int(h * 0.7), int(w * 0.3):int(w * 0.7)]
        center_region_hsv = img_hsv[int(h * 0.3):int(h * 0.7), int(w * 0.3):int(w * 0.7)]

        mean_r = np.mean(center_region_rgb[:, :, 0])
        mean_g = np.mean(center_region_rgb[:, :, 1])
        mean_b = np.mean(center_region_rgb[:, :, 2])
        mean_saturation = np.mean(center_region_hsv[:, :, 1]) / 255.0

        score = 0.0

        # Red channel (40%)
        if mean_r < 110:
            score += 40
        elif mean_r < 140:
            score += 28
        elif mean_r < 170:
            score += 15

        # Saturation (30%)
        if mean_saturation < 0.10:
            score += 30
        elif mean_saturation < 0.20:
            score += 20
        elif mean_saturation < 0.30:
            score += 10

        # R - B (30%) – healthy should have R > B
        r_b_diff = mean_r - mean_b
        if r_b_diff < 0:
            score += 30
        elif r_b_diff < 10:
            score += 20
        elif r_b_diff < 25:
            score += 10

        score = min(score, 100)

        return {
            "score": float(score),
            "mean_r": float(mean_r),
            "mean_g": float(mean_g),
            "mean_b": float(mean_b),
            "saturation": float(mean_saturation),
            "r_b_diff": float(r_b_diff),
            "interpretation": get_interpretation(score),
        }
    except Exception as e:
        return {"error": str(e), "score": 0}
"""
def analyze_eye_color(image_path):
    score = random.randint(0, 100)
    return {
        "score": score,
        "mean_r": score,  # Just for demonstration
        "mean_g": score,
        "mean_b": score,
        "rg_ratio": 1.0,
        "brightness": score,
        "interpretation": get_interpretation(score)
    }

def analyze_tongue_color(image_path):
    score = random.randint(0, 100)
    return {
        "score": score,
        "mean_r": score,
        "mean_g": score,
        "mean_b": score,
        "saturation": 0.5,
        "r_g_diff": 0,
        "interpretation": get_interpretation(score)
    }

def analyze_nail_color(image_path):
    score = random.randint(0, 100)
    return {
        "score": score,
        "mean_r": score,
        "mean_g": score,
        "mean_b": score,
        "saturation": 0.5,
        "r_b_diff": 0,
        "interpretation": get_interpretation(score)
    }


def normalize_scores(eye_score: float, tongue_score: float, nail_score: float) -> float:
    """
    Weighted combination:
      eye: 40%, tongue: 35%, nail: 25%.
    """
    eye_weight = 0.40
    tongue_weight = 0.35
    nail_weight = 0.25
    final_score = eye_score * eye_weight + tongue_score * tongue_weight + nail_score * nail_weight
    return round(final_score, 2)


def get_recommendation(final_score: float) -> dict:
    if final_score < 30:
        risk_level = "Low Risk"
        recommendation = (
            "Your results indicate a low risk of anemia. Continue maintaining a balanced diet rich in iron."
        )
        dietary_advice = [
            "Include iron-rich foods: red meat, poultry, fish, beans, lentils",
            "Consume vitamin C-rich foods to enhance iron absorption: citrus fruits, tomatoes, peppers",
            "Include dark leafy greens: spinach, kale, collard greens",
            "Eat fortified cereals and whole grains",
        ]
        action = "maintain_diet"
    elif final_score < 55:
        risk_level = "Mild Risk"
        recommendation = (
            "Your results suggest mild anemia indicators. Focus on improving your iron intake through diet."
        )
        dietary_advice = [
            "Increase consumption of iron-rich foods: red meat (3–4 times/week), liver, shellfish",
            "Pair iron sources with vitamin C: have orange juice with iron-fortified cereal",
            "Add more legumes: chickpeas, black beans, kidney beans (daily)",
            "Snack on dried fruits: raisins, apricots, prunes",
            "Cook in cast iron cookware to increase iron content",
            "Avoid tea/coffee with meals as they reduce iron absorption",
        ]
        action = "dietary_changes"
    else:
        risk_level = "Moderate to High Risk"
        recommendation = (
            "Your results indicate moderate to high anemia risk. Please consult a healthcare provider for proper evaluation and testing."
        )
        dietary_advice = [
            "Seek medical consultation for blood tests (Complete Blood Count)",
            "A doctor may prescribe iron supplements",
            "Continue eating iron-rich foods under medical guidance",
            "Get evaluated for underlying causes",
        ]
        action = "consult_doctor"

    return {
        "risk_level": risk_level,
        "final_score": float(final_score),
        "recommendation": recommendation,
        "dietary_advice": dietary_advice,
        "action": action,
    }


@app.route("/api/analyze", methods=["POST"])
def analyze_images():
    """
    Main endpoint:
    - Expects multipart/form-data with fields: eye, tongue, nail
    - Returns per-image scores + combined score + recommendation
    """
    try:
        if "eye" not in request.files or "tongue" not in request.files or "nail" not in request.files:
            return jsonify({"error": "Missing required images. Please upload eye, tongue, and nail images."}), 400

        eye_file = request.files["eye"]
        tongue_file = request.files["tongue"]
        nail_file = request.files["nail"]

        # Validate filenames
        if (
            eye_file.filename == ""
            or tongue_file.filename == ""
            or nail_file.filename == ""
        ):
            return jsonify({"error": "One or more files have empty filename."}), 400

        if not (
            allowed_file(eye_file.filename)
            and allowed_file(tongue_file.filename)
            and allowed_file(nail_file.filename)
        ):
            return jsonify({"error": "Invalid file format. Please upload PNG, JPG, or JPEG images."}), 400

        # Save files
        eye_path = os.path.join(app.config["UPLOAD_FOLDER"], "eye_" + secure_filename(eye_file.filename))
        tongue_path = os.path.join(app.config["UPLOAD_FOLDER"], "tongue_" + secure_filename(tongue_file.filename))
        nail_path = os.path.join(app.config["UPLOAD_FOLDER"], "nail_" + secure_filename(nail_file.filename))

        eye_file.save(eye_path)
        tongue_file.save(tongue_path)
        nail_file.save(nail_path)

        print(f"Files saved: {eye_path}, {tongue_path}, {nail_path}")

        # Analyze
        eye_results = analyze_eye_color(eye_path)
        tongue_results = analyze_tongue_color(tongue_path)
        nail_results = analyze_nail_color(nail_path)

        print(
            "Analysis complete - Eye: {e}, Tongue: {t}, Nail: {n}".format(
                e=eye_results.get("score", 0),
                t=tongue_results.get("score", 0),
                n=nail_results.get("score", 0),
            )
        )

        # Combined score
        final_score = normalize_scores(
            eye_results.get("score", 0.0),
            tongue_results.get("score", 0.0),
            nail_results.get("score", 0.0),
        )

        recommendation = get_recommendation(final_score)

        # Cleanup
        for p in [eye_path, tongue_path, nail_path]:
            try:
                os.remove(p)
            except OSError:
                pass

        return jsonify(
            {
                "success": True,
                "eye_analysis": eye_results,
                "tongue_analysis": tongue_results,
                "nail_analysis": nail_results,
                "final_score": final_score,
                "recommendation": recommendation,
            }
        )

    except Exception as e:
        print(f"Error in analysis: {str(e)}")
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


@app.route("/")
def serve_index():
    # For production build: serve React app
    index_path = os.path.join(app.static_folder, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(app.static_folder, "index.html")
    return jsonify({"message": "Frontend build not found. Run React build and place it in ./build"}), 200


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "message": "Server is running"})


if __name__ == "__main__":
    print("Starting Anemia Detection Server...")
    print("Server running on http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)

