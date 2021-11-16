import logging
from flask import Flask, render_template, request
from elasticsearch import Elasticsearch

app = Flask(__name__)
es = Elasticsearch(host="localhost", port=9200)

logging.getLogger("werkzeug").disabled = True

INDEX = "covid"
SIMILIARITIES = {
    "boolean": {
        "type": "boolean",
        "k1": None,
        "b": None,
        "discount_overlaps": None,
        "mu": None,
    },
    "tfidf": {
        "type": "BM25",
        "k1": 1.2,
        "b": 0.75,
        "discount_overlaps": True,
        "mu": None,
    },
    "lm": {
        "type": "LMDirichlet",
        "k1": None,
        "b": None,
        "discount_overlaps": None,
        "mu": 2000,
    }
}


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    if request.method == "POST":
        keywords = request.form.get("keywords")
        query_logic = request.form.get("logic")

        print("User input:", keywords, query_logic, flush=True)

        keywords = keywords.replace(" ", " AND ")
        change_index_similarity(query_logic)

        query = {"query_string": {"query": keywords}}
        res = es.search(index=INDEX, query=query, size=25)
        articles = [d["_source"] for d in res["hits"]["hits"]]

        output_info = {
            "keywords": keywords,
            "query_logic": SIMILIARITIES.get(query_logic).get("type"),
            "count": len(articles)
        }

        return render_template("index.html", articles=articles, output_info=output_info)


def change_index_similarity(query_logic):
    es.indices.close(index=INDEX, wait_for_active_shards=0)
    settings = {"index": {"similarity": {"default": SIMILIARITIES.get(query_logic)}}}
    es.indices.put_settings(body=settings, index=INDEX)
    es.indices.open(index=INDEX)

    new_sim = es.indices.get(index=INDEX)[INDEX]["settings"]["index"]["similarity"]["default"]
    print("changed similarity type:", new_sim["type"], flush=True)


if __name__ == "__main__":
    app.run(debug=True)
