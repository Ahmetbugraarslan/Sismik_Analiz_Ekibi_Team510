#!/usr/bin/env python3
"""
Sismik Analiz Ekibi - Team510
Ana uygulama modülü

Kullanım:
    python main.py --help
    python main.py analyze --file data.csv
    python main.py visualize --file data.csv --output plots/
    python main.py report --file data.csv
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from src.data_loader import DataLoader
from src.seismic_analyzer import SeismicAnalyzer
from src.visualizer import SeismicVisualizer
from src import __version__


def print_banner():
    """Uygulama banner'ı"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║         SİSMİK ANALİZ EKİBİ - TEAM510                    ║
    ║         Deprem Veri Analiz Sistemi v{}               ║
    ╚═══════════════════════════════════════════════════════════╝
    """.format(__version__)
    print(banner)


def cmd_analyze(args):
    """Analiz komutu"""
    print(f"\n[*] Veri yükleniyor: {args.file}")

    loader = DataLoader(data_path=str(Path(args.file).parent))
    filename = Path(args.file).name

    # Dosya uzantısına göre yükle
    if filename.endswith('.csv'):
        data = loader.load_csv(filename)
    elif filename.endswith(('.xlsx', '.xls')):
        data = loader.load_excel(filename)
    elif filename.endswith('.json'):
        data = loader.load_json(filename)
    else:
        print("[!] Desteklenmeyen dosya formatı. CSV, Excel veya JSON kullanın.")
        return

    print(f"[+] {len(data)} deprem verisi yüklendi")

    # Analiz
    analyzer = SeismicAnalyzer(data)

    print("\n" + "=" * 50)
    print("TEMEL İSTATİSTİKLER")
    print("=" * 50)
    stats = analyzer.basic_statistics()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"\n{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"{key}: {value}")

    print("\n" + "=" * 50)
    print("BÜYÜKLÜK KATEGORİLERİ")
    print("=" * 50)
    try:
        categories = analyzer.categorize_by_magnitude()
        for cat, count in categories.items():
            print(f"  {cat}: {count}")
    except Exception as e:
        print(f"  [!] {e}")

    print("\n" + "=" * 50)
    print("DERİNLİK ANALİZİ")
    print("=" * 50)
    try:
        depth = analyzer.depth_analysis()
        for key, value in depth.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"  [!] {e}")

    print("\n" + "=" * 50)
    print("ZAMANSAL ANALİZ")
    print("=" * 50)
    try:
        temporal = analyzer.temporal_analysis()
        print(f"  İlk deprem: {temporal.get('ilk_deprem', 'N/A')}")
        print(f"  Son deprem: {temporal.get('son_deprem', 'N/A')}")
        print(f"  Toplam gün: {temporal.get('toplam_gun', 'N/A')}")
        print(f"  Günlük ortalama: {temporal.get('gunluk_ortalama', 'N/A')}")
    except Exception as e:
        print(f"  [!] {e}")

    print("\n" + "=" * 50)
    print("B-DEĞERİ ANALİZİ")
    print("=" * 50)
    try:
        b_value = analyzer.calculate_b_value()
        for key, value in b_value.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"  [!] {e}")

    print("\n" + "=" * 50)
    print("RİSK DEĞERLENDİRMESİ")
    print("=" * 50)
    try:
        risk = analyzer.risk_assessment()
        print(f"  Risk seviyesi: {risk.get('risk_seviyesi', 'N/A')}")
        print(f"  5+ deprem sayısı: {risk.get('5_ve_ustu_deprem', 'N/A')}")
        if risk.get('risk_faktörleri'):
            print("  Risk faktörleri:")
            for factor in risk['risk_faktörleri']:
                print(f"    - {factor}")
    except Exception as e:
        print(f"  [!] {e}")


def cmd_visualize(args):
    """Görselleştirme komutu"""
    print(f"\n[*] Veri yükleniyor: {args.file}")

    loader = DataLoader(data_path=str(Path(args.file).parent))
    filename = Path(args.file).name

    if filename.endswith('.csv'):
        data = loader.load_csv(filename)
    elif filename.endswith(('.xlsx', '.xls')):
        data = loader.load_excel(filename)
    elif filename.endswith('.json'):
        data = loader.load_json(filename)
    else:
        print("[!] Desteklenmeyen dosya formatı")
        return

    print(f"[+] {len(data)} deprem verisi yüklendi")

    # Görselleştirme
    output_dir = args.output or "output"
    visualizer = SeismicVisualizer(data, output_path=output_dir)

    print(f"\n[*] Grafikler oluşturuluyor: {output_dir}/")

    generated = visualizer.generate_all_plots()

    print(f"\n[+] {len(generated)} grafik oluşturuldu")


def cmd_report(args):
    """Rapor oluşturma komutu"""
    print(f"\n[*] Veri yükleniyor: {args.file}")

    loader = DataLoader(data_path=str(Path(args.file).parent))
    filename = Path(args.file).name

    if filename.endswith('.csv'):
        data = loader.load_csv(filename)
    elif filename.endswith(('.xlsx', '.xls')):
        data = loader.load_excel(filename)
    elif filename.endswith('.json'):
        data = loader.load_json(filename)
    else:
        print("[!] Desteklenmeyen dosya formatı")
        return

    # Tüm analizleri çalıştır
    analyzer = SeismicAnalyzer(data)
    analyzer.basic_statistics()
    analyzer.categorize_by_magnitude()

    try:
        analyzer.depth_analysis()
    except Exception:
        pass

    try:
        analyzer.temporal_analysis()
    except Exception:
        pass

    try:
        analyzer.spatial_analysis()
    except Exception:
        pass

    try:
        analyzer.calculate_b_value()
    except Exception:
        pass

    try:
        analyzer.risk_assessment()
    except Exception:
        pass

    # Rapor oluştur
    report = analyzer.generate_report()
    print(report)

    # Dosyaya kaydet
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n[+] Rapor kaydedildi: {output_path}")


def cmd_info(args):
    """Bilgi komutu"""
    print("\nSismik Analiz Ekibi - Team510")
    print(f"Versiyon: {__version__}")
    print("\nDesteklenen dosya formatları:")
    print("  - CSV (.csv)")
    print("  - Excel (.xlsx, .xls)")
    print("  - JSON (.json)")
    print("\nGerekli sütunlar:")
    print("  - tarih / date: Deprem tarihi")
    print("  - saat / time: Deprem saati (opsiyonel)")
    print("  - enlem / latitude / lat: Enlem koordinatı")
    print("  - boylam / longitude / lon: Boylam koordinatı")
    print("  - derinlik / depth: Odak derinliği (km)")
    print("  - buyukluk / magnitude / mag: Deprem büyüklüğü")


def create_sample_data(args):
    """Örnek veri oluştur"""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta

    np.random.seed(42)
    n = args.count or 100

    # Türkiye sınırları içinde rastgele koordinatlar
    data = {
        'tarih': [(datetime(2024, 1, 1) + timedelta(days=np.random.randint(0, 365))).strftime('%Y-%m-%d')
                  for _ in range(n)],
        'saat': [f"{np.random.randint(0, 24):02d}:{np.random.randint(0, 60):02d}:{np.random.randint(0, 60):02d}"
                 for _ in range(n)],
        'enlem': np.random.uniform(36, 42, n).round(4),
        'boylam': np.random.uniform(26, 45, n).round(4),
        'derinlik': np.random.exponential(20, n).round(1),
        'buyukluk': np.random.exponential(1.5, n).round(1) + 1
    }

    df = pd.DataFrame(data)

    output_path = args.output or 'data/raw/sample_earthquakes.csv'
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"[+] {n} adet örnek deprem verisi oluşturuldu: {output_path}")


def main():
    """Ana fonksiyon"""
    print_banner()

    parser = argparse.ArgumentParser(
        description='Sismik Analiz Ekibi - Deprem Veri Analiz Sistemi',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Komutlar')

    # Analyze komutu
    parser_analyze = subparsers.add_parser('analyze', help='Deprem verilerini analiz et')
    parser_analyze.add_argument('--file', '-f', required=True, help='Veri dosyası yolu')
    parser_analyze.set_defaults(func=cmd_analyze)

    # Visualize komutu
    parser_viz = subparsers.add_parser('visualize', help='Grafik ve görselleştirmeler oluştur')
    parser_viz.add_argument('--file', '-f', required=True, help='Veri dosyası yolu')
    parser_viz.add_argument('--output', '-o', help='Çıktı dizini')
    parser_viz.set_defaults(func=cmd_visualize)

    # Report komutu
    parser_report = subparsers.add_parser('report', help='Analiz raporu oluştur')
    parser_report.add_argument('--file', '-f', required=True, help='Veri dosyası yolu')
    parser_report.add_argument('--output', '-o', help='Rapor dosyası yolu')
    parser_report.set_defaults(func=cmd_report)

    # Info komutu
    parser_info = subparsers.add_parser('info', help='Program hakkında bilgi')
    parser_info.set_defaults(func=cmd_info)

    # Sample komutu
    parser_sample = subparsers.add_parser('sample', help='Örnek veri oluştur')
    parser_sample.add_argument('--count', '-n', type=int, default=100, help='Deprem sayısı')
    parser_sample.add_argument('--output', '-o', help='Çıktı dosyası')
    parser_sample.set_defaults(func=create_sample_data)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        print("\nKullanım örnekleri:")
        print("  python main.py analyze --file data/earthquakes.csv")
        print("  python main.py visualize --file data/earthquakes.csv --output plots/")
        print("  python main.py report --file data/earthquakes.csv --output report.txt")
        print("  python main.py sample --count 500 --output data/sample.csv")
        print("  python main.py info")
        sys.exit(0)

    args.func(args)


if __name__ == '__main__':
    main()
