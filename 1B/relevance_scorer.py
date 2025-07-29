# relevance_scorer.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def rank_sections(sections, persona, job):
    combined_query = persona + " " + job
    texts = [s["text"] for s in sections]
    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform([combined_query] + texts)
    sims = cosine_similarity(vectors[0:1], vectors[1:]).flatten()

    for i, score in enumerate(sims):
        sections[i]["score"] = float(score)

    ranked = sorted(sections, key=lambda x: x["score"], reverse=True)
    for i, sec in enumerate(ranked):
        sec["importance_rank"] = i + 1
    return ranked[:10]  # Return top 10 most relevant sections

