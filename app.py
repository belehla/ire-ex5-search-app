from flask import Flask, render_template, request
from elasticsearch import Elasticsearch

app = Flask(__name__)
es = Elasticsearch()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    if request.method == "POST":
        res = es.search(index="cnn", query={"match_all": {}})
        articles = [d["_source"] for d in res["hits"]["hits"]]

        print(request.form.get("keywords"), flush=True)
        print(request.form.get("type"), flush=True)
        return render_template("index.html", articles=articles)


if __name__ == "__main__":
    app.run(debug=True)
