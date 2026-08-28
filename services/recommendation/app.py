from flask import Flask, jsonify, request
from flask_cors import CORS
from recommendation import DEFAULT_WEIGHTS, MODEL_VERSION, rank_programs

app = Flask(__name__)
CORS(app)

@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "recommendation-service", "modelVersion": MODEL_VERSION})

@app.post("/api/v1/recommendations")
def recommendations():
    payload = request.get_json(silent=True) or {}
    profile, programs = payload.get("profile"), payload.get("programs")
    if not isinstance(profile, dict) or not isinstance(programs, list):
        return jsonify({"message": "profile must be an object and programs must be an array"}), 400
    weights = payload.get("weights") if isinstance(payload.get("weights"), dict) else DEFAULT_WEIGHTS
    return jsonify({"items": rank_programs(profile, programs, weights), "modelVersion": MODEL_VERSION, "weights": weights,
                    "disclaimer": "推荐结果仅供择校参考，不构成录取承诺。请以对应年度院校官方发布信息为准。"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)