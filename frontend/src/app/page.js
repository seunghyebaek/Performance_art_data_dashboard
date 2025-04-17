// /src/app/page.js
'use client';

import { useState } from "react";
import dynamic from "next/dynamic";
import Sidebar from "../../scenes/global/Sidebar.jsx";
import { CssBaseline } from "@mui/material";

const Dashboard = dynamic(() => import("../../scenes/dashboard/index"), {
  ssr: false,
});

export default function App() {
  const [isSidebar, setIsSidebar] = useState(true);

  return (
    <>
      <CssBaseline />
      <div className="app">
        <Sidebar isSidebar={isSidebar} />
        <main className="content">
          <Dashboard />
        </main>
      </div>
    </>
  );
}