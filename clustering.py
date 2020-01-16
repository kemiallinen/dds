import pandas as pd
import collections
from sklearn.cluster import KMeans, SpectralClustering, AgglomerativeClustering
from pprint import pprint
from sklearn.feature_extraction.text import HashingVectorizer


data = pd.read_csv('out.csv', sep=',')
formulas = data['formula'].sample(n=100, random_state=1)
vectorizer = HashingVectorizer(n_features=2**4,
                               ngram_range=(1, 3),
                               analyzer='char')
X = vectorizer.fit_transform(formulas)
# km_model = KMeans(n_clusters=7).fit(X)
# sc_model = SpectralClustering(n_clusters=7).fit(X)
ac_model = AgglomerativeClustering(n_clusters=7).fit(X.toarray())

clustering = collections.defaultdict(list)

formulas_np = formulas.to_numpy()
model = ac_model

for idx, label in enumerate(model.labels_):
    clustering[label].append(formulas_np[idx])

pprint(dict(clustering))
