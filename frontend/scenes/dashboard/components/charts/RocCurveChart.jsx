// scenes/dashboard/components/charts/RocCurveChart.jsx
'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

export default function RocCurveChart({ data, xField = 'fpr', yField = 'tpr' }) {
  if (!data || data.length === 0) return null;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xField} label={{ value: xField, position: 'insideBottom', offset: -5 }} />
        <YAxis label={{ value: yField, angle: -90, position: 'insideLeft' }} />
        <Tooltip />
        <Legend />
        <Line
          type="monotone"
          dataKey={yField}
          stroke="#ff7300"
          strokeWidth={2}
          name="ROC Curve"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
