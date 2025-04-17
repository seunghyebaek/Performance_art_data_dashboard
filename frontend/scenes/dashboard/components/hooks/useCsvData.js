// scenes/dashboard/components/hooks/useCsvData.js
import { useEffect, useState } from "react";

export default function useCsvData() {
  const [scenarioData, setScenarioData] = useState({});

  useEffect(() => {
    const loadJson = async () => {
      try {
        const fileMap = {
          audience: "/audience_tb.json",
          perfBar: "/공연별_실측_vs_예측.json",
          perfScatter: "/좌석수_vs_예측관객수.json",
          genrePerfAudience: "/장르별_공연작수_관객수.json",
          genreRevenueSales: "/장르별_매출_판매수.json",
          regionTop5: "/지역별_통계_TOP5.json",
          venue2023: "/공연시설_From2023.json",
          venue2024: "/공연시설_From2024.json",
          salesLine: "/판매_누적관객추이.json",
          salesScatter: "/판매_좌석수vs누적판매량.json",
          salesCompare: "/판매_실측vs예측비교.json",
          roiBep: "/roi_bep_data.json",
          roiHistogram: "/roi_histogram.json",
          bepBoxplot: "/bep_boxplot.json",
          predictedAudienceLine: "/예측_관객_추이_그래프.json",
          scatterPredicted: "/좌석수_vs_관객수_산점도.json",
          ticketWarningLine: "/예매_추이_비교_그래프.json",
          rocCurve: "/roc_curve_data.json",
          forecastAudience: "/forecast_audience_time_series.json"
        };

        const results = await Promise.all(
          Object.values(fileMap).map(path => fetch(path).then(res => res.json()))
        );

        const [
          audience,
          perfBar,
          perfScatter,
          genrePerfAudience,
          genreRevenueSales,
          regionTop5,
          venue2023,
          venue2024,
          salesLine,
          salesScatter,
          salesCompare,
          roiBep,
          roiHistogram,
          bepBoxplot,
          predictedAudienceLine,
          scatterPredicted,
          ticketWarningLine,
          rocCurve,
          forecastAudience
        ] = results;

        const forecastAudienceProcessed = forecastAudience.dates.map((date, idx) => ({
          date,
          predicted: forecastAudience.predicted_cumulative[idx],
          lower: forecastAudience.confidence_interval.lower[idx],
          upper: forecastAudience.confidence_interval.upper[idx]
        }));

        setScenarioData({
          "🔎 집계 시각화": [
            {
              chartType: "bar-line-combo",
              title: "장르별 공연작수 및 관객수",
              xField: "genre",
              yFields: ["performance_count", "audience"],
              data: genrePerfAudience,
            },
            {
              chartType: "bar-line-combo",
              title: "장르별 티켓매출액 및 티켓판매수",
              xField: "genre",
              yFields: ["ticket_revenue", "ticket_sales"],
              data: genreRevenueSales,
            },
            {
              chartType: "pie-multiple",
              title: "지역별 공연 통계 분석",
              pieFields: [
                { title: "공연건수 상위 5개 지역 비중", dataKey: "공연건수 상위 5개 지역", nameKey: "name" },
                { title: "상연횟수 상위 5개 지역 비중", dataKey: "상연횟수 상위 5개 지역", nameKey: "name" },
                { title: "총 티켓판매수 상위 5개 지역 비중", dataKey: "총 티켓판매수 상위 5개 지역", nameKey: "name" },
                { title: "티켓매출액 상위 5개 지역 비중", dataKey: "티켓매출액 상위 5개 지역", nameKey: "name" },
              ],
              data: regionTop5,
            },
            {
              chartType: "bar-line-combo",
              title: "2023년 규모별 공연건수 및 총티켓판매수",
              xField: "scale",
              yFields: ["performance_count", "total_ticket_sales"],
              data: venue2023,
            },
            {
              chartType: "bar-line-combo",
              title: "2024년 규모별 공연건수 및 총티켓판매수",
              xField: "scale",
              yFields: ["performance_count", "total_ticket_sales"],
              data: venue2024,
            },
          ],
          "🙋‍♀️ 관객 수 예측 – 기획 단계": [
            {
              chartType: "bar",
              title: "동일 장르 내 과거 공연 관객 수 비교",
              xField: "performance_name",
              yFields: ["actual", "predicted"],
              data: perfBar,
            },
            {
              chartType: "scatter",
              title: "좌석 수 대비 예측 관객 수",
              xField: "capacity",
              yField: "predicted_sales",
              categoryField: "genre",
              data: perfScatter,
            },
            {
              chartType: "line-band",
              title: "날짜별 예측 관객 곡선 (유사 공연)",
              xField: "date",
              yField: "predicted",
              band: { lower: "lower", upper: "upper" },
              data: forecastAudienceProcessed
            }
          ], 
          "🙋‍♂️ 관객 수 예측 – 판매 단계": [
            {
              chartType: "line-multiple-series",
              title: "일자별 누적 관객 추이 (공연별)",
              xField: "dates",
              yFields: ["actual_cumulative", "predicted_cumulative"],
              groupField: "performance_id",
              data: salesLine,
              options: {
                genreField: "genre",
                showMarketingEvents: true,
              }
            },
            {
              chartType: "scatter",
              title: "공연장 좌석 수 vs 누적 판매량",
              xField: "capacity",
              yField: "accumulated_sales",
              categoryField: "genre",
              data: salesScatter,
            },
            {
              chartType: "bar",
              title: "유사 공연 비교 바 차트",
              xField: "performance_name",
              yFields: ["actual", "predicted"],
              data: salesCompare,
            },
          ],
          "📊 손익 예측 – 기획 단계": [
            {
              chartType: "line",
              title: "ROI 변화 추이",
              xField: "performance_name",
              yFields: ["roi"],
              data: roiBep,
            },
            {
              chartType: "bar",
              title: "BEP (손익분기점) 비교",
              xField: "performance_name",
              yFields: ["bep"],
              data: roiBep,
            },
            {
              chartType: "histogram",
              title: "ROI 분포 (히스토그램)",
              xField: "range",
              yField: "count",
              data: roiHistogram,
            },
            {
              chartType: "boxplot",
              title: "BEP 분포 (박스플롯)",
              stats: bepBoxplot,
            }
          ],
          "📊 손익 예측 – 판매 단계": [
            {
              chartType: "line",
              title: "ROI 변화 추이 (판매 기준)",
              xField: "performance_name",
              yFields: ["roi"],
              data: roiBep,
            },
            {
              chartType: "bar",
              title: "BEP (손익분기점) 비교 (판매 기준)",
              xField: "performance_name",
              yFields: ["bep"],
              data: roiBep,
            },
            {
              chartType: "scatter",
              title: "좌석 수 vs 예측 관객 수 산점도",
              xField: "capacity",
              yField: "predicted_sales",
              categoryField: "genre",
              data: scatterPredicted,
            },
            {
              chartType: "multi-line",
              title: "예측 관객 추이 그래프 (Top 3 공연)",
              xField: "date",
              yFields: Object.keys(predictedAudienceLine[0] || {}).filter(k => k !== "date"),
              data: predictedAudienceLine,
            }
          ],
          "🚨 티켓 판매 위험 예측 – 판매 단계 조기 경보": [
            {
              chartType: "table",
              title: "과거 공연 리스트 테이블",
              columns: ["performance_name", "booking_rate", "risk_level"],
              data: audience,
            },
            {
              chartType: "roc-curve",
              title: "ROC 및 PR Curve",
              xField: "fpr",
              yField: "tpr",
              data: rocCurve,
            },
            {
              chartType: "bar-line-combo",
              title: "예매 추이 비교 그래프",
              xField: "date",
              yFields: ["booking_rate", "target_booking_rate"],
              data: ticketWarningLine,
            }
          ]
        });
      } catch (err) {
        console.error("JSON 로딩 중 오류 발생:", err);
      }
    };

    loadJson();
  }, []);

  return scenarioData;
}