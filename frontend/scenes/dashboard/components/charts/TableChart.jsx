// scenes/dashboard/components/charts/TableChart.jsx
'use client';

import {
  Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper
} from '@mui/material';

export default function TableChart({ data, columns }) {
  // data가 배열인지 확인
  if (!Array.isArray(data) || !Array.isArray(columns) || data.length === 0) return null;

  const slicedData = data.slice(0, 9); // 상위 9개만 표시

  return (
    <TableContainer component={Paper}>
      <Table size="small">
        <TableHead>
          <TableRow>
            {columns.map((col, idx) => (
              <TableCell key={idx}>{col}</TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {slicedData.map((row, rowIndex) => (
            <TableRow key={rowIndex}>
              {columns.map((col, colIndex) => (
                <TableCell key={colIndex}>{row[col]}</TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
