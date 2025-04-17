// scenes/dashboard/components/chartHelpers.js

import {
  BarChart, Bar,
  LineChart, Line,
  ScatterChart, Scatter,
  AreaChart, Area,
  PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer
} from 'recharts';

import { Box, Typography } from '@mui/material';
import TableChart from "./charts/TableChart";
import RocCurveChart from "./charts/RocCurveChart";

const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff7f50", "#a2d5f2", "#f7a072", "#b28dff"];

export function renderCharts(chartDataArray) {
  if (!Array.isArray(chartDataArray)) return null;

  return chartDataArray.map((chart, idx) => {
    const {
      chartType, title, xField, yField, yFields, band, data,
      categoryField, columns, pieFields, stats
    } = chart;

    return (
      <Box key={idx} mb={6}>
        <Typography variant="subtitle1" fontWeight="bold" mb={1}>
          {title}
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          {getChartComponent(
            chartType, data, xField, yField, yFields,
            band, categoryField, columns, pieFields, stats
          )}
        </ResponsiveContainer>
      </Box>
    );
  });
}

function getChartComponent(
  type, data, xField, yField, yFields,
  band, categoryField, columns, pieFields, stats
) {
  switch (type) {
    case 'bar':
      return (
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xField} />
          <YAxis />
          <Tooltip />
          <Legend />
          {(yFields || [yField]).map((field, idx) => (
            <Bar
              key={field}
              dataKey={field}
              fill={COLORS[idx % COLORS.length]}
              name={field === 'actual' ? '실제 관객 수' : field === 'predicted' ? '예측 관객 수' : field}
            />
          ))}
        </BarChart>
      );

    case 'line':
      return (
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xField} />
          <YAxis />
          <Tooltip />
          <Legend />
          {(yFields || [yField]).map((field, idx) => (
            <Line
              key={field}
              type="monotone"
              dataKey={field}
              stroke={COLORS[idx % COLORS.length]}
              strokeWidth={2}
            />
          ))}
        </LineChart>
      );

    case 'multi-line':
    case 'line-multiple-series':
      return (
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xField} />
          <YAxis />
          <Tooltip />
          <Legend />
          {(yFields || []).map((field, idx) => (
            <Line
              key={field}
              type="monotone"
              dataKey={field}
              stroke={COLORS[idx % COLORS.length]}
              strokeWidth={2}
              dot={false}
            />
          ))}
        </LineChart>
      );

    case 'line-band':
      return (
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xField} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Area
            type="monotone"
            dataKey={band.upper}
            stroke="#d0e0ff"
            fillOpacity={0.3}
            fill="#d0e0ff"
          />
          <Area
            type="monotone"
            dataKey={band.lower}
            stroke="#d0e0ff"
            fillOpacity={0.1}
            fill="#ffffff"
          />
          <Line type="monotone" dataKey={yField} stroke="#3366cc" strokeWidth={2} />
        </AreaChart>
      );

    case 'scatter':
      return (
        <ScatterChart>
          <CartesianGrid />
          <XAxis dataKey={xField} name={xField} />
          <YAxis dataKey={yField} name={yField} />
          <Tooltip cursor={{ strokeDasharray: '3 3' }} />
          <Legend />
          <Scatter name={categoryField || '데이터'} data={data} fill="#8884d8" />
        </ScatterChart>
      );

    case 'table':
      return <TableChart data={data} columns={columns} />;

    case 'roc-curve':
      return <RocCurveChart data={data} xField={xField} yField={yField} />;

    case 'bar-line-combo':
      return (
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xField} />
          <YAxis yAxisId="left" />
          <YAxis yAxisId="right" orientation="right" />
          <Tooltip />
          <Legend />
          <Bar yAxisId="left" dataKey={yFields[0]} fill="#8884d8" />
          <Line yAxisId="right" type="monotone" dataKey={yFields[1]} stroke="#ff0000" strokeWidth={2} />
        </BarChart>
      );

    case 'pie-multiple':
      return (
        <Box display="flex" flexWrap="wrap" gap={3} justifyContent="center">
          {pieFields.map((field, idx) => {
            const pieData = data[field.dataKey];
            return (
              <Box key={idx} width="220px" height="220px">
                <Typography variant="caption" align="center">{field.title}</Typography>
                <ResponsiveContainer width="100%" height="90%">
                  <PieChart>
                    <Tooltip />
                    <Pie
                      data={pieData}
                      dataKey="value"
                      nameKey={field.nameKey}
                      outerRadius={80}
                      label={({ name, percent }) =>
                        `${name} (${(percent * 100).toFixed(1)}%)`
                      }
                    >
                      {pieData.map((entry, i) => (
                        <Cell key={`cell-${i}`} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            );
          })}
        </Box>
      );

    case 'histogram':
      return (
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey={xField} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey={yField} fill={COLORS[0]} name="빈도수" />
        </BarChart>
      );

    case 'boxplot':
      if (!stats || !stats.min || !stats.max || !stats.q1 || !stats.q3 || !stats.median) return null;

      const boxData = [{ name: "BEP", ...stats }];
      return (
        <ResponsiveContainer width="100%" height={200}>
          <BarChart layout="vertical" data={boxData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" domain={[stats.min * 0.95, stats.max * 1.05]} />
            <YAxis type="category" dataKey="name" />
            <Tooltip />
            <Bar dataKey="median" fill={COLORS[2]} name="중앙값" />
          </BarChart>
        </ResponsiveContainer>
      );

    default:
      return null;
  }
}