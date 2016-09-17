
# coding: utf-8

# In[ ]:

from __future__ import division

from scipy import linalg
import networkx as nx
import pandas as pd
import numpy as np


# In[ ]:

from matplotlib import pyplot as plt
import seaborn as sns
get_ipython().magic(u'matplotlib inline')


# In[ ]:

import matplotlib as mpl
mpl.rc('savefig', dpi=300)
mpl.rc('text', usetex=True)


# Load a `pandas.DataFrame` of interaction logs that contains the following columns: `user_id`, `module_id`, and `timestamp`

# In[ ]:

df = pd.read_csv('history.csv')


# Gauge the size of the transition graph

# In[ ]:

idx_of_module_id = {k: i for i, k in enumerate(df['module_id'].unique())}
num_modules = len(idx_of_module_id)


# In[ ]:

num_modules


# Should we ignore a student's multiple attempts at the same assessment or lesson?

# In[ ]:

IGNORE_REPEATED_MODULE_IDS = False


# Construct a *transition graph*, where nodes are content modules and directed edge weights represent the number of times any student has transitioned directly from the source node to the target node during their interaction history

# In[ ]:

X = np.zeros((num_modules, num_modules))
for _, ixns in df.sort_values(by='timestamp').groupby('user_id')['module_id']:
    module_idxes = ixns.map(idx_of_module_id).values
    
    if IGNORE_REPEATED_MODULE_IDS:
        filtered_module_idxes = []
        module_idxes_seen = set()
        for module_idx in module_idxes:
            if module_idx in module_idxes_seen:
                continue
            filtered_module_idxes.append(module_idx)
            module_idxes_seen.add(module_idx)
        
        X[filtered_module_idxes[:-1], filtered_module_idxes[1:]] += 1
    else:
        for i, j in zip(module_idxes[:-1], module_idxes[1:]):
            X[i, j] += 1


# In[ ]:

G = nx.from_numpy_matrix(X, create_using=nx.DiGraph())


# Assume that student paths are Markovian (i.e., that the transition graph describes a Markov chain). We will use the expression derived on page 5 in [these notes](http://math.ubbcluj.ro/~tradu/TI/coverch4_article.pdf) to compute the entropy of the Markov chain. Entropy is a function of the stationary distribution of the Markov chain, so we need to make sure that exists. 
# 
# First, we check if the Markov chain is irreducible (i.e., that the transition graph is strongly connected). It's unclear how to proceed if there are multiple components — perhaps take a weighted average of the entropy of each component, use pseudocounts to smooth the transition matrix, or simply ignore all but the largest component? 

# In[ ]:

assert len(list(nx.strongly_connected_components(G))) == 1


# Estimate the stationary distribution of the Markov chain by raising the transition probability matrix to a large power (simple, but inefficient)

# In[ ]:

P = X / X.sum(axis=1)[:, np.newaxis]


# In[ ]:

prev = P
diffs = []


# In[ ]:

for _ in xrange(15):
    Pn = np.dot(prev, prev) # exponentiation by squaring
    diffs.append(np.linalg.norm(Pn - prev))
    prev = Pn


# In[ ]:

stationary_distrn = Pn[:, 0]


# Check if the matrix is converging (the Frobenius norm of the differences should be getting smaller)

# In[ ]:

plt.plot(2**np.arange(0, len(diffs), 1), diffs, '-s')
plt.xlabel(r'$n$')
plt.ylabel(r'$\|P^{n+1} - P^n\|_F$')
plt.xscale('log')
plt.yscale('log')
plt.show()


# In[ ]:

mc_entropy = -np.dot(stationary_distrn, np.nansum(P*np.log(P), axis=1))


# In[ ]:

mc_entropy


# In[ ]:



