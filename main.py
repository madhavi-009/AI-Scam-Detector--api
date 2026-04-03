
import pickle
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow Flutter app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model
with open("scam_model.pkl", "rb") as f:
    model = pickle.load(f)
with open("scam_vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

class Message(BaseModel):
    text: str

@app.get("/")
def home():
    return {"status": "Scam Detector API is running!"}

@app.post("/predict")
def predict(msg: Message):
    text_lower = msg.text.lower()

    # Indian scam keywords boost
    keywords = ["otp", "kyc", "blocked", "lottery", "prize",
                "urgent", "verify", "click here", "refund",
                "disconnected", "customs", "bit.ly"]

    keyword_found = [k for k in keywords if k in text_lower]
    boost = 0.15 if keyword_found else 0.0

    vec = vectorizer.transform([msg.text])
    prob = model.predict_proba(vec)[0]
    scam_score = min(1.0, float(prob[1]) + boost)

    return {
        "scam_probability": round(scam_score, 2),
        "is_scam": scam_score > 0.5,
        "risk_level": "HIGH" if scam_score > 0.8 else
                      "MEDIUM" if scam_score > 0.5 else "LOW",
        "keywords_found": keyword_found
    }
