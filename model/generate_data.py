import pandas as pd
import numpy as np
import random

# Veri seti büyüklüğü
NUM_SAMPLES = 2000

def generate_synthetic_data():
    data = []
    
    for _ in range(NUM_SAMPLES):
        # %50 ihtimalle hırsız (1), %50 ihtimalle normal (0) durumu üret
        is_thief = random.choice([0, 1])
        
        if is_thief:
            # HIRSIZ PROFİLİ:
            # Genellikle: Yüksek Korku (yakalanma korkusu), Öfke veya Tiksinme.
            # Düşük: Mutluluk.
            fear = random.uniform(40, 100)
            angry = random.uniform(20, 90)
            disgust = random.uniform(10, 80)
            surprise = random.uniform(20, 80) # Ani tepkiler verebilir
            sad = random.uniform(0, 40)
            happy = random.uniform(0, 10)     # Hırsızken mutlu olması beklenmez
            neutral = random.uniform(0, 30)   # Duygularını gizlemeye çalışabilir ama düşük kalır
            
        else:
            # NORMAL İNSAN PROFİLİ:
            # Genellikle: Yüksek Nötr, Mutlu veya hafif Şaşkın/Üzgün.
            # Düşük: Korku, Öfke (aşırı durumlar hariç).
            fear = random.uniform(0, 20)
            angry = random.uniform(0, 20)
            disgust = random.uniform(0, 10)
            surprise = random.uniform(0, 40)
            sad = random.uniform(0, 60)
            happy = random.uniform(0, 100)
            neutral = random.uniform(40, 100)

        # Değerleri birleştirip normalize edelim (DeepFace toplamı genelde 100'dür)
        raw_emotions = np.array([happy, sad, angry, surprise, fear, disgust, neutral])
        normalized_emotions = (raw_emotions / raw_emotions.sum()) * 100
        
        row = {
            "happy": normalized_emotions[0],
            "sad": normalized_emotions[1],
            "angry": normalized_emotions[2],
            "surprise": normalized_emotions[3],
            "fear": normalized_emotions[4],
            "disgust": normalized_emotions[5],
            "neutral": normalized_emotions[6],
            "label": is_thief  # 1: Hırsız/Tehlikeli, 0: Güvenli
        }
        data.append(row)

    df = pd.DataFrame(data)
    
    # CSV olarak kaydet
    df.to_csv("thief_dataset.csv", index=False)
    print(f"✅ {NUM_SAMPLES} adet veri üretildi ve 'thief_dataset.csv' dosyasına kaydedildi.")
    print(df.head())

if __name__ == "__main__":
    generate_synthetic_data()