import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

def train_model():
    # 1. Veriyi Yükle
    try:
        df = pd.read_csv("thief_dataset.csv")
    except FileNotFoundError:
        print("❌ Hata: 'thief_dataset.csv' bulunamadı. Önce veri üretme kodunu çalıştırın.")
        return

    # 2. Özellikler (X) ve Etiket (y) ayırımı
    # Özellik sırası çok önemlidir, DeepFace'den gelen sırayla aynı olmalı
    feature_columns = ["happy", "sad", "angry", "surprise", "fear", "disgust", "neutral"]
    X = df[feature_columns]
    y = df["label"]

    # 3. Eğitim ve Test setlerine böl (%80 Eğitim, %20 Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. Modeli Oluştur ve Eğit (Random Forest genellikle bu işler için iyidir)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    print("⏳ Model eğitiliyor...")
    model.fit(X_train, y_train)

    # 5. Test et
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"🎯 Model Doğruluğu: %{accuracy * 100:.2f}")
    print("\nDetaylı Rapor:\n", classification_report(y_test, y_pred))

    # 6. Modeli Kaydet
    model_filename = "thief_detector_model.pkl"
    joblib.dump(model, model_filename)
    print(f"✅ Model başarıyla kaydedildi: {model_filename}")

if __name__ == "__main__":
    train_model()