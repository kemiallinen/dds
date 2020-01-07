import pandas as pd
import collections
from sklearn.cluster import KMeans
from pprint import pprint
from sklearn.feature_extraction.text import HashingVectorizer
import numpy as np


data = pd.read_csv('out.csv', sep=',')
formulas = data['formula'].sample(n=200, random_state=1)
vectorizer = HashingVectorizer(n_features=2**4,
                               ngram_range=(1, 3),
                               analyzer='char')
X = vectorizer.fit_transform(formulas)
km_model = KMeans(n_clusters=10)
km_model.fit(X)
clustering = collections.defaultdict(list)

formulas_np = formulas.to_numpy()

for idx, label in enumerate(km_model.labels_):
    clustering[label].append(formulas_np[idx])

pprint(dict(clustering))
