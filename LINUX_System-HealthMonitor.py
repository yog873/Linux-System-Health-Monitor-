# Linux-System-Health-Monitor-

Built a Linux System Health Monitor -

Project Description -
The Linux System Health Monitor is a Python-based system administration utility designed to monitor important operating-system resources 
and provide a quick view of system health.

---The project was developed and tested using Ubuntu under WSL.

Through :
- Python • Linux • WSL • psutil - 


LINUX System Health Monitor - Project Architecture - 

                    LINUX SYSTEM
                         │
                         ▼
                PYTHON MONITOR
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
      CPU              MEMORY             DISK
       │                 │                 │
       └─────────────────┼─────────────────┘
                         ▼
                  HEALTH ENGINE
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
        CPU PROCESSES         MEMORY PROCESSES
              │                     │
              └──────────┬──────────┘
                         ▼
                 SERVICE MONITOR
                         │
                         ▼
                NETWORK + UPTIME
                         │
                         ▼
                     LOGGING
                         │
                         ▼
                  HEALTH REPORT


*Python 
  Code : 

import psutil
import subprocess
import time
import logging


# ==============================
# Configuration
# ==============================

CPU_WARNING = 80
CPU_CRITICAL = 90

MEMORY_WARNING = 80
MEMORY_CRITICAL = 90

DISK_WARNING = 80
DISK_CRITICAL = 90

SERVICES_TO_MONITOR = [
    "systemd-journald"
]


# ==============================
# Logging
# ==============================

logging.basicConfig(
    filename="logs/system_monitor.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# ==============================
# Health Status
# ==============================

def get_status(usage, warning, critical):

    if usage < warning:
        return "OK"

    elif usage <= critical:
        return "WARNING"

    else:
        return "CRITICAL"

# ==============================
# Service Monitoring
# ==============================

def check_service(service_name):

    try:

        result = subprocess.run(
            ["systemctl", "is-active", service_name],
            capture_output=True,
            text=True
        )

        return result.stdout.strip()

    except Exception:

        return "unknown"


# ==============================
# Process Monitoring
# ==============================

def get_top_cpu_processes():

    processes = []

    for process in psutil.process_iter(
        ["pid", "name", "cpu_percent"]
    ):

        try:
            processes.append(process.info)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    processes.sort(
        key=lambda x: x["cpu_percent"] or 0,
        reverse=True
    )

    return processes[:5]


def get_top_memory_processes():

    processes = []

    for process in psutil.process_iter(
        ["pid", "name", "memory_percent"]
    ):

        try:
            processes.append(process.info)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    processes.sort(
        key=lambda x: x["memory_percent"] or 0,
        reverse=True
    )

    return processes[:5]


# ==============================
# Main Monitoring Function
# ==============================

def monitor_system():

    # CPU
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_status = get_status(
        cpu_usage,
        CPU_WARNING,
        CPU_CRITICAL
    )

    # Memory
    memory_usage = psutil.virtual_memory().percent
    memory_status = get_status(
        memory_usage,
        MEMORY_WARNING,
        MEMORY_CRITICAL
    )

    # Disk
    disk_usage = psutil.disk_usage("/").percent
    disk_status = get_status(
        disk_usage,
        DISK_WARNING,
        DISK_CRITICAL
    )

    # Overall health
    statuses = [
        cpu_status,
        memory_status,
        disk_status
    ]

    if "CRITICAL" in statuses:
        overall_status = "CRITICAL"

    elif "WARNING" in statuses:
        overall_status = "WARNING"

    else:
        overall_status = "HEALTHY"


    # ==============================
    # Display
    # ==============================

    print("\n========================================")
    print("        LINUX SYSTEM HEALTH MONITOR")
    print("========================================")

    print("\nSYSTEM RESOURCES")
    print("----------------------------------------")

    print(
        f"CPU Usage:     {cpu_usage:.1f}% "
        f"[{cpu_status}]"
    )

    print(
        f"Memory Usage:  {memory_usage:.1f}% "
        f"[{memory_status}]"
    )

    print(
        f"Disk Usage:    {disk_usage:.1f}% "
        f"[{disk_status}]"
    )


    # ==============================
    # Top CPU Processes
    # ==============================

    print("\nTOP CPU PROCESSES")
    print("----------------------------------------")

    for process in get_top_cpu_processes():

        print(
            f"PID: {process['pid']:<6} "
            f"CPU: {process['cpu_percent'] or 0:.1f}% "
            f"Name: {process['name']}"
        )


    # ==============================
    # Top Memory Processes
    # ==============================

    print("\nTOP MEMORY PROCESSES")
    print("----------------------------------------")

    for process in get_top_memory_processes():

        print(
            f"PID: {process['pid']:<6} "
            f"MEM: {process['memory_percent'] or 0:.1f}% "
            f"Name: {process['name']}"
        )


    # ==============================
    # Services
    # ==============================

    print("\nSERVICES")
    print("----------------------------------------")

    for service in SERVICES_TO_MONITOR:

        status = check_service(service)

        if status == "active":
            display_status = "RUNNING"

        elif status == "inactive":
            display_status = "STOPPED"

        else:
            display_status = status.upper()

        print(
            f"{service:<25} {display_status}"
        )


    # ==============================
    # Network
    # ==============================

    network = psutil.net_io_counters()

    sent_mb = network.bytes_sent / (1024 ** 2)
    received_mb = network.bytes_recv / (1024 ** 2)

    print("\nNETWORK")
    print("----------------------------------------")

    print(f"Bytes Sent:     {sent_mb:.2f} MB")
    print(f"Bytes Received: {received_mb:.2f} MB")


    # ==============================
    # Uptime
    # ==============================

    uptime_seconds = time.time() - psutil.boot_time()

    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)

    print("\nSYSTEM UPTIME")
    print("----------------------------------------")

    print(
        f"{days} days, "
        f"{hours} hours, "
        f"{minutes} minutes"
    )


    # ==============================
    # Overall Status
    # ==============================

    print("\n========================================")
    print(f"Overall Status: {overall_status}")
    print("========================================")


    # ==============================
    # Logging
    # ==============================

    logging.info(
        f"CPU={cpu_usage:.1f}% "
        f"Memory={memory_usage:.1f}% "
        f"Disk={disk_usage:.1f}% "
        f"Status={overall_status}"
    )


