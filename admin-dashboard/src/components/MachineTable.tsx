import { useEffect, useState } from "react";
import {
  fetchMachines,
  filterMachines,
  exportMachinesCSV,
} from "../api";
import {
  Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Paper, Button, Select, MenuItem, Typography, Chip
} from "@mui/material";

interface Machine {
  machine_id: string;
  system: string;
  release: string;
  arch: string;
  reported_at: string;
  disk_encryption?: any;
  os_update?: any;
  antivirus?: any;
}

export default function MachineTable() {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [osFilter, setOsFilter] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const loadMachines = async () => {
    setLoading(true);
    try {
      const data = await fetchMachines();
      setMachines(data);
    } finally {
      setLoading(false);
    }
  };

  const applyFilter = async () => {
    const data = await filterMachines({ os: osFilter });
    setMachines(data);
  };

  useEffect(() => {
    loadMachines();
  }, []);

  return (
    <Paper sx={{ padding: 2 }}>
      <Typography variant="h5" gutterBottom>
        Admin Dashboard
      </Typography>

      <div style={{ display: "flex", gap: "1rem", marginBottom: "1rem" }}>
        <Select
          value={osFilter}
          onChange={(e) => setOsFilter(e.target.value)}
          displayEmpty
        >
          <MenuItem value="">All OS</MenuItem>
          <MenuItem value="Windows">Windows</MenuItem>
          <MenuItem value="Darwin">MacOS</MenuItem>
          <MenuItem value="Linux">Linux</MenuItem>
        </Select>
        <Button variant="contained" onClick={applyFilter}>Apply Filter</Button>
        <Button variant="outlined" onClick={exportMachinesCSV}>Export CSV</Button>
      </div>

      {loading ? (
        <Typography>Loading...</Typography>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Machine ID</TableCell>
                <TableCell>OS</TableCell>
                <TableCell>Release</TableCell>
                <TableCell>Arch</TableCell>
                <TableCell>Last Check-in</TableCell>
                <TableCell>Encryption</TableCell>
                <TableCell>OS Update</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {machines.map((m) => (
                <TableRow key={m.machine_id}>
                  <TableCell>{m.machine_id}</TableCell>
                  <TableCell>{m.system}</TableCell>
                  <TableCell>{m.release}</TableCell>
                  <TableCell>{m.arch}</TableCell>
                  <TableCell>{new Date(m.reported_at).toLocaleString()}</TableCell>
                  <TableCell>
                    {m.disk_encryption?.status === "true" ? (
                      <Chip label="Encrypted" color="success" size="small" />
                    ) : (
                      <Chip label="Not Encrypted" color="error" size="small" />
                    )}
                  </TableCell>
                  <TableCell>
                    {m.os_update?.up_to_date === "true" ? (
                      <Chip label="Up-to-date" color="success" size="small" />
                    ) : (
                      <Chip label="Outdated" color="warning" size="small" />
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Paper>
  );
}
