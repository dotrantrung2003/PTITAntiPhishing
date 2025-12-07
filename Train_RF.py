import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score
from sklearn.inspection import permutation_importance

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

rf = RandomForestClassifier(
    verbose=2,
    oob_score=True,
    random_state=42,
    n_jobs=-1,

    n_estimators=100,
    max_depth=20,
    min_samples_split=2,
    min_samples_leaf=1,
)

rf.fit(features_train, labels_train)
# rf = joblib.load('classifier/27_11_25k_RF_Model_shuf.pkl')
predictions = rf.predict(features_test)

joblib.dump(rf, 'classifier/27_11_25k_RF_Model.pkl')
print("Done")

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



importance = rf.feature_importances_
std = np.std([tree.feature_importances_ for tree in rf.estimators_], axis=0)
print("Feature importances:", importance)
print("=" * 50)
indices = np.argsort(importance)[::-1]
print("Feature ranking:", indices + 1)
print("=" * 50)

features_plot = ['Has IP instead of domain', 'Long Url', 'Url shortening service', 'Has @ symbol', 'Has "//" in Url',
                 'Has "-" in Url','Has multiple subdomains', 'Domain registration length', 'Has favicon',
                 'Has HTTP||HTTPS in domain', 'Has too many request Urls',
                 'Has too many anchor Urls', 'Has too many links to other domains',
                 'Has forms that are blank or linked to other domains',
                 'Submits information to email', 'Host name not included in Url',
                 'Uses iFrame', 'Age of domain','Has DNS records',
                 'Is in Google Index','PhishTank & StopBadware statistical report']

indices_list = indices.tolist()
for label in range(len(indices_list)):
    indices_list[label] = features_plot[indices_list[label]]
print("Feature ranking with labels:", indices_list)
print("=" * 50)

fig, ax = plt.subplots()
ax.set_title("")
# Vẽ cột
bars = ax.bar(
    range(features_train.shape[1]),
    importance[indices],
    color='red',
    align='center',
    label='Khả năng giảm độ nhiễu'
)
# Vẽ sai số (độ lệch chuẩn)
ax.errorbar(
    range(features_train.shape[1]),
    importance[indices],
    yerr=std[indices],
    fmt='none',
    ecolor='black',
    elinewidth=1.5,
    capsize=3,
    label='Độ lệch chuẩn'
)
ax.set_xlabel("Đặc trưng")
ax.set_ylabel("Giá trị độ quan trọng")
ax.set_xticks(range(features_train.shape[1]))
ax.set_xticklabels(indices + 1)
ax.set_xlim([-1, features_train.shape[1]])
ax.grid(axis='y', linestyle='--', alpha=0.5)
ax.legend()
plt.tight_layout()
plt.show()


result = permutation_importance(rf, features_test, labels_test, n_repeats=10,
                                random_state=42, n_jobs=2)
print("---------------------------here1----------------------------------------")
print(result.importances_mean)
print("-------------------------------------------------------------------")


sorted_idx = result.importances_mean.argsort()[::-1]
print(sorted_idx + 1)
print("---------------------------here2----------------------------------------")
print(result.importances[sorted_idx].T)
print("-------------------------------------------------------------------")

fig, ax = plt.subplots()  # <── tạo figure và axes
ax.set_title("")
# Vẽ cột
bars = ax.bar(
    range(features_test.shape[1]),
    result.importances_mean[sorted_idx],
    color='orange',
    align='center',
    label='Mức giảm hiệu năng'
)

# Vẽ sai số (độ lệch chuẩn)
ax.errorbar(
    range(features_test.shape[1]),
    result.importances_mean[sorted_idx],
    yerr=result.importances_std[sorted_idx],
    fmt='none',
    ecolor='black',
    elinewidth=1.5,
    capsize=3,
    label='Độ lệch chuẩn'
)

# Gán nhãn đặc trưng
ax.set_xlabel("Đặc trưng")
ax.set_ylabel("Giá trị độ quan trọng")
ax.set_xticks(range(features_train.shape[1]))
ax.set_xticklabels(sorted_idx + 1)
ax.set_xlim([-1, features_test.shape[1]])
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()

imp_impurity = rf.feature_importances_
imp_perm_mean = result.importances_mean

x = np.arange(len(features_plot))  # vị trí trục X
width = 0.35  # độ rộng cột

fig, ax = plt.subplots()

# Vẽ độ quan trọng theo độ nhiễu (Impurity)
bars1 = ax.bar(
    x - width/2,
    imp_impurity,
    width,
    label='Giảm độ nhiễu',
    color='red'
)

# Vẽ độ quan trọng theo mức giảm hiệu năng (Permutation)
bars2 = ax.bar(
    x + width/2,
    imp_perm_mean,
    width,
    label='Giảm hiệu năng',
    color='orange',
)

# Tùy chỉnh hiển thị
ax.set_title("")
ax.set_xlabel("Đặc trưng")
ax.set_ylabel("Giá trị độ quan trọng")
ax.set_xticks(x)
ax.set_xticklabels(np.arange(1, len(features_plot) + 1))
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=1.0)

plt.tight_layout()
plt.show()

import shap

explainer = shap.TreeExplainer(rf)

shap_values = explainer.shap_values(features_test)
print("SHAP shape:", shap_values.shape)

# shap_values_phishing = shap_values[:, :, 0]
# print("Phishing SHAP shape:", shap_values_phishing.shape)
shap_values_legitimate = shap_values[:, :, 1]
print("Legitimate SHAP shape:", shap_values_legitimate.shape)

# shap.summary_plot(
#   shap_values_phishing,
#   features_test,
#   feature_names= [f'Feature {i+1}' for i in range(len(features_plot))]
#    )

shap.summary_plot(
    shap_values_legitimate, 
    features_test, 
    feature_names= [f'Feature {i+1}' for i in range(len(features_plot))]
    )

shap_interaction_values = explainer.shap_interaction_values(features_test)
print('Interaction SHAP shape:', shap_interaction_values.shape)

shap_interaction_values_phishing = shap_interaction_values[:, :, 0]
print(shap_interaction_values_phishing.shape)
# shap_interaction_values_legitmate = shap_interaction_values[:, :, 1]
# print(shap_interaction_values_legitmate.shape)

shap.summary_plot(
    shap_interaction_values_phishing, 
    features_test, 
    feature_names= [f'Feature {i+1}' for i in range(len(features_plot))]
    )

# shap.summary_plot(
#     shap_interaction_values_legitmate, 
#     features_test, 
#     feature_names= [f'Feature {i+1}' for i in range(len(features_plot))]
#     )

