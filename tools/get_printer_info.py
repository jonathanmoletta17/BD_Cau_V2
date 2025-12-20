import subprocess
import json
import platform
import socket
import datetime
import sys

def run_powershell_json(script):
    """Runs a PowerShell script and returns the parsed JSON."""
    command = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script]
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            return None, result.stderr.strip()
        
        output = result.stdout.strip()
        if not output:
            return None, "Empty output"
            
        try:
            data = json.loads(output)
            return data, None
        except json.JSONDecodeError:
            return None, f"JSON Decode Error. Output: {output[:100]}..."
            
    except Exception as e:
        return None, str(e)

def get_printer_diagnostics():
    info = {
        "timestamp": datetime.datetime.now().isoformat(),
        "hostname": platform.node(),
        "printers": [],
        "server_integration": {
            "target_server": "piratinipaeps02",
            "accessible": False,
            "details": {}
        },
        "issues": [],
        "suggestions": []
    }

    # --- 1. Collect Printers & Status ---
    # We use Get-Printer (available Win8+) and Win32_Printer for Default check
    ps_script_printers = r"""
    $ErrorActionPreference = "SilentlyContinue"
    
    # Get Default Printer Name
    $defaultName = (Get-CimInstance -ClassName Win32_Printer | Where-Object Default -eq $true).Name

    # Get All Printers
    $printers = Get-Printer | Select-Object Name, DriverName, PortName, Shared, Published, DeviceType, PrinterStatus, JobCount, ComputerName, Location, Type

    $printers | ForEach-Object {
        $isDefault = ($_.Name -eq $defaultName)
        $isNetwork = ($_.Type -eq "Connection" -or $_.Name -match "^\\\\")
        
        # Determine specific server if network
        $server = $null
        if ($_.ComputerName) { 
            $server = $_.ComputerName.Trim("\") 
        } elseif ($_.Name -match "^\\\\([^\\]+)\\") {
            $server = $Matches[1]
        }

        @{
            Name = $_.Name
            DriverName = $_.DriverName
            PortName = $_.PortName
            Shared = $_.Shared
            Published = $_.Published
            DeviceType = $_.DeviceType
            Status = "$($_.PrinterStatus)"   # Force string representation of Enum
            JobCount = $_.JobCount
            IsDefault = $isDefault
            IsNetwork = $isNetwork
            Server = $server
            Location = $_.Location
        }
    } | ConvertTo-Json -Compress
    """
    
    printers_data, err = run_powershell_json(ps_script_printers)
    
    if err:
        info['issues'].append(f"Failed to query printers: {err}")
    else:
        if isinstance(printers_data, dict):
            printers_data = [printers_data]
        elif printers_data is None:
            printers_data = []
            
        info['printers'] = printers_data

    # --- 2. Check Server Connectivity (piratinipaeps02) ---
    server_target = "piratinipaeps02"
    ps_script_server = f"""
    $server = "{server_target}"
    $ping = Test-Connection -ComputerName $server -Count 1 -Quiet
    $smb = Test-NetConnection -ComputerName $server -Port 445 -InformationLevel Quiet
    
    @{{
        Ping = $ping,
        SMB = $smb
    }} | ConvertTo-Json -Compress
    """
    
    server_data, err_srv = run_powershell_json(ps_script_server)
    if not err_srv and server_data:
        info['server_integration']['details'] = server_data
        if server_data.get('Ping') or server_data.get('SMB'):
            info['server_integration']['accessible'] = True
        else:
            info['server_integration']['accessible'] = False
            info['issues'].append(f"Print server {server_target} is unreachable (Ping: {server_data.get('Ping')}, SMB: {server_data.get('SMB')})")
            info['suggestions'].append(f"Check network connection or VPN. Verify if {server_target} is online.")
    else:
         info['server_integration']['details'] = {"error": err_srv}

    # --- 3. Analyze & Diagnose ---
    
    has_default = False
    piratini_printers = []
    
    for p in info['printers']:
        p_name = p.get('Name', 'Unknown')
        p_status = p.get('Status') # Could be int or string
        p_server = p.get('Server')
        
        # Check Default
        if p.get('IsDefault'):
            has_default = True
            
        # Check Server Mapping
        if p_server and p_server.lower() == server_target.lower():
            piratini_printers.append(p_name)
            
        # Check Status (PrinterStatus: 3=Idle, 4=Printing. 1=Other, 2=Unknown, 7=Offline, 2=Error often)
        # Note: PowerShell JSON serialization of Enums can sometimes be the int value or string name.
        # We'll handle common "bad" states.
        # Known Bad: Offline(7), Error(2), NotAvailable(13), NoToner(19)
        # Note: 'PrinterStatus' from Get-Printer is usually descriptive string in JSON if not cast to int, but let's be safe.
        
        status_str = str(p_status).lower()
        if 'offline' in status_str or p_status == 7:
            info['issues'].append(f"Printer '{p_name}' is OFFLINE.")
            info['suggestions'].append(f"Check power and network cable for '{p_name}'. If network printer, ensure IP is reachable.")
        elif 'error' in status_str or p_status == 2:
             info['issues'].append(f"Printer '{p_name}' is in ERROR state.")
             info['suggestions'].append(f"Check printer panel for '{p_name}' (paper jam, cover open).")

        if not p.get('DriverName'):
            info['issues'].append(f"Printer '{p_name}' has no driver information.")
            info['suggestions'].append(f"Reinstall drivers for '{p_name}'.")

        # Check Queue
        job_count = p.get('JobCount', 0)
        if job_count > 5:
             info['issues'].append(f"High queue count ({job_count}) on '{p_name}'.")
             info['suggestions'].append(f"Clear print queue for '{p_name}' or restart spooler.")

    if not info['printers']:
        info['issues'].append("No printers installed on this system.")
        info['suggestions'].append("Install a local printer or map a network printer.")
    elif not has_default:
        info['issues'].append("No default printer selected.")
        info['suggestions'].append("Set a default printer in Windows Settings.")

    if not piratini_printers and info['server_integration']['accessible']:
        # Server is up but no printers mapped
        info['issues'].append(f"No printers mapped from {server_target}.")
        info['suggestions'].append(f"Map printers from \\\\{server_target} if needed.")
    elif piratini_printers and not info['server_integration']['accessible']:
        info['issues'].append(f"Printers mapped from {server_target} but server unreachable.")
        info['suggestions'].append("You may not be able to print. Check VPN/Network.")

    return info

