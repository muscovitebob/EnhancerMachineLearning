import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd
import joblib as jb
import seaborn as sns

feature_matrix_2 = pd.read_table("feature_matrix_2.csv", sep=",", index_col=0)

feature_matrix_2 = feature_matrix_2.fillna(value=0)

# What is in the feature matrix?
# log likelihood ratios for every genomic site and motif
# log[P(cluster sequence given that it's a cluster of real sites)/P(cluster sequence given that it's random DNA)]

# Let's visualise the distribution of the scores across all motifs and genomic sites

for i in range(1, len(feature_matrix_2.columns)):
    plot1 = sns.kdeplot(feature_matrix_2.iloc[:, i], legend=False)
    plot1.set(xlabel="log[P(cluster sequence | real cluster)/P(cluster sequence | random DNA)]")

plt.show()

# There are some outliers that scored more than 80. The distribution appears to be lognormal.
# Since the vectors are all the same length its permissible to take the average of averages to see a rough value.

averages_list = []
for i in range(1, len(feature_matrix_2.columns)):
    averages_list.append(np.average(feature_matrix_2.iloc[:, i]))

np.average(averages_list)

# This comes out about 1.384, so most values actually score around that much - ish.

