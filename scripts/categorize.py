import joblib

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pprint import pprint

from sklearn.cluster import MiniBatchKMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import roc_auc_score as auc
from sklearn.model_selection import StratifiedKFold

from mlgear.cv import run_cv_model
from mlgear.models import runLR

from utils.download import file_name_from_url, read_cache
from utils.embed import embed, clean


# Adapted from https://www.kaggle.com/jbencina/clustering-documents-with-tfidf-and-kmeans
def find_optimal_clusters(data, max_k):
    iters = range(2, max_k+1, 2)
    
    sse = []
    for k in iters:
        sse.append(MiniBatchKMeans(n_clusters=k, init_size=1024, batch_size=2048, random_state=20).fit(data).inertia_)
        print('Fit {} clusters'.format(k))
        
    f, ax = plt.subplots(1, 1)
    ax.plot(iters, sse, marker='o')
    ax.set_xlabel('Cluster Centers')
    ax.set_xticks(iters)
    ax.set_xticklabels(iters)
    ax.set_ylabel('SSE')
    ax.set_title('SSE by Cluster Center Plot')
    return plt, sse


# Adapted from https://www.kaggle.com/jbencina/clustering-documents-with-tfidf-and-kmeans
def plot_tsne_pca(data, labels):
    print('PCA...')
    pca = PCA(n_components=2).fit_transform(data.todense())
    print('TSNE...')
    tsne = TSNE().fit_transform(data.todense())
    print('Plots...')
    f, ax = plt.subplots(1, 2, figsize=(14, 6))
    ax[0].scatter(pca[:, 0], pca[:, 1], c=labels)
    ax[0].set_title('PCA Cluster Plot')
    ax[1].scatter(tsne[:, 0], tsne[:, 1], c=labels)
    ax[1].set_title('TSNE Cluster Plot')
    return plt, pca, tsne


def cluster_counts(clusters):
    unique, counts = np.unique(clusters, return_counts=True)
    cc = dict(zip(unique, counts))
    return dict(sorted([(k, v) for k, v in cc.items()], key=lambda x: x[1], reverse=True))


# Adapted from https://www.kaggle.com/jbencina/clustering-documents-with-tfidf-and-kmeans
def get_top_keywords(data, clusters, cluster_counts, labels, n_terms):
    df = pd.DataFrame(data.todense()).groupby(clusters).mean()
    for i,r in df.iterrows():
        print('\nCluster {} - Size {}'.format(i, cluster_counts[i]))
        print(', '.join([labels[t] for t in np.argsort(r)[-n_terms:]]))
            

print('Loading...')
original_links = pd.read_csv('data/links.csv')
links = original_links[original_links['liked'] == 1]

links['text'] = links['url'].apply(file_name_from_url).apply(read_cache).fillna('').apply(clean)

print('Load GloVe...')
embeddings_dict = joblib.load('data/glove.pkl')
text = links['text'].values.tolist()

print('Embed...')
embeddings_text = [embed(t, embeddings_dict=embeddings_dict) for t in text]

print('TFIDF Fit...')
tfidf = TfidfVectorizer(
    min_df=4,
    max_df=0.8,
    max_features=2000,
    stop_words='english'
)
tfidf.fit(text)
print('TFIDF Predict...')
tfidf_text = tfidf.transform(text)
print('TFIDF Merge...')
blank = np.zeros(300)
embeddings_text = [blank if e.shape == () else e for e in embeddings_text]
embeddings_text = np.concatenate((np.array(embeddings_text), tfidf_text.todense()), axis=1)

embeddings_df = pd.DataFrame(embeddings_text)
embeddings_df['cluster'] = links['cluster']

targets = [t for t in embeddings_df['cluster'].unique() if t != '-1']
train = embeddings_df[links['cluster'] != '-1']
results = {}


print('Training categorization models...')
for target in targets:
    target_ = (train['cluster'] == target).astype(int)
    if target_.value_counts().min() > 10:
        print(target)
        folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        folds = folds.split(train.drop('cluster', axis=1).values, target_)
        results[target] = run_cv_model(train=train.drop('cluster', axis=1).values,
                                       target=target_.values,
                                       model_fn=runLR,
                                       params={'C': 20.0},
                                       eval_fn=auc,
                                       fold_splits=folds,
                                       n_folds=5)

print('Per-Model CVs')
pprint(sorted([(k, v['final_cv']) for k, v in results.items()],
              key=lambda x: x[1], reverse=True))

print('Overall CV: {}'.format(np.mean([v['final_cv'] for k, v in results.items()])))
# 0.9094

print('Predicting...')
values_to_cat = embeddings_df.drop(['cluster'], axis=1).values.tolist()
values_to_cat = [sorted([(k, np.mean([m.predict_proba([v])[0][1]
                         for m in results[k]['model'].values()]))
                         for k in results.keys()], key=lambda x: x[1], reverse=True)[0][0]
                         for v in values_to_cat]
embeddings_df['predicted'] = values_to_cat

# edf = embeddings_df[c for c in embeddings_df.columns if c not in ['cluster', 'predicted']]
# plt, sse = find_optimal_clusters(edf.values, 50)
# plt.show()

# print('Training clusters...')
# clusters = MiniBatchKMeans(n_clusters=60,
#                            init_size=1024,
#                            batch_size=2048,
#                            random_state=20).fit_predict(embeddings_text)

# plt, tsne, pca = plot_tsne_pca(tfidf_text, clusters)
# plt.show()

get_top_keywords(tfidf_text,
                 embeddings_df['predicted'],
                 cluster_counts(embeddings_df['predicted']),
                 tfidf.get_feature_names(),
                 10)

print('Saving models...')
models = dict([(k, [m for m in results[k]['model'].values()]) for k in results.keys()])
joblib.dump(models, 'data/models.pkl')
joblib.dump(tfidf, 'data/tfidf.pkl')

print('Merging...')
links.loc[:, 'cluster'] = embeddings_df['cluster']
original_links = pd.merge(original_links, links[['url', 'cluster']], how='inner')
print('De-dupe...')
original_links = original_links.drop_duplicates('url')
print('Save...')
original_links.to_csv('data/links.csv', index=False)
print('Done!')