# ==============================
# Program Entry Point
# ==============================

#Step -15 Continuous Monitoring -=

if __name__ == "__main__":

    while True:

        monitor_system()

        print("\nNext check in 10 seconds...")
        print("Press Ctrl+C to stop.")

        time.sleep(10)


#Developed a Python-based Linux System Health Monitoring utility to automate basic system administration and troubleshooting tasks.

*Key features:

- CPU, memory, and disk utilization monitoring
- Configurable OK / WARNING / CRITICAL health thresholds
- Overall system health evaluation
- Top CPU- and memory-consuming process detection
- Linux service status monitoring using systemctl
- Network traffic statistics monitoring
- System uptime tracking
- Automated System Health logging
- Continuous Monitoring at configurable Intervals

- Technologies : Python 3, Linux/Ubuntu, WSL, psutil, systemctl, subprocess, logging, Git/GitHub.


Main Functions used and their Workings and Functions- 

1. CPU Monitoring

Uses:

psutil.cpu_percent(interval=1)
to measure CPU utilization.

Example:
CPU Usage: 12.4% [OK]


2. Memory Monitoring

Uses:
psutil.virtual_memory()

to retrieve system memory information.

The project uses:
memory.percent

to determine memory utilization.

Example:
Memory Usage: 48.2% [OK]



3. Disk Monitoring

Uses:
psutil.disk_usage("/")
to monitor disk utilization of the Linux root filesystem.

Example:
Disk Usage: 37.1% [OK]



 9. Health Threshold System -

The project evaluates resource utilization using three states:
   
Usage	Status
< 80%	OK
80–90%	WARNING
> 90%	CRITICAL

The thresholds are configurable at the top of the Python program.

Example:
CPU_WARNING = 80
CPU_CRITICAL = 90
Similar thresholds are defined for memory and disk.



 10. Overall System Health

The project doesn't simply report individual values.

It calculates an overall status.

Logic:
Any CRITICAL
      ↓
   CRITICAL

Otherwise, any WARNING
      ↓
    WARNING

Otherwise
      ↓
   HEALTHY

Example:

CPU       → OK
Memory    → WARNING
Disk      → OK

Overall   → WARNING
This gives an administrator a quick indication of whether the system requires attention.


  
11. CPU Process Monitoring

The project uses:
psutil.process_iter()
to inspect running processes.

It collects:
PID
Process name
CPU utilization

The processes are sorted by CPU usage to identify the top CPU-consuming processes.

Example:
TOP CPU PROCESSES

PID: 1234   CPU: 5.2%   Name: python3
PID: 5678   CPU: 2.1%   Name: bash
🧠 12. Memory Process Monitoring

The same concept is used for memory.
The program identifies the top processes based on memory utilization.

Example:
TOP MEMORY PROCESSES

PID: 1234   MEM: 4.2%   Name: python3
PID: 5678   MEM: 2.7%   Name: chrome

                        
Why this is useful -
If the system reports:
Memory Usage: 95%

an administrator can investigate:
Which processes are consuming the most memory?
                        

