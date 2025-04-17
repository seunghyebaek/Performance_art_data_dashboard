# backend/ModelPredictionModule/test_stats.py
import sys
import os
import pprint

# 프로젝트 루트(IntegratedCode)를 sys.path에 추가 (필요 시)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ModelPredictionModule.analysis_module import (
    get_genre_stats,
    get_regional_stats,
    get_venue_scale_stats
)

def main():
    print("=== 집계: 장르별 통계 ===")
    genre_stats = get_genre_stats()
    pprint.pprint(genre_stats)

    print("\n=== 집계: 지역별 통계 ===")
    regional_stats = get_regional_stats()
    pprint.pprint(regional_stats)

    print("\n=== 집계: 공연장 규모별 통계 ===")
    venue_scale_stats = get_venue_scale_stats()
    pprint.pprint(venue_scale_stats)

if __name__ == "__main__":
    main()
