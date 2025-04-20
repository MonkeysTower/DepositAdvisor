from sklearn.neighbors import KNeighborsClassifier

def prepare_query(query, scaler, features):
    """
    Подготавливает и масштабирует параметры искомого наблюдения.
    """
    query["Пополнение"] = int(query["Пополнение"])
    query["Снятие"] = int(query["Снятие"])
    query_scaled = {k: v for k, v in query.items()}
    query_scaled.update(zip(features, scaler.transform([[query[k] for k in features]])[0]))
    return query_scaled

def find_nearest_neighbors(X, y, query_features, n_neighbors=3):
    """
    Находит ближайших соседей для искомого наблюдения.
    """
    knn = KNeighborsClassifier(n_neighbors=n_neighbors)
    knn.fit(X, y)
    predicted_group = knn.predict([query_features])[0]
    neighbors = knn.kneighbors([query_features], return_distance=False)
    return predicted_group, neighbors