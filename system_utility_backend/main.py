from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from supabase import Client, create_client
import datetime
import json
import io
import csv
from fastapi.responses import StreamingResponse

app = FastAPI(title="System Utility Backend")

# ---------------- Supabase Setup ----------------
SUPABASE_URL = "https://betlagfewgcpvcxjjurc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJldGxhZ2Zld2djcHZjeGpqdXJjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYwMTk2NjMsImV4cCI6MjA3MTU5NTY2M30.5mGPCG8cCARurPLOAPXS66vfAkGr2Z_fVfj8HX9S5zE"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev; restrict to ["http://localhost:3000"] later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Routes ----------------
@app.get("/")
def root():
    return {"message": "System Utility Backend is running!"}

@app.post("/report")
async def report(request: Request):
    data = await request.json()
    data["reported_at"] = datetime.datetime.utcnow().isoformat()

    print("\n===== New Report Received =====")
    print("Time:", datetime.datetime.now())
    print(json.dumps(data, indent=4))
    print("==============================\n")

    insert_data = {
        "machine_id": data.get("machine_id"),
        "system": data.get("system"),
        "release": data.get("release"),
        "version": data.get("version"),
        "arch": data.get("arch"),
        "checked_at": data.get("checked_at"),
        "disk_encryption": data.get("checks", {}).get("disk_encryption"),
        "os_update": data.get("checks", {}).get("os_update"),
        "antivirus": data.get("checks", {}).get("antivirus"),
        "inactivity_sleep": data.get("checks", {}).get("inactivity_sleep"),
        "reported_at": data.get("reported_at")
    }

    try:
        resp = supabase.table("systems").upsert(insert_data, on_conflict="machine_id").execute()
        print("Supabase insert response:", resp.data)
    except Exception as e:
        print("Supabase insert exception:", e)

    return {"status": "success", "received_at": str(datetime.datetime.now())}

# ---------- List all machines (latest status) ----------
@app.get("/machines")
def list_machines():
    try:
        resp = supabase.table("systems").select("*").order("reported_at", desc=True).execute()
        machines = resp.data or []
        return machines
    except Exception as e:
        return {"error": str(e)}

# ---------- Filter machines ----------
@app.get("/machines/filter")
def filter_machines(
    os: str | None = Query(None),
    outdated: bool | None = Query(None),
    unencrypted: bool | None = Query(None),
):
    try:
        query = supabase.table("systems").select("*")

        if os:
            query = query.eq("system", os)
        if outdated is not None:
            query = query.eq("os_update->>up_to_date", str(not outdated).lower())
        if unencrypted is not None:
            query = query.eq("disk_encryption->>status", str(not unencrypted).lower())

        resp = query.order("reported_at", desc=True).execute()
        return resp.data
    except Exception as e:
        return {"error": str(e)}

# ---------- Export CSV ----------
@app.get("/machines/export")
def export_machines():
    try:
        resp = supabase.table("systems").select("*").order("reported_at", desc=True).execute()
        machines = resp.data or []

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["machine_id", "system", "release", "arch", "reported_at"])

        for m in machines:
            writer.writerow([
                m.get("machine_id"),
                m.get("system"),
                m.get("release"),
                m.get("arch"),
                m.get("reported_at")
            ])

        output.seek(0)
        return StreamingResponse(output, media_type="text/csv", headers={
            "Content-Disposition": "attachment; filename=machines.csv"
        })
    except Exception as e:
        return {"error": str(e)}
