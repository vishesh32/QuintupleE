import React from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';

export default function DeferrableTable({data}: any) {
    return (
        <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell>Day</TableCell>
              <TableCell align="right">Demand Type</TableCell>
              <TableCell align="right">Energy Supplied</TableCell>
              <TableCell align="right">Energy To Supply</TableCell>
              <TableCell align="right">Window</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map((row: any) => (
              <TableRow
                key={row.name}
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                <TableCell component="th" scope="row">
                  {row.name}
                </TableCell>
                <TableCell align="right">{row.day}</TableCell>
                <TableCell align="right">{row.defType}</TableCell>
                <TableCell align="right">{row.energySupplied}</TableCell>
                <TableCell align="right">{row.energyToSupply}</TableCell>
                <TableCell align="right">{row.window}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    )
}