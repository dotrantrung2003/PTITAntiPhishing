import numpy as np

from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score

import joblib
import matplotlib.pyplot as plt

data_file = open('dataset/27_11_25k_TrainingDataset_shuf.arff').read()
data_list = data_file.split('\n')
data = np.array(data_list)
data_array = [i.split(',') for i in data]
data_array = data_array[0:-1]

labels = []
for i in data_array:
    labels.append(i[30])
data_array = np.array(data_array)

features = data_array[:, :-1]

# features = features[:, [0, 1, 2, 3, 4, 5, 6, 8, 9, 11, 12, 13, 14, 15, 16, 17, 22, 23, 24, 25, 27, 29]]
features = features[:, [0, 1, 2, 3, 4, 5, 6, 8, 9, 11, 12, 13, 14, 15, 16, 17, 22, 23, 24, 27, 29]]

features = np.array(features).astype(np.float64)
labels = np.array(labels).astype(np.float64)

features_train, features_test, labels_train, labels_test = train_test_split(
    features, labels,
    test_size=0.1,
    random_state=42,
    stratify=labels,
    shuffle=True
)

knn = KNeighborsClassifier(
    n_jobs=-1
)

param_grid = {
    'n_neighbors': [3, 5, 7, 9, 11],
    'weights': ['uniform', 'distance'],
}

grid_search = GridSearchCV(
    estimator=knn,
    param_grid=param_grid,
    cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=42),
    scoring='accuracy',
    n_jobs=-1,
    verbose=2
)

grid_search.fit(features_train, labels_train)

best_knn = grid_search.best_estimator_
print("\nBest Parameters:", grid_search.best_params_)
print("=" * 50)

predictions = best_knn.predict(features_test)

labels_test = [int(i) for i in labels_test]
predictions = [int(i) for i in predictions]

_accuracy_score = accuracy_score(np.array(labels_test), np.array(predictions))
_precision_score = precision_score(np.array(labels_test), np.array(predictions))
_recall_score = recall_score(np.array(labels_test), np.array(predictions))
_f1_score = f1_score(np.array(labels_test), np.array(predictions))
_confusion_matrix = confusion_matrix(np.array(labels_test), np.array(predictions))
_roc_auc_score = roc_auc_score(np.array(labels_test), np.array(predictions))

print("Accuracy:", _accuracy_score)
print("=" * 50)
print("Precision:", _precision_score)
print("=" * 50)
print("Recall:", _recall_score)
print("=" * 50)
print("F1 Score:", _f1_score)
print("=" * 50)
print("Confusion Matrix:\n", _confusion_matrix)
print("=" * 50)

# joblib.dump(best_knn, 'classifier/Final_KNN_Model.pkl')
