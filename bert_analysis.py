import pandas as pd
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from sklearn.cluster import KMeans


# ---------------- EXPRESSIVE PRAISE RULES ----------------

PRAISE_WORDS = [
    "love", "slay", "slayed", "slaying", "queen", "king",
    "fire", "lit", "iconic", "legend", "amazing", "perfect",
    "obsessed", "goat", "best"
]

PRAISE_EMOJIS = ["🔥", "❤️", "😍", "🫶", "👑", "😂", "😭"]

def contains_expressive_praise(text: str) -> bool:
    text_lower = text.lower()

    for word in PRAISE_WORDS:
        if word in text_lower:
            return True

    for emoji in PRAISE_EMOJIS:
        if emoji in text:
            return True

    return False


# Load models once
#bert_model = SentenceTransformer("all-MiniLM-L6-v2") ---for bert
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment",
    tokenizer="cardiffnlp/twitter-roberta-base-sentiment"
)

LABEL_MAP = {
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive"
}


"""def analyze_comments(comments):
    df = pd.DataFrame(comments, columns=["comment"])

    # BERT embeddings
    embeddings = bert_model.encode(df["comment"].tolist())

    # Sentiment
    df["sentiment"] = df["comment"].apply(
        lambda x: sentiment_pipeline(x)[0]["label"]
    )
    df["confidence"] = df["comment"].apply(
        lambda x: sentiment_pipeline(x)[0]["score"]
    )

    # Clustering
    kmeans = KMeans(n_clusters=2, random_state=42)
    df["cluster"] = kmeans.fit_predict(embeddings)

    # Polarisation score
    cluster_score = df.groupby("cluster")["confidence"].mean()
    polarisation_score = abs(cluster_score[0] - cluster_score[1])

    return df, polarisation_score """


def analyze_comments(comments):

     # 🔴 SAFETY CHECK
    if not comments or len(comments) == 0:
        empty_df = pd.DataFrame(columns=["comment", "sentiment", "confidence"])
        return empty_df, 0.0

    data = []

    for comment in comments:
        result = sentiment_pipeline(comment[:512])[0]

        sentiment = LABEL_MAP[result["label"]]
        confidence = result["score"]

        if sentiment == "neutral" and confidence > 0.7:
            if contains_expressive_praise(comment):
                sentiment = "positive-expressive"

        data.append({
            "comment": comment,
            "sentiment": sentiment,
            "confidence": confidence
        })

    df = pd.DataFrame(data)

    pos = (df["sentiment"] == "positive").sum()
    neg = (df["sentiment"] == "negative").sum()
    total = len(df)

    polarisation_score = abs(pos - neg) / total if total > 0 else 0

    return df, polarisation_score
