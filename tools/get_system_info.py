import platform
import socket
import subprocess
import json
import datetime

def get_system_info():
    info = {
        "system": {},
        "hardware": {},
        "storage": {},
        "network": {},
        "monitors": [],
        "status": {}
    }
    
    # --- 1. System & OS ---
    info['system']['hostname'] = platform.node()
    info['system']['os_release'] = platform.release()
    info['system']['os_version'] = platform.version()
    info['system']['architecture'] = platform.machine()
    
    # Get simplified OS name/build via PowerShell for better readability
    try:
        cmd_os = 'powershell "Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, BuildNumber | ConvertTo-Json -Compress"'
        res_os = subprocess.check_output(cmd_os, shell=True).decode().strip()
        os_data = json.loads(res_os)
        info['system']['os'] = os_data.get('Caption')
        info['system']['build'] = str(os_data.get('BuildNumber'))
    except Exception:
        info['system']['os'] = f"Windows {platform.release()}"

    # --- 2. Network (IP) ---
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            s.connect(('10.254.254.254', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        info['network']['ip'] = IP
    except Exception as e:
        info['network']['ip'] = "Unknown"

    # --- 3. Hardware (Serial & CPU) ---
    try:
        cmd_hardware = 'powershell "Get-CimInstance Win32_BIOS | Select-Object SerialNumber | ConvertTo-Json -Compress"'
        res_hw = subprocess.check_output(cmd_hardware, shell=True).decode().strip()
        hw_data = json.loads(res_hw)
        info['hardware']['serial_number'] = hw_data.get('SerialNumber')
    except Exception as e:
        info['hardware']['serial_number'] = "Unknown"

    # --- 4. Storage (C: Drive & SMART) ---
    try:
        # C: Drive Space - Use Where-Object to avoid complex nesting quotes in Filter
        cmd_disk = 'powershell "Get-CimInstance Win32_LogicalDisk | Where-Object { $_.DeviceID -eq \'C:\' } | Select-Object Size, FreeSpace | ConvertTo-Json -Compress"'
        res_disk = subprocess.check_output(cmd_disk, shell=True).decode().strip()
        disk_data = json.loads(res_disk)
        
        total_gb = round(disk_data.get('Size', 0) / (1024**3), 2)
        free_gb = round(disk_data.get('FreeSpace', 0) / (1024**3), 2)
        # Avoid division by zero
        if total_gb > 0:
            percent_free = round((free_gb / total_gb) * 100, 1)
        else:
            percent_free = 0
        
        info['storage'] = {
            "drive": "C:",
            "total_gb": total_gb,
            "free_gb": free_gb,
            "percent_free": percent_free
        }
    except Exception as e:
        info['storage'] = {"error": str(e)}

    # SMART Status (Basic check - might require Admin)
    try:
        cmd_smart = 'powershell "Get-PhysicalDisk | Select-Object FriendlyName, MediaType, HealthStatus | ConvertTo-Json -Compress"'
        # This often returns a list
        res_smart = subprocess.run(cmd_smart, shell=True, capture_output=True, text=True)
        if res_smart.returncode == 0 and res_smart.stdout.strip():
            smart_data = json.loads(res_smart.stdout)
            if isinstance(smart_data, dict): smart_data = [smart_data]
            # Just verify if any disk is NOT 'Healthy'
            unhealthy = [d for d in smart_data if d.get('HealthStatus') != 'Healthy']
            info['storage']['smart_status'] = "Warning" if unhealthy else "OK"
            info['storage']['disks'] = smart_data
        else:
             info['storage']['smart_status'] = "Unknown"
    except Exception:
         info['storage']['smart_status'] = "Unknown"

    # --- 5. Uptime ---
    try:
        # Calculate uptime in days
        cmd_uptime = 'powershell "(Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime | Select-Object Days, Hours | ConvertTo-Json -Compress"'
        res_uptime = subprocess.check_output(cmd_uptime, shell=True).decode().strip()
        uptime_data = json.loads(res_uptime)
        info['status']['uptime_days'] = uptime_data.get('Days', 0)
        info['status']['uptime_hours'] = uptime_data.get('Hours', 0)
    except Exception:
        info['status']['uptime'] = "Unknown"

    # --- 6. Battery ---
    try:
        cmd_batt = 'powershell "Get-CimInstance Win32_Battery | Select-Object DesignCapacity, FullChargeCapacity, EstimatedChargeRemaining | ConvertTo-Json -Compress"'
        res_batt = subprocess.run(cmd_batt, shell=True, capture_output=True, text=True)
        if res_batt.returncode == 0 and res_batt.stdout.strip():
            batt_data = json.loads(res_batt.stdout)
            if isinstance(batt_data, list): batt_data = batt_data[0] # Assume one battery usually
            
            design = batt_data.get('DesignCapacity', 0)
            full = batt_data.get('FullChargeCapacity', 0)
            
            # Some drivers return 0 or null
            if design and full:
                 health_pct = round((full / design) * 100, 1)
                 info['hardware']['battery_health_percent'] = health_pct
                 info['hardware']['battery_charge_percent'] = batt_data.get('EstimatedChargeRemaining')
            else:
                 info['hardware']['battery'] = "No Design/Full Capacity data"
        else:
             info['hardware']['battery'] = "Not Detected (Desktop?)"
    except Exception:
        info['hardware']['battery'] = "Error reading"

    # --- 7. Monitors (Previous Logic) ---
    ps_script_mon = r"""
    try {
        $monitors = Get-CimInstance -Namespace root\wmi -ClassName WmiMonitorID -ErrorAction Stop
        $monitors | ForEach-Object {
            $man = if ($_.ManufacturerName) { [System.Text.Encoding]::ASCII.GetString($_.ManufacturerName).Trim([char]0) } else { 'Unknown' }
            $model = if ($_.UserFriendlyName) { [System.Text.Encoding]::ASCII.GetString($_.UserFriendlyName).Trim([char]0) } else { 'Unknown' }
            $ser = if ($_.SerialNumberID) { [System.Text.Encoding]::ASCII.GetString($_.SerialNumberID).Trim([char]0) } else { 'Unknown' }
            
            @{
                Manufacturer = $man
                Model = $model
                SerialNumber = $ser
            }
        } | ConvertTo-Json -Compress
    } catch {
        Write-Output "[]"
    }
    """
    try:
        cmd_monitors = ["powershell", "-NoProfile", "-Command", ps_script_mon]
        result = subprocess.run(cmd_monitors, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            try:
                monitors_data = json.loads(result.stdout.strip())
                if isinstance(monitors_data, dict): monitors_data = [monitors_data]
                elif monitors_data is None: monitors_data = []
                info['monitors'] = monitors_data
            except json.JSONDecodeError:
                 info['monitors'] = []
        else:
             info['monitors'] = []

    except Exception:
        info['monitors'] = []

    # --- 8. Security (Defender) ---
    try:
         # Check if Defender service is running
         cmd_sec = 'powershell "Get-Service WinDefend | Select-Object Status | ConvertTo-Json -Compress"'
         res_sec = subprocess.run(cmd_sec, shell=True, capture_output=True, text=True)
         if res_sec.returncode == 0 and res_sec.stdout.strip():
              sec_data = json.loads(res_sec.stdout)
              status = sec_data.get('Status') # 4 = Running usually
              info['status']['defender_active'] = (status == 4 or status == "Running")
         else:
              info['status']['defender_active'] = False
    except Exception:
         info['status']['defender_active'] = "Unknown"

    return info

if __name__ == "__main__":
    import pprint
    data = get_system_info()
    
    # Custom Pretty Print
    print("\n" + "="*50)
    print("      SYSTEM HEALTH & INVENTORY REPORT")
    print("="*50)
    
    print(f"\n[SYSTEM]")
    print(f"  Hostname   : {data['system'].get('hostname')}")
    print(f"  OS         : {data['system'].get('os')} (Build {data['system'].get('build')})")
    print(f"  Architecture: {data['system'].get('architecture')}")
    print(f"  Uptime     : {data['status'].get('uptime_days')} days, {data['status'].get('uptime_hours')} hours")
    
    print(f"\n[NETWORK]")
    print(f"  IP Address : {data['network'].get('ip')}")
    
    print(f"\n[HARDWARE]")
    print(f"  Serial No  : {data['hardware'].get('serial_number')}")
    if 'battery_health_percent' in data['hardware']:
        print(f"  Battery    : {data['hardware']['battery_health_percent']}% Health | {data['hardware']['battery_charge_percent']}% Charged")
    else:
        print(f"  Battery    : {data['hardware'].get('battery', 'N/A')}")
        
    print(f"\n[STORAGE C:]")
    storage = data.get('storage', {})
    print(f"  Total Size : {storage.get('total_gb')} GB")
    print(f"  Free Space : {storage.get('free_gb')} GB ({storage.get('percent_free')}%)")
    print(f"  SMART Status: {storage.get('smart_status')}")
    
    print(f"\n[SECURITY]")
    print(f"  WinDefender: {'Active' if data['status'].get('defender_active') else 'INACTIVE/Unknown'}")

    print(f"\n[MONITORS]")
    monitors = data.get('monitors', [])
    if monitors:
        for idx, mon in enumerate(monitors, 1):
            print(f"  #{idx} {mon.get('Manufacturer')} {mon.get('Model')} (SN: {mon.get('SerialNumber')})")
    else:
        print("  No monitors detected.")
        
    print("\n" + "="*50 + "\n")