def print_report(data):
    print("\n" + "="*60)
    print("      PRINTER DIAGNOSTIC REPORT")
    print("="*60)
    
    print(f"\n[SUMMARY]")
    print(f"  Hostname: {data.get('hostname')}")
    print(f"  Total Printers: {len(data.get('printers', []))}")
    print(f"  Server ({data['server_integration']['target_server']}): {'ONLINE' if data['server_integration']['accessible'] else 'UNREACHABLE'}")
    
    print(f"\n[PRINTERS]")
    if not data['printers']:
        print("  No printers found.")
    else:
        print(f" {'':<1} {'Name':<40} | {'Status':<15} | {'Jobs':<5}")
        print("-" * 70)
        for p in data['printers']:
            name = p.get('Name', 'Unknown').strip()
            # Truncate long names for display
            disp_name = (name[:37] + '..') if len(name) > 39 else name
            
            status_tag = "OK"
            s_val = str(p.get('Status'))
            
            def_tag = "*" if p.get('IsDefault') else " "
            print(f" {def_tag} {disp_name:<40} | {s_val:<15} | {p.get('JobCount')}")
            if p.get('IsNetwork'):
                srv = p.get('Server')
                port = p.get('PortName')
                print(f"     -> Server: {srv} | Port: {port}")

    if data.get('issues'):
        print(f"\n[DETECTED ISSUES]")
        for issue in data['issues']:
            print(f"  [!] {issue}")

    if data.get('suggestions'):
        print(f"\n[SUGGESTIONS]")
        for sug in data['suggestions']:
            print(f"  -> {sug}")
            
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Printer Diagnostics Tool")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--save-log", action="store_true", help="Save report to file")
    args = parser.parse_args()

    info = get_printer_diagnostics()
    
    if args.json:
        print(json.dumps(info, indent=2))
    else:
        print_report(info)
        
    if args.save_log:
        log_file = f"printer_diag_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, 'w') as f:
            json.dump(info, f, indent=2)
        print(f"[Info] Log saved to {log_file}")
