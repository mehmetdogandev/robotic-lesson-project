import pandas as pd
import numpy as np
import random

# Veri seti büyüklüğü (Burayı istediğiniz kadar artırabilirsiniz)
NUM_SAMPLES = 50000 

def _sample_emotions_dirichlet(label: int) -> dict:
    """Daha gerçekçi duygu dağılımı üretir.

    Amaç: sınıflar arasında belirgin ama tam ayrışmayan (overlap'lı) veri.
    - Dirichlet dağılımı: 7 duygu için toplamı 1 olan olasılık vektörü üretir.
    - Karışım (mixture): Her sınıfta az da olsa diğer sınıfa benzeyen örnekler olur.
    """
    # Sıra: happy, sad, angry, surprise, fear, disgust, neutral
    # Normal (genelde neutral/happy daha yüksek)
    alpha_normal = np.array([4.5, 2.2, 1.2, 1.8, 1.1, 0.9, 6.0], dtype=float)
    # Normal ama gergin (fear/angry biraz daha yüksek)
    alpha_normal_anx = np.array([3.2, 2.3, 1.8, 2.0, 1.8, 1.2, 4.8], dtype=float)
    # Hırsız (genelde fear/angry/surprise daha yüksek, neutral daha düşük)
    alpha_thief = np.array([1.6, 2.0, 3.2, 3.0, 3.0, 1.9, 2.0], dtype=float)
    # Hırsız ama sakin/rahat (her zaman panik olmaz)
    alpha_thief_calm = np.array([2.6, 2.2, 2.0, 2.1, 2.0, 1.4, 3.6], dtype=float)

    # Mixture oranları (overlap için kritik)
    if int(label) == 1:
        # %75 tipik hırsız, %25 daha sakin
        alpha = alpha_thief if random.random() < 0.75 else alpha_thief_calm
    else:
        # %80 tipik normal, %20 daha gergin normal
        alpha = alpha_normal if random.random() < 0.80 else alpha_normal_anx

    probs = np.random.dirichlet(alpha)

    # Küçük ölçekte ölçüm gürültüsü simülasyonu (sonra re-normalize)
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

def generate_synthetic_data():
    data = []
    
    for _ in range(NUM_SAMPLES):
        is_thief = random.choice([0, 1])

        row = _sample_emotions_dirichlet(is_thief)
        row["label"] = int(is_thief)
        data.append(row)

    df = pd.DataFrame(data)
    df.to_csv("thief_dataset.csv", index=False)
    print(f"{NUM_SAMPLES} satırlık veri seti oluşturuldu: thief_dataset.csv")

if __name__ == "__main__":
    generate_synthetic_data()