🖥️ 13. Linux Service Monitoring

The project uses:
systemctl

to inspect Linux services.

Python's:
subprocess
module executes:

systemctl is-active <service>
The program then reports the service state.

Example:
SERVICES

systemd-journald          RUNNING
Concepts demonstrated
Linux services
systemd
systemctl
Python subprocess automation


                        
 14. Network Monitoring -

The project uses:
psutil.net_io_counters()

to obtain network I/O statistics.

It reports:
Bytes Sent
Bytes Received

Example:
NETWORK

Bytes Sent:     120.45 MB
Bytes Received: 850.32 MB
                        
                        
 15. System Uptime

The project calculates system uptime using:
psutil.boot_time()

and the current time.
The result is displayed as:

SYSTEM UPTIME
0 days, 8 hours, 42 minutes

Uptime is useful when Troubleshooting system restarts and availability.

                        
 16. Logging -

The project uses Python's:

logging

module.

Monitoring results are stored in:

logs/system_monitor.log

Example:

2026-08-30 10:30:21 - INFO -
CPU=12.3% Memory=48.2% Disk=37.1% Status=HEALTHY
Why logging matters

Instead of only seeing the current status, an administrator can maintain a record of previous monitoring checks.
                        

 17. Continuous Monitoring -

The program can repeatedly execute monitoring checks.

Conceptually:

Start
  ↓
Collect metrics
  ↓
Analyze health
  ↓
Display report
  ↓
Log results
  ↓
Wait
  ↓
Repeat

The current implementation uses a Monitoring Interval of 10 seconds.

It can be stopped using:
Ctrl + C

                        
18. Linux Commands that I've Practiced -

This is actually something I'd highlight in your GitHub README.

-Process management
-ps
-ps aux
-CPU/process investigation
-ps aux --sort=-%cpu
-Memory/process investigation
-ps aux --sort=-%mem
-Memory
-free -h
-Disk
-df -h
-Services
-systemctl
-systemctl status
-systemctl is-active
-Networking

 also explored Linux networking utilities such as:
ip
ss

These commands helped you understand what the Python monitoring program was automating.

 19. Technology Stack

Put this in your GitHub README:

Language:
Python 3

Operating System:
Ubuntu Linux

Environment:
WSL (Windows Subsystem for Linux)

Libraries:
psutil

Python Modules:
subprocess
logging
time

Linux Tools:
ps
systemctl
free
df
ip
ss

Version Control:
Git / GitHub

To Stop continuous monitoring:
Ctrl + C

                        
📊 Output of Project : 
========================================
        LINUX SYSTEM HEALTH MONITOR
========================================

SYSTEM RESOURCES
----------------------------------------
CPU Usage:     8.4% [OK]
Memory Usage:  45.7% [OK]
Disk Usage:    32.1% [OK]

TOP CPU PROCESSES
----------------------------------------
PID: 1234   CPU: 1.2% Name: python3
PID: 88     CPU: 0.1% Name: systemd-udevd

TOP MEMORY PROCESSES
----------------------------------------
PID: 1234   MEM: 4.2% Name: python3
PID: 88     MEM: 0.8% Name: systemd

SERVICES
----------------------------------------
systemd-journald          RUNNING

NETWORK
----------------------------------------
Bytes Sent:     120.45 MB
Bytes Received: 850.32 MB

SYSTEM UPTIME
----------------------------------------
0 days, 8 hours, 42 minutes

========================================
Overall Status: HEALTHY
========================================


**Learning Insights from this Project : 

This is arguably more important than the Feature List -

Linux

I learned the Core Fundamental Concepts in:

-Linux filesystem/environment basics
-Processes
-PIDs
-CPU utilization
-Memory utilization
-Disk utilization
-Linux services
-systemd/systemctl
-Network statistics
-System uptime
-Basic troubleshooting concepts
-Python

with this I practiced manually and Understood how the LINUX System works, monitor CPU, memory, disk, processes, services, network statistics, and system uptime, to evaluate resource Health using configurable thresholds, and records Monitoring Results through Logging. 

Functions -
-Variables
-Conditional statements
-Loops
-Lists
-Sorting
-Exception handling
-psutil
-subprocess
-logging
-Continuous execution
-System Administration

Practised Architecture: 
                        
Monitor
   ↓
Identify abnormal resource usage
   ↓
Find responsible processes
   ↓
Check services
   ↓
Record system state
   ↓
Repeat monitoring

That's the enitre story about my LINUX System Project.

                        *** Use - Understand the Core Linux Concepts ->>> Implement and Create new Solutions ***
                                                    Learn - Code - Enjoy:)
                                                     ---  Thank you!  ---
                                
                        
