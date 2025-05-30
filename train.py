# train.py
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import joblib
import os

# Dataset esperado: texto_extraido,tipo_nota
csv_path = "dataset/treino_notas.csv"
df = pd.read_csv(csv_path)

X_raw = df["texto_extraido"].fillna("").values
y_raw = df["tipo_nota"].values

# Codificação das classes
classes = sorted(list(set(y_raw)))
label2idx = {label: idx for idx, label in enumerate(classes)}
y = torch.tensor([label2idx[label] for label in y_raw], dtype=torch.long)

# Vetorização
vectorizer = TfidfVectorizer(max_features=2000)
X_vec = vectorizer.fit_transform(X_raw)
X_tensor = torch.tensor(X_vec.toarray(), dtype=torch.float32)

# Split
X_train, X_val, y_train, y_val = train_test_split(X_tensor, y, test_size=0.2, random_state=42)

# Modelo
class NotaClassifier(nn.Module):
    def __init__(self, input_dim, num_classes):
        super().__init__()
        self.fc = nn.Linear(input_dim, num_classes)

    def forward(self, x):
        return self.fc(x)

model = NotaClassifier(X_tensor.shape[1], len(classes))
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

# Treinamento
for epoch in range(10):
    model.train()
    optimizer.zero_grad()
    outputs = model(X_train)
    loss = criterion(outputs, y_train)
    loss.backward()
    optimizer.step()
    print(f"Epoch {epoch+1}, Loss: {loss.item():.4f}")

# Avaliação
model.eval()
with torch.no_grad():
    val_preds = torch.argmax(model(X_val), dim=1)
    acc = (val_preds == y_val).float().mean()
    print(f"Acurácia de validação: {acc:.4f}")

# Salvar modelo e vetorizador
os.makedirs("modelos", exist_ok=True)
torch.save(model.state_dict(), "modelos/model.pth")
joblib.dump(vectorizer, "modelos/vectorizer.joblib")

# Salvar índice das classes
with open("modelos/classes.txt", "w") as f:
    for label in classes:
        f.write(f"{label}\n")
