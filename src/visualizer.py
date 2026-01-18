"""
Görselleştirme Modülü - Sismik verileri görselleştirir
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Optional, List, Tuple, Dict, Any
from pathlib import Path
from datetime import datetime


class SeismicVisualizer:
    """Sismik veri görselleştirme sınıfı"""

    # Renk paletleri
    MAGNITUDE_COLORS = {
        'low': '#2ecc71',      # Yeşil (< 3)
        'medium': '#f39c12',   # Turuncu (3-5)
        'high': '#e74c3c',     # Kırmızı (5-7)
        'extreme': '#9b59b6'   # Mor (> 7)
    }

    DEFAULT_FIGSIZE = (12, 8)
    DEFAULT_DPI = 100

    def __init__(self, data: Optional[pd.DataFrame] = None,
                 output_path: str = "output"):
        """
        SeismicVisualizer başlatıcı

        Args:
            data: Görselleştirilecek DataFrame
            output_path: Çıktı dosyalarının kaydedileceği dizin
        """
        self._data = data
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Matplotlib Türkçe karakter desteği
        plt.rcParams['font.family'] = 'DejaVu Sans'

    @property
    def data(self) -> Optional[pd.DataFrame]:
        return self._data

    @data.setter
    def data(self, value: pd.DataFrame) -> None:
        self._data = value

    def set_data(self, data: pd.DataFrame) -> None:
        """Veri setini ayarla"""
        self._data = data

    def _get_magnitude_color(self, magnitude: float) -> str:
        """Büyüklüğe göre renk döndür"""
        if magnitude < 3:
            return self.MAGNITUDE_COLORS['low']
        elif magnitude < 5:
            return self.MAGNITUDE_COLORS['medium']
        elif magnitude < 7:
            return self.MAGNITUDE_COLORS['high']
        else:
            return self.MAGNITUDE_COLORS['extreme']

    def _save_figure(self, fig: plt.Figure, filename: str) -> str:
        """Figürü kaydet"""
        filepath = self.output_path / filename
        fig.savefig(filepath, dpi=self.DEFAULT_DPI, bbox_inches='tight')
        plt.close(fig)
        return str(filepath)

    def plot_magnitude_histogram(self, bins: int = 20,
                                  save: bool = True) -> Optional[str]:
        """Büyüklük histogramı çiz"""
        if self._data is None or 'buyukluk' not in self._data.columns:
            raise ValueError("Geçerli büyüklük verisi yok")

        fig, ax = plt.subplots(figsize=self.DEFAULT_FIGSIZE)

        magnitudes = self._data['buyukluk'].dropna()

        # Histogram
        n, bins_edges, patches = ax.hist(magnitudes, bins=bins,
                                          edgecolor='black', alpha=0.7)

        # Renklendirme
        for patch, left_edge in zip(patches, bins_edges[:-1]):
            patch.set_facecolor(self._get_magnitude_color(left_edge))

        ax.set_xlabel('Büyüklük (Mw)', fontsize=12)
        ax.set_ylabel('Deprem Sayısı', fontsize=12)
        ax.set_title('Deprem Büyüklük Dağılımı', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # İstatistik bilgisi
        stats_text = f'Toplam: {len(magnitudes)}\nOrt: {magnitudes.mean():.2f}\nMax: {magnitudes.max():.2f}'
        ax.text(0.95, 0.95, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        if save:
            return self._save_figure(fig, 'magnitude_histogram.png')
        else:
            plt.show()
            return None

    def plot_depth_histogram(self, bins: int = 20,
                              save: bool = True) -> Optional[str]:
        """Derinlik histogramı çiz"""
        if self._data is None or 'derinlik' not in self._data.columns:
            raise ValueError("Geçerli derinlik verisi yok")

        fig, ax = plt.subplots(figsize=self.DEFAULT_FIGSIZE)

        depths = self._data['derinlik'].dropna()

        ax.hist(depths, bins=bins, edgecolor='black', alpha=0.7, color='#3498db')

        ax.set_xlabel('Derinlik (km)', fontsize=12)
        ax.set_ylabel('Deprem Sayısı', fontsize=12)
        ax.set_title('Deprem Derinlik Dağılımı', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Derinlik kategorileri için çizgiler
        ax.axvline(x=70, color='orange', linestyle='--', label='Sığ/Orta sınırı (70 km)')
        ax.axvline(x=300, color='red', linestyle='--', label='Orta/Derin sınırı (300 km)')
        ax.legend()

        if save:
            return self._save_figure(fig, 'depth_histogram.png')
        else:
            plt.show()
            return None

    def plot_scatter_map(self, save: bool = True) -> Optional[str]:
        """Deprem haritası çiz (scatter plot)"""
        if self._data is None:
            raise ValueError("Veri seti yüklenmemiş")

        if 'enlem' not in self._data.columns or 'boylam' not in self._data.columns:
            raise ValueError("Koordinat sütunları bulunamadı")

        fig, ax = plt.subplots(figsize=(14, 10))

        df = self._data.dropna(subset=['enlem', 'boylam'])

        # Büyüklüğe göre boyut ve renk
        if 'buyukluk' in df.columns:
            sizes = (df['buyukluk'] ** 2) * 5
            colors = df['buyukluk'].apply(self._get_magnitude_color)
        else:
            sizes = 20
            colors = '#3498db'

        scatter = ax.scatter(df['boylam'], df['enlem'],
                             s=sizes, c=colors, alpha=0.6, edgecolors='black', linewidth=0.5)

        ax.set_xlabel('Boylam', fontsize=12)
        ax.set_ylabel('Enlem', fontsize=12)
        ax.set_title('Deprem Dağılım Haritası', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Renk açıklaması
        legend_elements = [
            plt.scatter([], [], c=self.MAGNITUDE_COLORS['low'], s=50, label='< 3.0'),
            plt.scatter([], [], c=self.MAGNITUDE_COLORS['medium'], s=100, label='3.0 - 5.0'),
            plt.scatter([], [], c=self.MAGNITUDE_COLORS['high'], s=150, label='5.0 - 7.0'),
            plt.scatter([], [], c=self.MAGNITUDE_COLORS['extreme'], s=200, label='> 7.0')
        ]
        ax.legend(handles=legend_elements, title='Büyüklük', loc='upper right')

        if save:
            return self._save_figure(fig, 'earthquake_map.png')
        else:
            plt.show()
            return None

    def plot_time_series(self, freq: str = 'M', save: bool = True) -> Optional[str]:
        """Zaman serisi grafiği çiz"""
        if self._data is None:
            raise ValueError("Veri seti yüklenmemiş")

        date_col = 'datetime' if 'datetime' in self._data.columns else 'tarih'
        if date_col not in self._data.columns:
            raise ValueError("Tarih sütunu bulunamadı")

        fig, axes = plt.subplots(2, 1, figsize=(14, 10))

        df = self._data.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.set_index(date_col)

        # Deprem sayısı zaman serisi
        counts = df.resample(freq).size()
        axes[0].plot(counts.index, counts.values, color='#3498db', linewidth=1.5)
        axes[0].fill_between(counts.index, counts.values, alpha=0.3)
        axes[0].set_ylabel('Deprem Sayısı', fontsize=12)
        axes[0].set_title('Zamana Göre Deprem Sayısı', fontsize=14, fontweight='bold')
        axes[0].grid(True, alpha=0.3)

        # Ortalama büyüklük zaman serisi
        if 'buyukluk' in df.columns:
            avg_mag = df['buyukluk'].resample(freq).mean()
            axes[1].plot(avg_mag.index, avg_mag.values, color='#e74c3c', linewidth=1.5)
            axes[1].fill_between(avg_mag.index, avg_mag.values, alpha=0.3, color='#e74c3c')
            axes[1].set_ylabel('Ortalama Büyüklük', fontsize=12)
            axes[1].set_title('Zamana Göre Ortalama Büyüklük', fontsize=14, fontweight='bold')
            axes[1].grid(True, alpha=0.3)

        axes[-1].set_xlabel('Tarih', fontsize=12)

        plt.tight_layout()

        if save:
            return self._save_figure(fig, 'time_series.png')
        else:
            plt.show()
            return None

    def plot_depth_vs_magnitude(self, save: bool = True) -> Optional[str]:
        """Derinlik vs Büyüklük scatter plot"""
        if self._data is None:
            raise ValueError("Veri seti yüklenmemiş")

        if 'derinlik' not in self._data.columns or 'buyukluk' not in self._data.columns:
            raise ValueError("Derinlik veya büyüklük sütunu bulunamadı")

        fig, ax = plt.subplots(figsize=self.DEFAULT_FIGSIZE)

        df = self._data.dropna(subset=['derinlik', 'buyukluk'])

        colors = df['buyukluk'].apply(self._get_magnitude_color)

        ax.scatter(df['buyukluk'], df['derinlik'], c=colors, alpha=0.6,
                   edgecolors='black', linewidth=0.5)

        ax.set_xlabel('Büyüklük (Mw)', fontsize=12)
        ax.set_ylabel('Derinlik (km)', fontsize=12)
        ax.set_title('Derinlik vs Büyüklük İlişkisi', fontsize=14, fontweight='bold')
        ax.invert_yaxis()  # Derinlik arttıkça aşağı
        ax.grid(True, alpha=0.3)

        if save:
            return self._save_figure(fig, 'depth_vs_magnitude.png')
        else:
            plt.show()
            return None

    def plot_magnitude_frequency(self, save: bool = True) -> Optional[str]:
        """Gutenberg-Richter grafiği (log-linear)"""
        if self._data is None or 'buyukluk' not in self._data.columns:
            raise ValueError("Geçerli büyüklük verisi yok")

        fig, ax = plt.subplots(figsize=self.DEFAULT_FIGSIZE)

        magnitudes = self._data['buyukluk'].dropna().sort_values()

        # Kümülatif frekans hesapla
        mag_bins = np.arange(magnitudes.min(), magnitudes.max() + 0.1, 0.1)
        cumulative_counts = []

        for mag in mag_bins:
            count = len(magnitudes[magnitudes >= mag])
            cumulative_counts.append(count)

        ax.semilogy(mag_bins, cumulative_counts, 'bo-', markersize=4)

        ax.set_xlabel('Büyüklük (Mw)', fontsize=12)
        ax.set_ylabel('Kümülatif Deprem Sayısı (log)', fontsize=12)
        ax.set_title('Gutenberg-Richter İlişkisi', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        if save:
            return self._save_figure(fig, 'magnitude_frequency.png')
        else:
            plt.show()
            return None

    def plot_hourly_distribution(self, save: bool = True) -> Optional[str]:
        """Saatlik dağılım grafiği"""
        if self._data is None:
            raise ValueError("Veri seti yüklenmemiş")

        date_col = 'datetime' if 'datetime' in self._data.columns else None
        if date_col is None and 'saat' not in self._data.columns:
            raise ValueError("Saat bilgisi bulunamadı")

        fig, ax = plt.subplots(figsize=self.DEFAULT_FIGSIZE, subplot_kw=dict(projection='polar'))

        df = self._data.copy()

        if date_col:
            df['saat_num'] = pd.to_datetime(df[date_col]).dt.hour
        else:
            df['saat_num'] = pd.to_datetime(df['saat'], format='%H:%M:%S').dt.hour

        hourly_counts = df.groupby('saat_num').size()

        # Polar koordinatlar
        theta = np.linspace(0, 2 * np.pi, 24, endpoint=False)
        radii = [hourly_counts.get(h, 0) for h in range(24)]
        width = 2 * np.pi / 24

        bars = ax.bar(theta, radii, width=width, bottom=0, alpha=0.7)

        # Renklendirme
        for bar, r in zip(bars, radii):
            bar.set_facecolor(plt.cm.viridis(r / max(radii)))

        ax.set_xticks(theta)
        ax.set_xticklabels([f'{h:02d}:00' for h in range(24)])
        ax.set_title('Saatlik Deprem Dağılımı', fontsize=14, fontweight='bold', pad=20)

        if save:
            return self._save_figure(fig, 'hourly_distribution.png')
        else:
            plt.show()
            return None

    def create_dashboard(self, save: bool = True) -> Optional[str]:
        """Özet dashboard oluştur"""
        if self._data is None:
            raise ValueError("Veri seti yüklenmemiş")

        fig = plt.figure(figsize=(16, 12))

        # Alt grafik düzeni
        gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)

        # 1. Harita (geniş)
        ax1 = fig.add_subplot(gs[0, :2])
        if 'enlem' in self._data.columns and 'boylam' in self._data.columns:
            df = self._data.dropna(subset=['enlem', 'boylam'])
            if 'buyukluk' in df.columns:
                sizes = (df['buyukluk'] ** 2) * 3
                colors = df['buyukluk'].apply(self._get_magnitude_color)
            else:
                sizes = 15
                colors = '#3498db'
            ax1.scatter(df['boylam'], df['enlem'], s=sizes, c=colors, alpha=0.5)
        ax1.set_title('Deprem Haritası', fontweight='bold')
        ax1.set_xlabel('Boylam')
        ax1.set_ylabel('Enlem')
        ax1.grid(True, alpha=0.3)

        # 2. Büyüklük histogramı
        ax2 = fig.add_subplot(gs[0, 2])
        if 'buyukluk' in self._data.columns:
            ax2.hist(self._data['buyukluk'].dropna(), bins=15, color='#3498db',
                     edgecolor='black', alpha=0.7)
        ax2.set_title('Büyüklük Dağılımı', fontweight='bold')
        ax2.set_xlabel('Büyüklük')
        ax2.set_ylabel('Sayı')

        # 3. Derinlik histogramı
        ax3 = fig.add_subplot(gs[1, 0])
        if 'derinlik' in self._data.columns:
            ax3.hist(self._data['derinlik'].dropna(), bins=15, color='#e74c3c',
                     edgecolor='black', alpha=0.7)
        ax3.set_title('Derinlik Dağılımı', fontweight='bold')
        ax3.set_xlabel('Derinlik (km)')
        ax3.set_ylabel('Sayı')

        # 4. Zaman serisi
        ax4 = fig.add_subplot(gs[1, 1])
        date_col = 'datetime' if 'datetime' in self._data.columns else 'tarih'
        if date_col in self._data.columns:
            df = self._data.copy()
            df[date_col] = pd.to_datetime(df[date_col])
            counts = df.set_index(date_col).resample('M').size()
            ax4.plot(counts.index, counts.values, color='#2ecc71')
            ax4.fill_between(counts.index, counts.values, alpha=0.3, color='#2ecc71')
        ax4.set_title('Aylık Deprem Sayısı', fontweight='bold')
        ax4.set_xlabel('Tarih')
        ax4.set_ylabel('Sayı')
        ax4.tick_params(axis='x', rotation=45)

        # 5. İstatistik özeti
        ax5 = fig.add_subplot(gs[1, 2])
        ax5.axis('off')

        stats_text = f"""
        ÖZET İSTATİSTİKLER
        ==================
        Toplam Deprem: {len(self._data)}
        """

        if 'buyukluk' in self._data.columns:
            stats_text += f"""
        Büyüklük:
          Min: {self._data['buyukluk'].min():.2f}
          Max: {self._data['buyukluk'].max():.2f}
          Ort: {self._data['buyukluk'].mean():.2f}
            """

        if 'derinlik' in self._data.columns:
            stats_text += f"""
        Derinlik:
          Min: {self._data['derinlik'].min():.1f} km
          Max: {self._data['derinlik'].max():.1f} km
          Ort: {self._data['derinlik'].mean():.1f} km
            """

        ax5.text(0.1, 0.9, stats_text, transform=ax5.transAxes, fontsize=11,
                 verticalalignment='top', fontfamily='monospace',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        fig.suptitle('Sismik Analiz Dashboard', fontsize=16, fontweight='bold', y=0.98)

        if save:
            return self._save_figure(fig, 'dashboard.png')
        else:
            plt.show()
            return None

    def generate_all_plots(self) -> List[str]:
        """Tüm grafikleri oluştur"""
        generated_files = []

        plot_methods = [
            ('magnitude_histogram', self.plot_magnitude_histogram),
            ('depth_histogram', self.plot_depth_histogram),
            ('scatter_map', self.plot_scatter_map),
            ('time_series', self.plot_time_series),
            ('depth_vs_magnitude', self.plot_depth_vs_magnitude),
            ('magnitude_frequency', self.plot_magnitude_frequency),
            ('dashboard', self.create_dashboard)
        ]

        for name, method in plot_methods:
            try:
                filepath = method(save=True)
                if filepath:
                    generated_files.append(filepath)
                    print(f"✓ {name} oluşturuldu: {filepath}")
            except Exception as e:
                print(f"✗ {name} oluşturulamadı: {e}")

        return generated_files
