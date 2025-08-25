import time
from system_utility.main import run_checks
from system_utility.reporter import report_results

def daemon_loop(interval=1800):  
    last_results = None
    while True:
        results = run_checks()
        if results != last_results:
            print("Change detected, reporting...")
            report_results(results)
            last_results = results
        else:
            print("No changes.")
        time.sleep(interval)

if __name__ == "__main__":
    print("Starting system utility daemon...")
    daemon_loop()
