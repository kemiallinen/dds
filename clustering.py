import pandas as pd
from leven import levenshtein
# import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import HashingVectorizer


def lev_metric(x, y):
    i, j = int(x[0]), int(y[0])
    return levenshtein(formulas[i], formulas[j])


data = pd.read_csv('out.csv', sep=',')
formulas = data['formula'][:100]
vectorizer = HashingVectorizer(n_features=2**4)
X = vectorizer.fit_transform(formulas)
clustering = DBSCAN(eps=5, min_samples=2).fit(X)
# X = np.arange(len(formulas)).reshape(-1, 1)
# dbscan(X, metric=lev_metric, eps=5, min_samples=2)
