"""
Yardımcı Fonksiyonlar - Sismik hesaplamalar ve araçlar
"""

import numpy as np
from typing import Tuple, List, Optional
from datetime import datetime, timedelta
import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    İki nokta arasındaki Haversine mesafesini hesapla (km)

    Args:
        lat1, lon1: İlk noktanın koordinatları (derece)
        lat2, lon2: İkinci noktanın koordinatları (derece)

    Returns:
        float: Mesafe (km)
    """
    R = 6371  # Dünya yarıçapı (km)

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def calculate_magnitude(amplitude: float, period: float,
                         distance: float, depth: float = 10) -> float:
    """
    Deprem büyüklüğü hesapla (basitleştirilmiş formül)

    Args:
        amplitude: Dalga genliği (mikrometre)
        period: Dalga periyodu (saniye)
        distance: Episantr mesafesi (km)
        depth: Odak derinliği (km)

    Returns:
        float: Tahmini büyüklük (Mw)
    """
    if amplitude <= 0 or period <= 0 or distance <= 0:
        raise ValueError("Tüm parametreler pozitif olmalıdır")

    # Basitleştirilmiş ML formülü
    magnitude = math.log10(amplitude / period) + 1.66 * math.log10(distance) + 0.0001 * depth

    return round(magnitude, 1)


def calculate_energy(magnitude: float) -> float:
    """
    Deprem enerjisini hesapla (Joule)

    Args:
        magnitude: Deprem büyüklüğü (Mw)

    Returns:
        float: Enerji (Joule)
    """
    # Gutenberg-Richter enerji formülü
    log_energy = 1.5 * magnitude + 4.8
    return 10 ** log_energy


def magnitude_to_tnt_equivalent(magnitude: float) -> Tuple[float, str]:
    """
    Deprem büyüklüğünü TNT eşdeğerine çevir

    Args:
        magnitude: Deprem büyüklüğü

    Returns:
        Tuple[float, str]: TNT miktarı ve birimi
    """
    energy_joules = calculate_energy(magnitude)

    # 1 ton TNT = 4.184 × 10^9 Joule
    tnt_tons = energy_joules / (4.184e9)

    if tnt_tons < 1:
        return tnt_tons * 1000, "kg TNT"
    elif tnt_tons < 1000:
        return tnt_tons, "ton TNT"
    elif tnt_tons < 1000000:
        return tnt_tons / 1000, "kiloton TNT"
    else:
        return tnt_tons / 1000000, "megaton TNT"


def intensity_from_magnitude(magnitude: float, distance: float,
                              depth: float = 10) -> int:
    """
    Büyüklük ve mesafeden şiddet tahmini (MMI ölçeği)

    Args:
        magnitude: Deprem büyüklüğü
        distance: Episantrdan uzaklık (km)
        depth: Odak derinliği (km)

    Returns:
        int: MMI şiddet değeri (I-XII)
    """
    # Basitleştirilmiş şiddet formülü
    hypo_distance = math.sqrt(distance ** 2 + depth ** 2)

    if hypo_distance < 1:
        hypo_distance = 1

    intensity = 1.5 * magnitude - 2.5 * math.log10(hypo_distance) + 1.5

    # MMI sınırları içinde tut
    intensity = max(1, min(12, round(intensity)))

    return int(intensity)


def mmi_description(intensity: int) -> str:
    """
    MMI şiddet açıklaması

    Args:
        intensity: MMI değeri (I-XII)

    Returns:
        str: Şiddet açıklaması
    """
    descriptions = {
        1: "I - Hissedilmez",
        2: "II - Sadece hassas kişilerce hissedilir",
        3: "III - İç mekanlarda hissedilir",
        4: "IV - Birçok kişi tarafından hissedilir",
        5: "V - Neredeyse herkes hisseder, küçük hasarlar",
        6: "VI - Herkes hisseder, orta hasar",
        7: "VII - Ayakta durmak zorlaşır, önemli hasar",
        8: "VIII - Araç kullanmak zorlaşır, ciddi hasar",
        9: "IX - Genel panik, büyük hasar",
        10: "X - Çoğu yapı yıkılır",
        11: "XI - Az sayıda yapı ayakta kalır",
        12: "XII - Tam yıkım"
    }

    return descriptions.get(intensity, "Bilinmeyen şiddet")


def earthquake_category(magnitude: float) -> Tuple[str, str]:
    """
    Deprem kategorisini ve açıklamasını döndür

    Args:
        magnitude: Deprem büyüklüğü

    Returns:
        Tuple[str, str]: Kategori adı ve açıklama
    """
    categories = [
        (2.0, "Mikro", "Genellikle hissedilmez, yılda 1 milyondan fazla"),
        (3.0, "Çok Küçük", "Nadiren hissedilir, yılda 100.000+"),
        (4.0, "Küçük", "Hissedilir ama hasar nadir, yılda 10.000-15.000"),
        (5.0, "Hafif", "Bazı hasarlar olabilir, yılda 1.000-1.500"),
        (6.0, "Orta", "Yoğun bölgelerde ciddi hasar, yılda 100-150"),
        (7.0, "Güçlü", "Geniş alanda ciddi hasar, yılda 10-20"),
        (8.0, "Büyük", "Yüzlerce km'de ciddi hasar, yılda 1"),
        (9.0, "Çok Büyük", "Binlerce km'de yıkıcı, on yılda 1"),
        (10.0, "Muazzam", "Dünya çapında yıkım, hiç kaydedilmedi")
    ]

    for threshold, name, desc in categories:
        if magnitude < threshold:
            return name, desc

    return "Muazzam", "Dünya çapında yıkım"


def calculate_pga(magnitude: float, distance: float) -> float:
    """
    Peak Ground Acceleration (PGA) tahmini

    Args:
        magnitude: Deprem büyüklüğü
        distance: Mesafe (km)

    Returns:
        float: PGA (g birimi)
    """
    if distance < 1:
        distance = 1

    # Basitleştirilmiş attenuation ilişkisi
    log_pga = 0.249 * magnitude - 0.00255 * distance - math.log10(distance) - 0.786

    pga = 10 ** log_pga

    return round(pga, 4)


def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Koordinatların geçerliliğini kontrol et

    Args:
        lat: Enlem
        lon: Boylam

    Returns:
        bool: Geçerli mi?
    """
    return -90 <= lat <= 90 and -180 <= lon <= 180


