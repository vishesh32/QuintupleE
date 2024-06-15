import React, { useEffect } from "react";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";
import { getAllDays, getDeferrableData } from "@/app/actions";

export default function DeferrableTable() {
  const [data, setData] = React.useState<DeferrableTableData[]>([]);

  const fetchData = async () => {
    const data = await getDeferrableTableData();
    setData(data);
  }

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <TableContainer component={Paper}>
      <Table sx={{ minWidth: 650 }} aria-label="simple table">
        <TableHead>
          <TableRow>
            <TableCell align="right">Day</TableCell>
            <TableCell align="right">Demand Type</TableCell>
            <TableCell align="right">Expected Energy Supplied</TableCell>
            <TableCell align="right">Actual Energy Supplied</TableCell>
            <TableCell align="right">Deferrable Amount</TableCell>
            <TableCell align="right">Ticks Left to Supply Demand</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((row: any) => (
            <TableRow
              key={row.name}
              sx={{ "&:last-child td, &:last-child th": { border: 0 } }}
            >
              {/* <TableCell component="th" scope="row">
                {row.name}
              </TableCell> */}
              <TableCell align="right">{row.day}</TableCell>
              <TableCell align="right">{row.defType}</TableCell>
              <TableCell align="right">{row.expSupplied}</TableCell>
              <TableCell align="right">{row.actSupplied}</TableCell>
              <TableCell align="right">{row.energyToSupply}</TableCell>
              <TableCell align="right">{row.ticksLeft}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

// 0 index = blue
// 1 index = grey
// 2 index = yellow
async function getDeferrableTableData() {
  var days = await getAllDays();

  var data: DeferrableTableData[] = [];

  if (days) {
    for (let day of days) {
      var expSum = [0, 0, 0];
      var actSum = [0, 0, 0];
      var ticks = await getDeferrableData(day.day);
      if (ticks) {
        for (let tick of ticks) {
          // blue/0 defferable
          if (
            tick["tick"] >= day["deferables"][0]["start"] &&
            tick["tick"] <= day["deferables"][0]["end"]
          ) {
            expSum[0] += tick["algo_blue_power"]*25;
            actSum[0] += tick["avg_blue_power"]*25;
            data.push({
              day: day.day,
              defType: "Blue",
              expSupplied: expSum[0],
              actSupplied: actSum[0],
              energyToSupply: day["deferables"][0]["energy"],
              ticksLeft: day["deferables"][0]["end"] - tick["tick"],
            });
          }

          // grey/1 defferable
          if (
            tick["tick"] >= day["deferables"][1]["start"] &&
            tick["tick"] <= day["deferables"][1]["end"]
          ) {
            expSum[1] += tick["algo_grey_power"]*25;
            actSum[1] += tick["avg_grey_power"]*25;
            data.push({
              day: day.day,
              defType: "Grey",
              expSupplied: expSum[1],
              actSupplied: actSum[1],
              energyToSupply: day["deferables"][1]["energy"],
              ticksLeft: day["deferables"][1]["end"] - tick["tick"],
            });
          }

          // yellow/2 defferable
          if (
            tick["tick"] >= day["deferables"][2]["start"] &&
            tick["tick"] <= day["deferables"][2]["end"]
          ) {
            expSum[2] += tick["algo_yellow_power"]*25;
            actSum[2] += tick["avg_yellow_power"]*25;
            data.push({
              day: day.day,
              defType: "Yellow",
              expSupplied: expSum[2],
              actSupplied: actSum[2],
              energyToSupply: day["deferables"][2]["energy"],
              ticksLeft: day["deferables"][2]["end"] - tick["tick"],
            });
          }
        }
      }
    }
  }

  return data;
}

interface DeferrableTableData {
  day: number;
  defType: string;
  expSupplied: number;
  actSupplied: number;
  energyToSupply: number;
  ticksLeft: number;
}
