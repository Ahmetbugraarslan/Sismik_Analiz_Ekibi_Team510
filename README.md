# Sismik Analiz Ekibi - Team510

Deprem verilerini analiz etmek, görselleştirmek ve raporlamak için geliştirilmiş Python tabanlı analiz sistemi.

## Kurulum

```bash
# Depoyu klonlayın
git clone https://github.com/Ahmetbugraarslan/Sismik_Analiz_Ekibi_Team510.git
cd Sismik_Analiz_Ekibi_Team510

# Sanal ortam oluşturun (önerilir)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

## Kullanım

### Komut Satırı

```bash
# Yardım
python main.py --help

# Örnek veri oluştur
python main.py sample --count 500 --output data/raw/sample.csv

# Veri analizi
python main.py analyze --file data/raw/sample.csv

# Görselleştirme
python main.py visualize --file data/raw/sample.csv --output output/

# Rapor oluştur
python main.py report --file data/raw/sample.csv --output rapor.txt
```

### Python API

```python
from src import DataLoader, SeismicAnalyzer, SeismicVisualizer

# Veri yükle
loader = DataLoader(data_path="data/raw")
data = loader.load_csv("earthquakes.csv")

# Analiz et
analyzer = SeismicAnalyzer(data)
stats = analyzer.basic_statistics()
categories = analyzer.categorize_by_magnitude()
b_value = analyzer.calculate_b_value()

# Görselleştir
visualizer = SeismicVisualizer(data, output_path="output")
visualizer.create_dashboard()
```

## Proje Yapısı

```
Sismik_Analiz_Ekibi_Team510/
├── main.py                 # Ana uygulama
├── requirements.txt        # Python bağımlılıkları
├── README.md              # Bu dosya
├── .gitignore             # Git ignore kuralları
├── src/                   # Kaynak kodlar
│   ├── __init__.py
│   ├── data_loader.py     # Veri yükleme modülü
│   ├── seismic_analyzer.py # Analiz modülü
│   ├── visualizer.py      # Görselleştirme modülü
│   └── utils.py           # Yardımcı fonksiyonlar
├── data/                  # Veri dosyaları
│   ├── raw/              # Ham veriler
│   └── processed/        # İşlenmiş veriler
├── models/               # Eğitilmiş modeller
├── notebooks/            # Jupyter notebook'ları
├── tests/                # Test dosyaları
├── docs/                 # Dokümantasyon
└── output/               # Çıktı dosyaları (grafikler, raporlar)
```

## Özellikler

### Veri Yükleme
- CSV, Excel ve JSON dosya desteği
- Otomatik sütun standartlaştırma
- Tarih/saat ayrıştırma
- Bölge ve büyüklük filtreleme

### Analiz
- Temel istatistikler (min, max, ortalama, medyan)
- Büyüklük kategorileri (mikro, küçük, orta, büyük)
- Derinlik analizi (sığ, orta, derin)
- Zamansal analiz (aylık, yıllık dağılım)
- Mekansal analiz (koordinat dağılımı)
- Gutenberg-Richter b-değeri hesabı
- Artçı deprem tespiti
- Risk değerlendirmesi

### Görselleştirme
- Büyüklük histogramı
- Derinlik histogramı
- Deprem haritası (scatter plot)
- Zaman serisi grafikleri
- Derinlik vs büyüklük ilişkisi
- Gutenberg-Richter grafiği
- Saatlik dağılım (polar grafik)
- Özet dashboard

### Yardımcı Fonksiyonlar
- Haversine mesafe hesabı
- Enerji hesabı
- TNT eşdeğeri
- MMI şiddet tahmini
- Fay kırılma uzunluğu tahmini
- Sismik moment hesabı

## Veri Formatı

Desteklenen sütunlar:

| Sütun | Alternatifler | Açıklama |
|-------|---------------|----------|
| tarih | date | Deprem tarihi |
| saat | time | Deprem saati |
| enlem | latitude, lat | Enlem (derece) |
| boylam | longitude, lon | Boylam (derece) |
| derinlik | depth | Odak derinliği (km) |
| buyukluk | magnitude, mag | Deprem büyüklüğü |

## Lisans

MIT License

## Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Commit yapın (`git commit -m 'Yeni özellik ekle'`)
4. Push yapın (`git push origin feature/yeni-ozellik`)
5. Pull Request oluşturun

## İletişim

Sismik Analiz Ekibi - Team510
