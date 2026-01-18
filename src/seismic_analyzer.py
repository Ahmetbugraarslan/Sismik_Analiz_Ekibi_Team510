"""
Sismik Analiz Modülü - Deprem verilerini analiz eder
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from scipy import stats
from collections import defaultdict


class SeismicAnalyzer:
    """Sismik veri analiz sınıfı"""

    # Büyüklük kategorileri
    MAGNITUDE_CATEGORIES = {
        'mikro': (0, 2.0),
        'cok_kucuk': (2.0, 3.0),
        'kucuk': (3.0, 4.0),
        'hafif': (4.0, 5.0),
        'orta': (5.0, 6.0),
        'guclu': (6.0, 7.0),
        'buyuk': (7.0, 8.0),
        'cok_buyuk': (8.0, 10.0)
    }

    def __init__(self, data: Optional[pd.DataFrame] = None):
        """
        SeismicAnalyzer başlatıcı

        Args:
            data: Analiz edilecek deprem verisi DataFrame'i
        """
        self._data = data
        self._analysis_results: Dict[str, Any] = {}

    @property
    def data(self) -> Optional[pd.DataFrame]:
        return self._data

    @data.setter
    def data(self, value: pd.DataFrame) -> None:
        self._data = value
        self._analysis_results = {}

    def set_data(self, data: pd.DataFrame) -> None:
        """Veri setini ayarla"""
        self._data = data
        self._analysis_results = {}

    def basic_statistics(self) -> Dict[str, Any]:
        """Temel istatistikleri hesapla"""
        if self._data is None:
            raise ValueError("Veri seti yüklenmemiş")

        stats_result = {
            'toplam_deprem': len(self._data),
            'sutunlar': list(self._data.columns)
        }

        numeric_cols = self._data.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            stats_result[f'{col}_istatistik'] = {
                'min': float(self._data[col].min()),
                'max': float(self._data[col].max()),
                'ortalama': float(self._data[col].mean()),
                'medyan': float(self._data[col].median()),
                'std': float(self._data[col].std())
            }

        self._analysis_results['basic_stats'] = stats_result
        return stats_result

    def categorize_by_magnitude(self) -> Dict[str, int]:
        """Büyüklüğe göre kategorize et"""
        if self._data is None or 'buyukluk' not in self._data.columns:
            raise ValueError("Geçerli büyüklük verisi yok")

        categories = {}
        for name, (min_mag, max_mag) in self.MAGNITUDE_CATEGORIES.items():
            count = len(self._data[
                (self._data['buyukluk'] >= min_mag) &
                (self._data['buyukluk'] < max_mag)
            ])
            categories[name] = count

        self._analysis_results['magnitude_categories'] = categories
        return categories

    def depth_analysis(self) -> Dict[str, Any]:
        """Derinlik analizi yap"""
        if self._data is None or 'derinlik' not in self._data.columns:
            raise ValueError("Geçerli derinlik verisi yok")

        depths = self._data['derinlik']

        analysis = {
            'sig': int((depths <= 70).sum()),  # Sığ depremler
            'orta': int(((depths > 70) & (depths <= 300)).sum()),  # Orta derinlik
            'derin': int((depths > 300).sum()),  # Derin depremler
            'ortalama_derinlik': float(depths.mean()),
            'max_derinlik': float(depths.max()),
            'min_derinlik': float(depths.min())
        }

        self._analysis_results['depth_analysis'] = analysis
        return analysis

    def temporal_analysis(self) -> Dict[str, Any]:
        """Zamansal analiz yap"""
        if self._data is None:
            raise ValueError("Veri seti yüklenmemiş")

        date_col = None
        for col in ['datetime', 'tarih']:
            if col in self._data.columns:
                date_col = col
                break

        if date_col is None:
            raise ValueError("Tarih sütunu bulunamadı")

        df = self._data.copy()
        df[date_col] = pd.to_datetime(df[date_col])

        analysis = {
            'ilk_deprem': str(df[date_col].min()),
            'son_deprem': str(df[date_col].max()),
            'toplam_gun': (df[date_col].max() - df[date_col].min()).days
        }

        # Aylık dağılım
        df['ay'] = df[date_col].dt.month
        monthly = df.groupby('ay').size().to_dict()
        analysis['aylik_dagilim'] = monthly

        # Yıllık dağılım
        df['yil'] = df[date_col].dt.year
        yearly = df.groupby('yil').size().to_dict()
        analysis['yillik_dagilim'] = {str(k): v for k, v in yearly.items()}

        # Günlük ortalama
        if analysis['toplam_gun'] > 0:
            analysis['gunluk_ortalama'] = round(len(df) / analysis['toplam_gun'], 2)

        self._analysis_results['temporal_analysis'] = analysis
        return analysis

    def spatial_analysis(self) -> Dict[str, Any]:
        """Mekansal analiz yap"""
        if self._data is None:
            raise ValueError("Veri seti yüklenmemiş")

        if 'enlem' not in self._data.columns or 'boylam' not in self._data.columns:
            raise ValueError("Koordinat sütunları bulunamadı")

        analysis = {
            'enlem_aralik': {
                'min': float(self._data['enlem'].min()),
                'max': float(self._data['enlem'].max())
            },
            'boylam_aralik': {
                'min': float(self._data['boylam'].min()),
                'max': float(self._data['boylam'].max())
            },
            'merkez': {
                'enlem': float(self._data['enlem'].mean()),
                'boylam': float(self._data['boylam'].mean())
            }
        }

        # Yoğunluk merkezi (büyüklükle ağırlıklı)
        if 'buyukluk' in self._data.columns:
            weights = self._data['buyukluk']
            analysis['agirlikli_merkez'] = {
                'enlem': float(np.average(self._data['enlem'], weights=weights)),
                'boylam': float(np.average(self._data['boylam'], weights=weights))
            }

        self._analysis_results['spatial_analysis'] = analysis
        return analysis

    def find_clusters(self, eps_km: float = 50, min_samples: int = 5) -> Dict[str, Any]:
        """Deprem kümelerini bul (basit mesafe tabanlı)"""
        if self._data is None:
            raise ValueError("Veri seti yüklenmemiş")

        if 'enlem' not in self._data.columns or 'boylam' not in self._data.columns:
            raise ValueError("Koordinat sütunları bulunamadı")

        # Basit grid tabanlı kümeleme
        lat_bins = np.arange(
            self._data['enlem'].min(),
            self._data['enlem'].max() + 0.5,
            0.5
        )
        lon_bins = np.arange(
            self._data['boylam'].min(),
            self._data['boylam'].max() + 0.5,
            0.5
        )

        df = self._data.copy()
        df['lat_bin'] = pd.cut(df['enlem'], bins=lat_bins, labels=False)
        df['lon_bin'] = pd.cut(df['boylam'], bins=lon_bins, labels=False)

        clusters = df.groupby(['lat_bin', 'lon_bin']).agg({
            'enlem': 'mean',
            'boylam': 'mean',
            'buyukluk': ['count', 'max', 'mean'] if 'buyukluk' in df.columns else 'count'
        }).reset_index()

        # En yoğun bölgeleri bul
        if 'buyukluk' in df.columns:
            clusters.columns = ['lat_bin', 'lon_bin', 'enlem', 'boylam', 'deprem_sayisi', 'max_buyukluk', 'ort_buyukluk']
            top_clusters = clusters.nlargest(10, 'deprem_sayisi')
        else:
            clusters.columns = ['lat_bin', 'lon_bin', 'enlem', 'boylam', 'deprem_sayisi']
            top_clusters = clusters.nlargest(10, 'deprem_sayisi')

        result = {
            'toplam_bolge': len(clusters),
            'en_yogun_bolgeler': top_clusters.to_dict('records')
        }

        self._analysis_results['clusters'] = result
        return result

    def detect_aftershocks(self, main_shock_threshold: float = 5.0,
                           time_window_days: int = 30,
                           distance_km: float = 100) -> List[Dict[str, Any]]:
        """Artçı depremleri tespit et"""
        if self._data is None:
            raise ValueError("Veri seti yüklenmemiş")

        if 'buyukluk' not in self._data.columns:
            raise ValueError("Büyüklük sütunu bulunamadı")

        date_col = 'datetime' if 'datetime' in self._data.columns else 'tarih'
        if date_col not in self._data.columns:
            raise ValueError("Tarih sütunu bulunamadı")

        df = self._data.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col)

        # Ana şokları bul
        main_shocks = df[df['buyukluk'] >= main_shock_threshold]

        aftershock_sequences = []

        for idx, main_shock in main_shocks.iterrows():
            end_time = main_shock[date_col] + timedelta(days=time_window_days)

            # Zaman penceresi içindeki depremler
            mask = (
                (df[date_col] > main_shock[date_col]) &
                (df[date_col] <= end_time) &
                (df['buyukluk'] < main_shock['buyukluk'])
            )

            aftershocks = df[mask]

            if len(aftershocks) > 0:
                sequence = {
                    'ana_sok': {
                        'tarih': str(main_shock[date_col]),
                        'buyukluk': float(main_shock['buyukluk']),
                        'enlem': float(main_shock['enlem']) if 'enlem' in main_shock else None,
                        'boylam': float(main_shock['boylam']) if 'boylam' in main_shock else None
                    },
                    'artci_sayisi': len(aftershocks),
                    'max_artci_buyukluk': float(aftershocks['buyukluk'].max()),
                    'ort_artci_buyukluk': float(aftershocks['buyukluk'].mean())
                }
                aftershock_sequences.append(sequence)

        self._analysis_results['aftershocks'] = aftershock_sequences
        return aftershock_sequences

    def calculate_b_value(self) -> Dict[str, float]:
        """Gutenberg-Richter b değerini hesapla"""
        if self._data is None or 'buyukluk' not in self._data.columns:
            raise ValueError("Geçerli büyüklük verisi yok")

        magnitudes = self._data['buyukluk'].dropna()

        if len(magnitudes) < 10:
            raise ValueError("b-değeri hesabı için yeterli veri yok (min 10 deprem)")

        # Minimum büyüklük (tamamlılık büyüklüğü tahmini)
        mc = magnitudes.median()

        # Mc üzerindeki depremler
        mags_above_mc = magnitudes[magnitudes >= mc]

        if len(mags_above_mc) < 5:
            mc = magnitudes.min()
            mags_above_mc = magnitudes

        # b-değeri hesabı (maximum likelihood)
        mean_mag = mags_above_mc.mean()
        b_value = np.log10(np.e) / (mean_mag - mc)

        # a-değeri
        n = len(mags_above_mc)
        a_value = np.log10(n) + b_value * mc

        result = {
            'b_degeri': round(b_value, 3),
            'a_degeri': round(a_value, 3),
            'mc_tahmini': round(mc, 2),
            'kullanilan_deprem_sayisi': n
        }

        self._analysis_results['b_value'] = result
        return result

    def risk_assessment(self) -> Dict[str, Any]:
        """Basit risk değerlendirmesi yap"""
        if self._data is None:
            raise ValueError("Veri seti yüklenmemiş")

        assessment = {
            'toplam_deprem': len(self._data),
            'risk_faktörleri': []
        }

        if 'buyukluk' in self._data.columns:
            large_quakes = len(self._data[self._data['buyukluk'] >= 5.0])
            assessment['5_ve_ustu_deprem'] = large_quakes

            if large_quakes > 10:
                assessment['risk_faktörleri'].append('Yüksek sayıda büyük deprem')

        if 'derinlik' in self._data.columns:
            shallow = len(self._data[self._data['derinlik'] <= 20])
            assessment['sig_deprem_orani'] = round(shallow / len(self._data) * 100, 1)

            if assessment['sig_deprem_orani'] > 50:
                assessment['risk_faktörleri'].append('Yüksek sığ deprem oranı')

        # Risk seviyesi belirleme
        risk_score = len(assessment['risk_faktörleri'])
        if risk_score == 0:
            assessment['risk_seviyesi'] = 'Düşük'
        elif risk_score == 1:
            assessment['risk_seviyesi'] = 'Orta'
        else:
            assessment['risk_seviyesi'] = 'Yüksek'

        self._analysis_results['risk_assessment'] = assessment
        return assessment

    def get_all_results(self) -> Dict[str, Any]:
        """Tüm analiz sonuçlarını döndür"""
        return self._analysis_results

    def generate_report(self) -> str:
        """Analiz raporu oluştur"""
        if not self._analysis_results:
            return "Henüz analiz yapılmamış. Önce analiz metodlarını çalıştırın."

        report = []
        report.append("=" * 60)
        report.append("SİSMİK ANALİZ RAPORU")
        report.append("=" * 60)
        report.append(f"Rapor Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        for analysis_name, results in self._analysis_results.items():
            report.append(f"\n--- {analysis_name.upper().replace('_', ' ')} ---")
            if isinstance(results, dict):
                for key, value in results.items():
                    report.append(f"  {key}: {value}")
            elif isinstance(results, list):
                for i, item in enumerate(results[:5], 1):
                    report.append(f"  {i}. {item}")

        report.append("\n" + "=" * 60)
        return "\n".join(report)
