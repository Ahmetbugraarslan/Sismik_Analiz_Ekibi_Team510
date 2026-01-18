"""
SeismicAnalyzer sınıfı için testler
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.seismic_analyzer import SeismicAnalyzer


@pytest.fixture
def sample_data():
    """Test için örnek veri oluştur"""
    np.random.seed(42)
    n = 100

    dates = [(datetime(2024, 1, 1) + timedelta(days=i)) for i in range(n)]

    return pd.DataFrame({
        'tarih': dates,
        'enlem': np.random.uniform(36, 42, n),
        'boylam': np.random.uniform(26, 45, n),
        'derinlik': np.random.exponential(30, n),
        'buyukluk': np.random.exponential(1.5, n) + 1
    })


@pytest.fixture
def analyzer(sample_data):
    """SeismicAnalyzer örneği"""
    return SeismicAnalyzer(sample_data)


class TestSeismicAnalyzerInit:
    """Başlatma testleri"""

    def test_init_with_data(self, sample_data):
        """Veri ile başlatma"""
        analyzer = SeismicAnalyzer(sample_data)
        assert analyzer.data is not None
        assert len(analyzer.data) == 100

    def test_init_without_data(self):
        """Veri olmadan başlatma"""
        analyzer = SeismicAnalyzer()
        assert analyzer.data is None

    def test_set_data(self, sample_data):
        """Veri ayarlama"""
        analyzer = SeismicAnalyzer()
        analyzer.set_data(sample_data)
        assert analyzer.data is not None


class TestBasicStatistics:
    """Temel istatistik testleri"""

    def test_basic_statistics(self, analyzer):
        """Temel istatistikler döndürülmeli"""
        stats = analyzer.basic_statistics()
        assert 'toplam_deprem' in stats
        assert stats['toplam_deprem'] == 100

    def test_statistics_include_numeric_columns(self, analyzer):
        """Sayısal sütunlar için istatistik olmalı"""
        stats = analyzer.basic_statistics()
        assert 'buyukluk_istatistik' in stats
        assert 'min' in stats['buyukluk_istatistik']
        assert 'max' in stats['buyukluk_istatistik']

    def test_no_data_error(self):
        """Veri yoksa hata vermeli"""
        analyzer = SeismicAnalyzer()
        with pytest.raises(ValueError):
            analyzer.basic_statistics()


class TestMagnitudeCategories:
    """Büyüklük kategorisi testleri"""

    def test_categorize_by_magnitude(self, analyzer):
        """Kategoriler döndürülmeli"""
        categories = analyzer.categorize_by_magnitude()
        assert isinstance(categories, dict)
        assert 'mikro' in categories or 'kucuk' in categories

    def test_total_matches_data_length(self, analyzer):
        """Kategori toplamı veri uzunluğuna eşit olmalı"""
        categories = analyzer.categorize_by_magnitude()
        total = sum(categories.values())
        assert total == 100


class TestDepthAnalysis:
    """Derinlik analizi testleri"""

    def test_depth_analysis(self, analyzer):
        """Derinlik analizi döndürülmeli"""
        analysis = analyzer.depth_analysis()
        assert 'sig' in analysis
        assert 'orta' in analysis
        assert 'derin' in analysis

    def test_depth_stats(self, analyzer):
        """Derinlik istatistikleri olmalı"""
        analysis = analyzer.depth_analysis()
        assert 'ortalama_derinlik' in analysis
        assert 'max_derinlik' in analysis


class TestTemporalAnalysis:
    """Zamansal analiz testleri"""

    def test_temporal_analysis(self, analyzer):
        """Zamansal analiz döndürülmeli"""
        analysis = analyzer.temporal_analysis()
        assert 'ilk_deprem' in analysis
        assert 'son_deprem' in analysis

    def test_monthly_distribution(self, analyzer):
        """Aylık dağılım olmalı"""
        analysis = analyzer.temporal_analysis()
        assert 'aylik_dagilim' in analysis


class TestSpatialAnalysis:
    """Mekansal analiz testleri"""

    def test_spatial_analysis(self, analyzer):
        """Mekansal analiz döndürülmeli"""
        analysis = analyzer.spatial_analysis()
        assert 'enlem_aralik' in analysis
        assert 'boylam_aralik' in analysis

    def test_center_calculation(self, analyzer):
        """Merkez hesaplanmalı"""
        analysis = analyzer.spatial_analysis()
        assert 'merkez' in analysis
        assert 'enlem' in analysis['merkez']
        assert 'boylam' in analysis['merkez']


class TestBValueCalculation:
    """b-değeri hesabı testleri"""

    def test_b_value_calculation(self, analyzer):
        """b-değeri hesaplanmalı"""
        result = analyzer.calculate_b_value()
        assert 'b_degeri' in result
        assert 'a_degeri' in result

    def test_b_value_positive(self, analyzer):
        """b-değeri pozitif olmalı"""
        result = analyzer.calculate_b_value()
        assert result['b_degeri'] > 0


class TestRiskAssessment:
    """Risk değerlendirme testleri"""

    def test_risk_assessment(self, analyzer):
        """Risk değerlendirmesi döndürülmeli"""
        assessment = analyzer.risk_assessment()
        assert 'toplam_deprem' in assessment
        assert 'risk_seviyesi' in assessment

    def test_risk_level_valid(self, analyzer):
        """Risk seviyesi geçerli olmalı"""
        assessment = analyzer.risk_assessment()
        assert assessment['risk_seviyesi'] in ['Düşük', 'Orta', 'Yüksek']


class TestReportGeneration:
    """Rapor oluşturma testleri"""

    def test_generate_report_empty(self):
        """Analiz yapılmadan rapor"""
        analyzer = SeismicAnalyzer()
        report = analyzer.generate_report()
        assert "Henüz analiz yapılmamış" in report

    def test_generate_report_with_analysis(self, analyzer):
        """Analiz sonrası rapor"""
        analyzer.basic_statistics()
        report = analyzer.generate_report()
        assert "SİSMİK ANALİZ RAPORU" in report

    def test_get_all_results(self, analyzer):
        """Tüm sonuçlar döndürülmeli"""
        analyzer.basic_statistics()
        analyzer.categorize_by_magnitude()
        results = analyzer.get_all_results()
        assert 'basic_stats' in results
        assert 'magnitude_categories' in results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
