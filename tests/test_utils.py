"""
Yardımcı fonksiyonlar için testler
"""

import pytest
import sys
from pathlib import Path

# src modülünü import edebilmek için
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import (
    haversine_distance,
    calculate_magnitude,
    calculate_energy,
    magnitude_to_tnt_equivalent,
    intensity_from_magnitude,
    mmi_description,
    earthquake_category,
    validate_coordinates,
    decimal_to_dms,
    dms_to_decimal,
    estimate_rupture_length,
    estimate_slip,
    seismic_moment,
    compare_earthquakes
)


class TestHaversineDistance:
    """Haversine mesafe fonksiyonu testleri"""

    def test_same_point(self):
        """Aynı nokta için mesafe 0 olmalı"""
        distance = haversine_distance(41.0, 29.0, 41.0, 29.0)
        assert distance == 0

    def test_istanbul_ankara(self):
        """İstanbul-Ankara mesafesi yaklaşık 350 km"""
        # İstanbul: 41.0082, 28.9784
        # Ankara: 39.9334, 32.8597
        distance = haversine_distance(41.0082, 28.9784, 39.9334, 32.8597)
        assert 340 < distance < 360

    def test_positive_distance(self):
        """Mesafe her zaman pozitif olmalı"""
        distance = haversine_distance(0, 0, 10, 10)
        assert distance > 0


class TestCalculateMagnitude:
    """Büyüklük hesabı testleri"""

    def test_positive_result(self):
        """Büyüklük pozitif olmalı"""
        mag = calculate_magnitude(amplitude=100, period=1, distance=100)
        assert mag > 0

    def test_invalid_amplitude(self):
        """Negatif amplitude hata vermeli"""
        with pytest.raises(ValueError):
            calculate_magnitude(amplitude=-1, period=1, distance=100)

    def test_invalid_period(self):
        """Negatif period hata vermeli"""
        with pytest.raises(ValueError):
            calculate_magnitude(amplitude=100, period=0, distance=100)


class TestCalculateEnergy:
    """Enerji hesabı testleri"""

    def test_energy_increases_with_magnitude(self):
        """Büyüklük arttıkça enerji artmalı"""
        e1 = calculate_energy(5.0)
        e2 = calculate_energy(6.0)
        assert e2 > e1

    def test_energy_ratio(self):
        """1 büyüklük farkı ~31.6 kat enerji farkı"""
        e1 = calculate_energy(5.0)
        e2 = calculate_energy(6.0)
        ratio = e2 / e1
        assert 30 < ratio < 33


class TestMagnitudeToTnt:
    """TNT eşdeğeri testleri"""

    def test_small_earthquake(self):
        """Küçük deprem için kg TNT"""
        amount, unit = magnitude_to_tnt_equivalent(2.0)
        assert "kg" in unit or "ton" in unit

    def test_large_earthquake(self):
        """Büyük deprem için megaton TNT"""
        amount, unit = magnitude_to_tnt_equivalent(9.0)
        assert "megaton" in unit.lower()


class TestIntensityFromMagnitude:
    """Şiddet tahmini testleri"""

    def test_intensity_range(self):
        """Şiddet 1-12 arasında olmalı"""
        for mag in [3.0, 5.0, 7.0]:
            intensity = intensity_from_magnitude(mag, distance=50)
            assert 1 <= intensity <= 12

    def test_intensity_increases_with_magnitude(self):
        """Büyüklük arttıkça şiddet artmalı"""
        i1 = intensity_from_magnitude(4.0, distance=50)
        i2 = intensity_from_magnitude(6.0, distance=50)
        assert i2 >= i1


class TestMmiDescription:
    """MMI açıklama testleri"""

    def test_valid_descriptions(self):
        """Tüm şiddetler için açıklama olmalı"""
        for i in range(1, 13):
            desc = mmi_description(i)
            assert len(desc) > 0

    def test_unknown_intensity(self):
        """Geçersiz şiddet için uygun mesaj"""
        desc = mmi_description(15)
        assert "Bilinmeyen" in desc


class TestEarthquakeCategory:
    """Deprem kategorisi testleri"""

    def test_micro_earthquake(self):
        """1.5 büyüklük mikro olmalı"""
        category, desc = earthquake_category(1.5)
        assert "Mikro" in category

    def test_large_earthquake(self):
        """7.5 büyüklük büyük olmalı"""
        category, desc = earthquake_category(7.5)
        assert "Büyük" in category


class TestValidateCoordinates:
    """Koordinat doğrulama testleri"""

    def test_valid_coordinates(self):
        """Geçerli koordinatlar True döndürmeli"""
        assert validate_coordinates(41.0, 29.0) is True
        assert validate_coordinates(-45.0, 170.0) is True

    def test_invalid_latitude(self):
        """Geçersiz enlem False döndürmeli"""
        assert validate_coordinates(91.0, 0.0) is False
        assert validate_coordinates(-91.0, 0.0) is False

    def test_invalid_longitude(self):
        """Geçersiz boylam False döndürmeli"""
        assert validate_coordinates(0.0, 181.0) is False
        assert validate_coordinates(0.0, -181.0) is False


class TestCoordinateConversion:
    """Koordinat dönüşüm testleri"""

    def test_decimal_to_dms(self):
        """Ondalık -> DMS dönüşümü"""
        result = decimal_to_dms(41.0082, is_latitude=True)
        assert "41°" in result
        assert "N" in result

    def test_dms_to_decimal(self):
        """DMS -> Ondalık dönüşümü"""
        result = dms_to_decimal(41, 0, 29.52, 'N')
        assert 40.9 < result < 41.1

    def test_south_coordinate(self):
        """Güney koordinatı negatif olmalı"""
        result = dms_to_decimal(45, 0, 0, 'S')
        assert result < 0


class TestRuptureEstimates:
    """Fay tahmini testleri"""

    def test_rupture_length_increases(self):
        """Büyüklük arttıkça kırılma uzunluğu artmalı"""
        l1 = estimate_rupture_length(5.0)
        l2 = estimate_rupture_length(7.0)
        assert l2 > l1

    def test_slip_increases(self):
        """Büyüklük arttıkça kayma artmalı"""
        s1 = estimate_slip(5.0)
        s2 = estimate_slip(7.0)
        assert s2 > s1


class TestSeismicMoment:
    """Sismik moment testleri"""

    def test_moment_positive(self):
        """Moment pozitif olmalı"""
        moment = seismic_moment(5.0)
        assert moment > 0

    def test_moment_increases(self):
        """Büyüklük arttıkça moment artmalı"""
        m1 = seismic_moment(5.0)
        m2 = seismic_moment(6.0)
        assert m2 > m1


class TestCompareEarthquakes:
    """Deprem karşılaştırma testleri"""

    def test_same_magnitude(self):
        """Aynı büyüklük için oran 1 olmalı"""
        energy_ratio, moment_ratio = compare_earthquakes(5.0, 5.0)
        assert energy_ratio == 1.0
        assert moment_ratio == 1.0

    def test_different_magnitude(self):
        """Farklı büyüklükler için oran > 1"""
        energy_ratio, moment_ratio = compare_earthquakes(6.0, 5.0)
        assert energy_ratio > 1
        assert moment_ratio > 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
