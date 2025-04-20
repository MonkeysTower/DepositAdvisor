from flask import Flask, render_template, request
from models import load_observations, scale_features
from knn import prepare_query, find_nearest_neighbors

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        amount = int(request.form["amount"])
        term = int(request.form["term"])
        replenishment = bool(request.form.get("replenishment"))
        withdrawal = bool(request.form.get("withdrawal"))

        observations = load_observations()

        features = ["Сумма вклада", "Срок вклада"]
        observations, scaler = scale_features(observations, features)

        query = {
            "Сумма вклада": amount,
            "Срок вклада": term,
            "Пополнение": replenishment,
            "Снятие": withdrawal
        }
        query_scaled = prepare_query(query, scaler, features)

        X = observations[["Сумма вклада", "Срок вклада", "Пополнение", "Снятие"]]
        y = observations["Лучший вклад"]
        query_features = [query_scaled[k] for k in X.columns]
        predicted_group, neighbors = find_nearest_neighbors(X, y, query_features, n_neighbors=3)

        return render_template("index.html", result=predicted_group)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)