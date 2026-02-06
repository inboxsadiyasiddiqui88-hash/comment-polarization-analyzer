from youtube_fetch import extract_video_id, get_youtube_comments
import streamlit as st
import pandas as pd
#import matplotlib.pyplot as plt
import plotly.express as px 
from youtube_fetch import get_youtube_comments
from bert_analysis import analyze_comments

st.markdown("""
<style>
.metric-label {
    font-size: 18px !important;
}
.metric-value {
    font-size: 32px !important;
    color: #ff4b4b;
}
</style>
""", unsafe_allow_html=True)


st.set_page_config(page_title="Comment Polarisation Analyzer")

st.title("🧠 Comment Section Polarisation Analyzer (BERT-Based)")

source = st.radio("Select Data Source:", ["YouTube"])

comments = []

# ---------------- YOUTUBE ----------------
if source == "YouTube":

    youtube_link = st.text_input("Enter YouTube video link")

#--Confidence Threshold---
confidence_threshold = st.slider(
    "🎚️ Confidence Threshold",
    min_value=0.0,
    max_value=1.0,
    value=0.6,
    step=0.05,
    help="Predictions below this confidence are treated as neutral to avoid wrong sentiment classification."
)

if st.button("Fetch & Analyze"):

        if not youtube_link:
            st.error("Please enter a YouTube link")
            st.stop()

        try:
            video_id = extract_video_id(youtube_link)
        except ValueError:
            st.error("Invalid YouTube link")
            st.stop()

        with st.spinner("Fetching YouTube comments..."):
            comments = get_youtube_comments(video_id)

        if not comments:
            st.warning("No comments found")
            st.stop()

if not comments:
    st.warning("No comments fetched yet. Please enter a valid link.")
    st.stop()

st.divider()

# ---------------- REDDIT CSV ----------------
#if source == "Reddit CSV":
#    uploaded_file = st.file_uploader("Upload Reddit Comments CSV", type="csv")
#
#   if uploaded_file:
#       df = pd.read_csv(uploaded_file)
#       comments = df["comment"].tolist()

# ---------------- ANALYSIS ----------------
with st.spinner("Analyzing comments using BERT..."):
    result_df, polarisation_score = analyze_comments(comments)


# Preserve raw sentiment
result_df["sentiment_raw"] = result_df["sentiment"]


#---applying confidence filter
result_df["sentiment_adjusted"] = result_df.apply (
    lambda row: "neutral"
    if row["confidence"] < confidence_threshold
    else row["sentiment_raw"],
    axis=1 ) 

DISPLAY_LABELS = {
    "positive": "Positive",
    "negative": "Negative",
    "neutral": "Neutral",
    "positive-expressive": "Expressive Positive"
}

#result_df["sentiment_display"] = result_df["sentiment"].map(DISPLAY_LABELS)


#----------VIEW ANALYZED COMMENTS------------
with st.expander("📄 View Analyzed Comments"):
    st.dataframe(
        result_df[[
            "comment",
            "sentiment_raw",
            "confidence",
            "sentiment_adjusted"
        ]])
    
st.divider()
st.subheader("📊 Analysis Overview")

col1, col2 = st.columns(2)

with col1:
    st.metric("Polarisation Score", round(polarisation_score, 3))

with col2:
    st.metric("Total Comments Analysed", len(result_df))

pos = result_df["sentiment"].isin(["positive", "positive-expressive"]).sum()
neg = (result_df["sentiment"] == "negative").sum()
neu = (result_df["sentiment"] == "neutral").sum()

total = len(result_df)
polarisation_score = abs(pos - neg) / total if total > 0 else 0

st.divider()

#---PIE-CHART-----

st.markdown(
    """
    ℹ️ **Sentiment Categories**
    - **Positive**: Clear positive opinion  
    - **Positive Expressive**: Emotional praise using slang or emojis
    """,  
    help="Positive Expressive comments are detected using a hybrid NLP approach combining BERT predictions with social-media rules."
)
st.markdown(
    """
    - **Neutral**: Informational or unclear sentiment  
    - **Negative**: Clear criticism or dislike  
    """
    #help="Expressive Positive comments are detected using a hybrid NLP approach combining BERT predictions with social-media rules."
)

sentiment_counts = result_df["sentiment_adjusted"].value_counts().reset_index()
sentiment_counts.columns = ["sentiment", "count"]

fig = px.pie(
    sentiment_counts,
    names="sentiment",
    values="count",
    color="sentiment",
    color_discrete_map={
        "positive": "#21b75f",
        "positive-expressive": "#72b6f7",
        "neutral": "#879596",
        "negative": "#c63f30"
    },
    title="Sentiment Distribution",
    #hole=0.4  # donut style
)
fig.update_traces(
    pull=[0.02]* len(sentiment_counts),  # slight pop-out animation feel
    textinfo="percent+label"
)

fig.update_layout(
    width=650,   # increase size here
    height=650,
    legend_title="Sentiment",
    transition_duration=800   # animation smoothness
)

st.plotly_chart(fig, use_container_width=True)
st.divider()



    #cluster_counts = result_df["cluster"].value_counts()

    #fig, ax = plt.subplots()
    #ax.bar(cluster_counts.index, cluster_counts.values)
    #ax.set_xlabel("Cluster")
    #ax.set_ylabel("Number of Comments")
    #ax.set_title("Opinion Group Distribution")
    #st.pyplot(fig)
