import requests
from system_utility.main import get_system_report  
import datetime

API_ENDPOINT = "http://127.0.0.1:8001/report"  
API_KEY = "MY_TEST_API_KEY"

def report_results(results):
    headers = {"x-api-key": API_KEY}
    try:
        r = requests.post(API_ENDPOINT, json=results, headers=headers, timeout=10)
        print(f"{datetime.datetime.now()} - Reported results: {r.status_code}")
    except Exception as e:
        print(f"{datetime.datetime.now()} - Reporting failed: {e}")


def run_daemon():
    system_data = get_system_report()  
    system_data["checked_at"] = str(datetime.datetime.utcnow())
    report_results(system_data)


if __name__ == "__main__":
    run_daemon()
