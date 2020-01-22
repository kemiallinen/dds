import pandas as pd
# import collections
from sklearn.cluster import KMeans, SpectralClustering, AgglomerativeClustering
# from pprint import pprint
from sklearn.feature_extraction.text import HashingVectorizer
from scipy.sparse import csr_matrix, hstack


def format_data(df):
    df['formula'] = df['formula'].str.replace(' -> ', '.')
    df['formula'] = df['formula'].str.replace('p1', 'p')
    df['formula'] = df['formula'].str.replace('p2', 'q')
    df['formula'] = df['formula'].str.replace('p3', 'r')
    df['formula'] = df['formula'].str.replace('p4', 's')


transform, dp_included = True, True
cl_methods = ['k-means', 'sc', 'ac']
ds = {True: '_dp', False: '_no-dp'}
ts = {True: '_transformed', False: '_no-transform'}
n_features = 2**11

data = pd.read_csv('out.csv', sep=',').drop(['A(t)', 'B(t)', 'C(t)', 'D(t)'], axis=1)

if transform:
    format_data(data)
    n_features = 2**10

formulas = data['formula'].sample(n=100, random_state=1)
vectorizer = HashingVectorizer(n_features=n_features,
                               ngram_range=(1, 3),
                               analyzer='char')
X = vectorizer.fit_transform(formulas)
if dp_included:
    dps = data.iloc[formulas.index].copy().drop('formula', axis=1)
    X = hstack([X, csr_matrix(dps)])

for method in cl_methods:
    fname = 'out_xls\\' + method + ts[transform] + ds[dp_included] + '.xls'
    with pd.ExcelWriter(fname) as writer:
        nc = [2, 3, 5, 7, 10]
        for n_clusters in nc:
            if method == 'k-means':
                model = KMeans(n_clusters=n_clusters).fit(X)
            elif method == 'sc':
                model = SpectralClustering(n_clusters=n_clusters).fit(X)
            else:
                model = AgglomerativeClustering(n_clusters=n_clusters).fit(X.toarray())
            data_to_export = data.iloc[formulas.index].copy()
            data_to_export.loc[:, 'cluster'] = model.labels_
            data_to_export = data_to_export.sort_values(['cluster'])
            data_to_export.to_excel(writer, sheet_name='k={}'.format(n_clusters))

# if verbosity:
#     clustering = collections.defaultdict(list)
#
#     formulas_np = formulas.to_numpy()
#
#     for idx, label in enumerate(model.labels_):
#         clustering[label].append(formulas_np[idx])
#
#     pprint(dict(clustering))
