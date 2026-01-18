"""
Veri yükleme modülü - Sismik veri dosyalarını okur ve işler
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import json


class DataLoader:
    """Sismik veri yükleme ve ön işleme sınıfı"""

    REQUIRED_COLUMNS = ['tarih', 'saat', 'enlem', 'boylam', 'derinlik', 'buyukluk']

    def __init__(self, data_path: Optional[str] = None):
        """
        DataLoader başlatıcı

        Args:
            data_path: Veri dosyalarının bulunduğu dizin yolu
        """
        self.data_path = Path(data_path) if data_path else Path("data")
        self._data: Optional[pd.DataFrame] = None
        self._metadata: Dict[str, Any] = {}

    @property
    def data(self) -> Optional[pd.DataFrame]:
        """Yüklenen veri"""
        return self._data

    @property
    def metadata(self) -> Dict[str, Any]:
        """Veri metadata bilgileri"""
        return self._metadata

    def load_csv(self, filename: str, encoding: str = 'utf-8') -> pd.DataFrame:
        """
        CSV dosyasından sismik veri yükle

        Args:
            filename: Dosya adı
            encoding: Dosya kodlaması

        Returns:
            pd.DataFrame: Yüklenen veri
        """
        filepath = self.data_path / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Dosya bulunamadı: {filepath}")

        try:
            df = pd.read_csv(filepath, encoding=encoding)
            df = self._standardize_columns(df)
            df = self._parse_datetime(df)
            self._data = df
            self._update_metadata(filename)
            return df
        except Exception as e:
            raise ValueError(f"CSV okuma hatası: {e}")

    def load_excel(self, filename: str, sheet_name: str = 0) -> pd.DataFrame:
        """
        Excel dosyasından sismik veri yükle

        Args:
            filename: Dosya adı
            sheet_name: Sayfa adı veya indeksi

        Returns:
            pd.DataFrame: Yüklenen veri
        """
        filepath = self.data_path / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Dosya bulunamadı: {filepath}")

        try:
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            df = self._standardize_columns(df)
            df = self._parse_datetime(df)
            self._data = df
            self._update_metadata(filename)
            return df
        except Exception as e:
            raise ValueError(f"Excel okuma hatası: {e}")

    def load_json(self, filename: str) -> pd.DataFrame:
        """
        JSON dosyasından sismik veri yükle

        Args:
            filename: Dosya adı

        Returns:
            pd.DataFrame: Yüklenen veri
        """
        filepath = self.data_path / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Dosya bulunamadı: {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            df = pd.DataFrame(data)
            df = self._standardize_columns(df)
            df = self._parse_datetime(df)
            self._data = df
            self._update_metadata(filename)
            return df
        except Exception as e:
            raise ValueError(f"JSON okuma hatası: {e}")

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sütun isimlerini standartlaştır"""
        column_mapping = {
            'latitude': 'enlem',
            'lat': 'enlem',
            'longitude': 'boylam',
            'lon': 'boylam',
            'lng': 'boylam',
            'depth': 'derinlik',
            'magnitude': 'buyukluk',
            'mag': 'buyukluk',
            'date': 'tarih',
            'time': 'saat'
        }

        df.columns = df.columns.str.lower().str.strip()
        df = df.rename(columns=column_mapping)

        return df

    def _parse_datetime(self, df: pd.DataFrame) -> pd.DataFrame:
        """Tarih ve saat sütunlarını parse et"""
        if 'tarih' in df.columns:
            try:
                df['tarih'] = pd.to_datetime(df['tarih'])
            except Exception:
                pass

        if 'tarih' in df.columns and 'saat' in df.columns:
            try:
                df['datetime'] = pd.to_datetime(
                    df['tarih'].astype(str) + ' ' + df['saat'].astype(str)
                )
            except Exception:
                pass

        return df

    def _update_metadata(self, filename: str) -> None:
        """Metadata bilgilerini güncelle"""
        if self._data is not None:
            self._metadata = {
                'dosya': filename,
                'satir_sayisi': len(self._data),
                'sutun_sayisi': len(self._data.columns),
                'sutunlar': list(self._data.columns),
                'yukleme_zamani': datetime.now().isoformat()
            }

    def filter_by_magnitude(self, min_mag: float = 0, max_mag: float = 10) -> pd.DataFrame:
        """Büyüklüğe göre filtrele"""
        if self._data is None:
            raise ValueError("Önce veri yüklemelisiniz")

        if 'buyukluk' not in self._data.columns:
            raise ValueError("'buyukluk' sütunu bulunamadı")

        mask = (self._data['buyukluk'] >= min_mag) & (self._data['buyukluk'] <= max_mag)
        return self._data[mask].copy()

    def filter_by_region(self, min_lat: float, max_lat: float,
                         min_lon: float, max_lon: float) -> pd.DataFrame:
        """Coğrafi bölgeye göre filtrele"""
        if self._data is None:
            raise ValueError("Önce veri yüklemelisiniz")

        mask = (
            (self._data['enlem'] >= min_lat) &
            (self._data['enlem'] <= max_lat) &
            (self._data['boylam'] >= min_lon) &
            (self._data['boylam'] <= max_lon)
        )
        return self._data[mask].copy()

    def filter_by_date_range(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Tarih aralığına göre filtrele"""
        if self._data is None:
            raise ValueError("Önce veri yüklemelisiniz")

        if 'datetime' in self._data.columns:
            date_col = 'datetime'
        elif 'tarih' in self._data.columns:
            date_col = 'tarih'
        else:
            raise ValueError("Tarih sütunu bulunamadı")

        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)

        mask = (self._data[date_col] >= start) & (self._data[date_col] <= end)
        return self._data[mask].copy()

    def get_summary(self) -> Dict[str, Any]:
        """Veri özeti döndür"""
        if self._data is None:
            return {"durum": "Veri yüklenmemiş"}

        summary = {
            "toplam_deprem": len(self._data),
            "metadata": self._metadata
        }

        if 'buyukluk' in self._data.columns:
            summary["buyukluk_istatistik"] = {
                "min": float(self._data['buyukluk'].min()),
                "max": float(self._data['buyukluk'].max()),
                "ortalama": float(self._data['buyukluk'].mean()),
                "medyan": float(self._data['buyukluk'].median())
            }

        if 'derinlik' in self._data.columns:
            summary["derinlik_istatistik"] = {
                "min": float(self._data['derinlik'].min()),
                "max": float(self._data['derinlik'].max()),
                "ortalama": float(self._data['derinlik'].mean())
            }

        return summary

    def export_to_csv(self, filename: str, output_path: Optional[str] = None) -> str:
        """Veriyi CSV olarak dışa aktar"""
        if self._data is None:
            raise ValueError("Dışa aktarılacak veri yok")

        out_dir = Path(output_path) if output_path else self.data_path / "processed"
        out_dir.mkdir(parents=True, exist_ok=True)

        filepath = out_dir / filename
        self._data.to_csv(filepath, index=False, encoding='utf-8')

        return str(filepath)
