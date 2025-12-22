import pandas as pd
import numpy as np
import random
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

# --- AYARLAR ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_FILE = os.path.join(BASE_DIR, "thief_dataset.csv")
MODEL_FILE = os.path.join(BASE_DIR, "thief_detector_model.pkl")
MIN_SAMPLES = 10000  # Eğer veri seti bundan azsa, otomatik yeni veri üretilecek
TARGET_SAMPLES = 50000 # Yeni üretilecekse kaç satır olsun?

def generate_large_dataset():
    """Büyük ölçekli sahte veri seti üretir."""
    print(f"⚡ {TARGET_SAMPLES} satırlık devasa veri seti üretiliyor...")
    data = []

    # Daha gerçekçi: sınıflar arasında overlap (tam ayrışmayan) dağılımlar
    # Sıra: happy, sad, angry, surprise, fear, disgust, neutral
    alpha_normal = np.array([4.5, 2.2, 1.2, 1.8, 1.1, 0.9, 6.0], dtype=float)
    alpha_normal_anx = np.array([3.2, 2.3, 1.8, 2.0, 1.8, 1.2, 4.8], dtype=float)
    alpha_thief = np.array([1.6, 2.0, 3.2, 3.0, 3.0, 1.9, 2.0], dtype=float)
    alpha_thief_calm = np.array([2.6, 2.2, 2.0, 2.1, 2.0, 1.4, 3.6], dtype=float)

    def sample_emotions(label: int) -> dict:
        if int(label) == 1:
            alpha = alpha_thief if random.random() < 0.75 else alpha_thief_calm
        else:
            alpha = alpha_normal if random.random() < 0.80 else alpha_normal_anx

        probs = np.random.dirichlet(alpha)
        noise = np.random.normal(loc=0.0, scale=0.008, size=probs.shape)
        probs = np.clip(probs + noise, 1e-6, None)
        probs = probs / probs.sum()
        pct = probs * 100.0
        return {
            "happy": float(pct[0]),
            "sad": float(pct[1]),
            "angry": float(pct[2]),
            "surprise": float(pct[3]),
            "fear": float(pct[4]),
            "disgust": float(pct[5]),
            "neutral": float(pct[6]),
        }
    
    for _ in range(TARGET_SAMPLES):
        is_thief = random.choice([0, 1])
        row = sample_emotions(is_thief)
        row["label"] = int(is_thief)
        data.append(row)

    df = pd.DataFrame(data)
    df.to_csv(DATASET_FILE, index=False)
    print(f"✅ Yeni veri seti kaydedildi: {os.path.basename(DATASET_FILE)} ({len(df)} satır)")
    return df

def train_model():
    # 1. Veriyi Yükle veya Oluştur
    if not os.path.exists(DATASET_FILE):
        print("❌ Veri dosyası bulunamadı, oluşturuluyor...")
        df = generate_large_dataset()
    else:
        df = pd.read_csv(DATASET_FILE)
        if len(df) < MIN_SAMPLES:
            print(f"⚠️ Mevcut veri az ({len(df)} satır). Daha iyi sonuç için yeniden üretiliyor...")
            df = generate_large_dataset()
        else:
            print(f"📂 Mevcut veri seti yüklendi: {len(df)} satır.")

    # 2. Özellikler ve Etiket
    feature_columns = ["happy", "sad", "angry", "surprise", "fear", "disgust", "neutral"]
    X = df[feature_columns]
    y = df["label"]

    # 3. Bölme (stratify ile sınıf oranlarını koru)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.3,
        random_state=42,
        stratify=y,
    )

    # 4. Model Eğitimi (n_jobs=-1 ile tüm işlemci gücünü kullanır)
    print("⏳ Model eğitiliyor (Bu işlem veri boyutuna göre sürebilir)...")
    model = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=42)
    model.fit(X_train, y_train)

    # 5. Test ve Rapor
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print("-" * 30)
    print(f"🎯 Model Doğruluğu: %{accuracy * 100:.2f}")
    print("-" * 30)
    print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
    print("Detaylı Rapor:\n", classification_report(y_test, y_pred))
    
    # Özellik Önem Dereceleri (Hangi duygu hırsızı ele veriyor?)
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    print("\n🔍 Hırsız Tespitinde En Önemli Duygular:")
    for f in range(X.shape[1]):
        print(f"{f+1}. {feature_columns[indices[f]]}: %{importances[indices[f]]*100:.2f}")

    # 6. Kaydet
    joblib.dump(model, MODEL_FILE)
    print(f"\n✅ Model başarıyla kaydedildi: {os.path.basename(MODEL_FILE)}")

    # 7. Kaydedilen model dosyasını yükle ve tekrar ölç (model dosyası doğruluğu)
    loaded_model = joblib.load(MODEL_FILE)
    y_pred_loaded = loaded_model.predict(X_test)
    loaded_accuracy = accuracy_score(y_test, y_pred_loaded)
    print("-" * 30)
    print(f"📦 Model dosyası doğruluğu (test): %{loaded_accuracy * 100:.2f}")
    print("-" * 30)

if __name__ == "__main__":
    train_model()