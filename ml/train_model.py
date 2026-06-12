import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay
import joblib
import matplotlib.pyplot as plt

#  Load dataset
df = pd.read_csv("gesture_dataset.csv")

print("\n Dataset Preview:")
print(df.head())

# Features & Labels
X = df.drop("label", axis=1)
y = df["label"]

# \ Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

#  Train model
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42
)
model.fit(X_train, y_train)

#  Accuracy
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n Model Accuracy: {accuracy * 100:.2f}%")

# CONFUSION MATRIX

cm = confusion_matrix(y_test, y_pred)
labels = model.classes_

disp = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=labels
)

fig, ax = plt.subplots(figsize=(8, 6))

disp.plot(
    cmap='Blues',
    ax=ax,
    colorbar=True
)

plt.title("Sign Language Gesture Confusion Matrix")

plt.xlabel("Predicted Gesture")

plt.ylabel("Actual Gesture")

plt.xticks(rotation=15)

plt.tight_layout()

# Save image
plt.savefig("confusion_matrix.png")

# Show graph
plt.show()

#  Save model
joblib.dump(model, "gesture_model.pkl")

print(" Model saved as gesture_model.pkl")