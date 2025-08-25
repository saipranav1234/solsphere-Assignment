import axios from "axios";

const API_BASE = "http://127.0.0.1:8001";

export async function fetchMachines() {
  const res = await axios.get(`${API_BASE}/machines`);
  return res.data;
}

export async function filterMachines(filters: { os?: string; outdated?: boolean; unencrypted?: boolean }) {
  const params = new URLSearchParams();
  if (filters.os) params.append("os", filters.os);
  if (filters.outdated !== undefined) params.append("outdated", String(filters.outdated));
  if (filters.unencrypted !== undefined) params.append("unencrypted", String(filters.unencrypted));

  const res = await axios.get(`${API_BASE}/machines/filter?${params.toString()}`);
  return res.data;
}

export async function exportMachinesCSV() {
  const res = await axios.get(`${API_BASE}/machines/export`, {
    responseType: "blob",
  });
  const url = window.URL.createObjectURL(new Blob([res.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", "machines.csv");
  document.body.appendChild(link);
  link.click();
}