def decimal_to_dms(decimal_degrees: float, is_latitude: bool = True) -> str:
    """
    Ondalık dereceyi derece-dakika-saniye formatına çevir

    Args:
        decimal_degrees: Ondalık derece
        is_latitude: Enlem mi?

    Returns:
        str: DMS formatında koordinat
    """
    is_positive = decimal_degrees >= 0
    decimal_degrees = abs(decimal_degrees)

    degrees = int(decimal_degrees)
    minutes_decimal = (decimal_degrees - degrees) * 60
    minutes = int(minutes_decimal)
    seconds = (minutes_decimal - minutes) * 60

    if is_latitude:
        direction = 'N' if is_positive else 'S'
    else:
        direction = 'E' if is_positive else 'W'

    return f"{degrees}° {minutes}' {seconds:.2f}\" {direction}"


def dms_to_decimal(degrees: int, minutes: int, seconds: float, direction: str) -> float:
    """
    Derece-dakika-saniye formatını ondalık dereceye çevir

    Args:
        degrees: Derece
        minutes: Dakika
        seconds: Saniye
        direction: Yön (N, S, E, W)

    Returns:
        float: Ondalık derece
    """
    decimal = degrees + minutes / 60 + seconds / 3600

    if direction.upper() in ['S', 'W']:
        decimal = -decimal

    return decimal


def format_magnitude(magnitude: float) -> str:
    """Büyüklüğü formatla"""
    return f"M{magnitude:.1f}"


def format_depth(depth: float) -> str:
    """Derinliği formatla"""
    return f"{depth:.1f} km"


def seconds_to_hms(seconds: float) -> str:
    """Saniyeyi saat:dakika:saniye formatına çevir"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def estimate_rupture_length(magnitude: float) -> float:
    """
    Deprem büyüklüğünden fay kırılma uzunluğu tahmini (km)

    Args:
        magnitude: Deprem büyüklüğü

    Returns:
        float: Tahmini kırılma uzunluğu (km)
    """
    # Wells & Coppersmith (1994) ilişkisi
    log_length = 0.74 * magnitude - 3.55
    return round(10 ** log_length, 1)


def estimate_slip(magnitude: float) -> float:
    """
    Deprem büyüklüğünden ortalama fay kayması tahmini (metre)

    Args:
        magnitude: Deprem büyüklüğü

    Returns:
        float: Tahmini kayma (metre)
    """
    # Wells & Coppersmith (1994) ilişkisi
    log_slip = 0.9 * magnitude - 6.32
    return round(10 ** log_slip, 2)


def seismic_moment(magnitude: float) -> float:
    """
    Sismik moment hesapla (Newton-metre)

    Args:
        magnitude: Moment büyüklüğü (Mw)

    Returns:
        float: Sismik moment (N·m)
    """
    # M0 = 10^(1.5*Mw + 9.1) (Newton-metre)
    log_moment = 1.5 * magnitude + 9.1
    return 10 ** log_moment


def compare_earthquakes(mag1: float, mag2: float) -> Tuple[float, float]:
    """
    İki depremi karşılaştır

    Args:
        mag1, mag2: Deprem büyüklükleri

    Returns:
        Tuple[float, float]: Enerji oranı ve moment oranı
    """
    energy_ratio = 10 ** (1.5 * (mag1 - mag2))
    moment_ratio = 10 ** (1.5 * (mag1 - mag2))

    return round(energy_ratio, 2), round(moment_ratio, 2)


def is_aftershock(main_shock_time: datetime, main_shock_mag: float,
                  event_time: datetime, event_mag: float,
                  distance: float, max_days: int = 365) -> bool:
    """
    Bir depremin artçı olup olmadığını kontrol et

    Args:
        main_shock_time: Ana şok zamanı
        main_shock_mag: Ana şok büyüklüğü
        event_time: Kontrol edilecek deprem zamanı
        event_mag: Kontrol edilecek deprem büyüklüğü
        distance: Ana şoktan uzaklık (km)
        max_days: Maksimum zaman penceresi (gün)

    Returns:
        bool: Artçı mı?
    """
    # Zaman kontrolü
    time_diff = (event_time - main_shock_time).days
    if time_diff < 0 or time_diff > max_days:
        return False

    # Büyüklük kontrolü (artçı ana şoktan küçük olmalı)
    if event_mag >= main_shock_mag:
        return False

    # Mesafe kontrolü (yaklaşık kırılma uzunluğunun 2 katı)
    max_distance = estimate_rupture_length(main_shock_mag) * 2
    if distance > max(max_distance, 100):
        return False

    return True
