//scenes/dashboard/index.jsx
"use client";

import { useState, useRef } from "react";
import { Box, Typography, Button, Paper } from "@mui/material";
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import ChatPage from "../chat/index";
import dynamic from "next/dynamic";

const InsightChart = dynamic(() => import("./components/InsightChart"), { ssr: false });

const Dashboard = () => {
  const [insightDataFromChatGpt, setInsightDataFromChatGpt] = useState([]);
  const [structuredDataFromChatGpt, setStructuredDataFromChatGpt] = useState(null); 
  const [realInsightFromChatGpt, setRealInsightFromChatGpt] = useState(null); 
  const [aisearchFromChatGpt, setAIsearchFromChatGpt] = useState(null); 
  const insightRef = useRef();

  const handleDownloadPDF = async () => {
    if (!insightRef.current) return;
  
    const canvas = await html2canvas(insightRef.current, {
      scale: 2, // 해상도 증가
      useCORS: true
    });
  
    const imgData = canvas.toDataURL("image/png");
  
    const pdf = new jsPDF("p", "mm", "a4");
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
  
    const imgWidth = pdfWidth;
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
  
    let heightLeft = imgHeight;
    let position = 0;
  
    // 첫 페이지
    pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;
  
    while (heightLeft > 0) {
      position = position - pageHeight;
      pdf.addPage();
      pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
      heightLeft -= pageHeight;
    }
  
    pdf.save("insight-report.pdf");
  };
  

  const handleDummyClick = () => {
    const dummyChartData = [
      {
        chartType: "bar",
        title: "장르별 예상 관객 수 (Dummy)",
        xField: "genre",
        yFields: ["expected_audience"],
        data: [
          { genre: "뮤지컬", expected_audience: 30000 },
          { genre: "콘서트", expected_audience: 28000 },
          { genre: "연극", expected_audience: 15000 },
        ],
      },
      {
        chartType: "scatter",
        title: "좌석 수 vs 예상 관객 수 (Dummy)",
        xField: "capacity",
        yField: "expected_audience",
        categoryField: "genre",
        data: [
          { capacity: 600, expected_audience: 500, genre: "뮤지컬" },
          { capacity: 1200, expected_audience: 1000, genre: "콘서트" },
          { capacity: 400, expected_audience: 300, genre: "연극" },
        ],
      },
    ];
    setInsightDataFromChatGpt(dummyChartData);
  };

  return (
    <Box m="10px">
      {/* ChatGPT 연결 */}
      {/* if (typeof onUpdateInsights === "function") {
          onUpdateInsights(charts); } */}
      {/* .analysis_results.accumulated_sales_planning.predictions 부분 
          이걸 setInsightDataFromChatGpt(charts)로 실행하는 셈 */}
      <ChatPage onUpdateInsights={setInsightDataFromChatGpt} setStructruedData={setStructuredDataFromChatGpt} setPlanningSummary={setRealInsightFromChatGpt} setAISearchSummary={setAIsearchFromChatGpt}/>

      {/* PDF 다운로드 + Dummy 버튼 */}
      <Box display="flex" justifyContent="flex-end" alignItems="center" my={2} gap={2}>
        <Button
          onClick={handleDummyClick}
          sx={{ fontSize: "14px", fontWeight: "bold", padding: "10px 20px" }}
          variant="outlined"
        >
          🎯 Dummy Chart 테스트(AI 연동용)
        </Button>

        <Button
          onClick={handleDownloadPDF}
          sx={{ fontSize: "14px", fontWeight: "bold", padding: "10px 20px" }}
          variant="contained"
        >
          <DownloadOutlinedIcon sx={{ mr: "10px" }} />
          Download Reports
        </Button>
      </Box>

      {/* 인사이트 영역 */}
      <Paper ref={insightRef} elevation={3} sx={{ p: 3 }}>
        <Typography variant="h6" fontWeight="bold" mb={3}>
          Insight Report
        </Typography>
        <InsightChart externalData={insightDataFromChatGpt} externalStructredData={structuredDataFromChatGpt} realInsightFromChatGpt={realInsightFromChatGpt} aisearchFromChatGpt={aisearchFromChatGpt}/>
      </Paper>
    </Box>
  );
};

export default Dashboard;