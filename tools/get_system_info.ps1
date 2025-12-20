# Get-SystemInfo.ps1
# Collects detailed system information for Ticket Agent
# Returns JSON object

$ErrorActionPreference = "SilentlyContinue"

# Initialize Data Structure
$Info = @{
    System   = @{}
    Network  = @{}
    Hardware = @{}
    Storage  = @{}
    Security = @{}
    Monitors = @()
}

# --- 1. SYSTEM INFORMATION ---
try {
    $comp = Get-CimInstance Win32_ComputerSystem
    $os = Get-CimInstance Win32_OperatingSystem
    
    # Uptime Calculation
    $uptimeSpan = (Get-Date) - $os.LastBootUpTime
    $uptime = "{0} days, {1} hours, {2} minutes" -f $uptimeSpan.Days, $uptimeSpan.Hours, $uptimeSpan.Minutes

    $Info.System = @{
        Hostname     = $env:COMPUTERNAME
        OS           = $os.Caption
        Version      = $os.Version
        Build        = $os.BuildNumber
        Architecture = $os.OSArchitecture
        Uptime       = $uptime
        LastBoot     = $os.LastBootUpTime.ToString("yyyy-MM-dd HH:mm:ss")
        User         = $env:USERNAME
    }
}
catch {
    $Info.System.Error = $_.Exception.Message
}

# --- 2. NETWORK (Active Internet Interface) ---
try {
    # Find interface with default gateway (0.0.0.0/0)
    $route = Get-NetRoute -DestinationPrefix "0.0.0.0/0" -AddressFamily IPv4 | Select-Object -First 1
    if ($route) {
        $ipObj = Get-NetIPAddress -InterfaceIndex $route.InterfaceIndex -AddressFamily IPv4
        $Info.Network.IP = $ipObj.IPAddress
        $Info.Network.Interface = $ipObj.InterfaceAlias
    }
    else {
        # Fallback to first non-loopback
        $ip = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "Loopback*" -and $_.PrefixOrigin -ne "WellKnown" } | Select-Object -First 1
        $Info.Network.IP = if ($ip) { $ip.IPAddress } else { "127.0.0.1" }
        $Info.Network.Interface = if ($ip) { $ip.InterfaceAlias } else { "Loopback" }
    }
}
catch {
    $Info.Network.IP = "Unknown"
}

# --- 3. HARDWARE & BIOS ---
try {
    $bios = Get-CimInstance Win32_BIOS
    $Info.Hardware = @{
        SerialNumber = $bios.SerialNumber
        Manufacturer = $comp.Manufacturer
        Model        = $comp.Model
    }
}
catch {
    $Info.Hardware.SerialNumber = "Unknown"
}

# --- 4. STORAGE (C: Drive + SMART) ---
try {
    $disk = Get-CimInstance Win32_LogicalDisk | Where-Object { $_.DeviceID -eq 'C:' }
    
    # Try getting Physical Disk Health (SMART)
    $health = "Unknown"
    try {
        $physDisks = Get-PhysicalDisk | Where-Object { $_.DeviceID -eq 0 -or $_.DeviceId -eq $disk.DeviceId } # Best guess mapping
        if ($physDisks) {
            $unhealthy = $physDisks | Where-Object { $_.HealthStatus -ne 'Healthy' }
            $health = if ($unhealthy) { "Warning" } else { "OK" }
        }
    }
    catch {}

    if ($disk) {
        $totalGB = [math]::Round($disk.Size / 1GB, 2)
        $freeGB = [math]::Round($disk.FreeSpace / 1GB, 2)
        $percentFree = if ($totalGB -gt 0) { [math]::Round(($freeGB / $totalGB) * 100, 1) } else { 0 }
        
        $Info.Storage = @{
            Drive       = "C:"
            TotalGB     = $totalGB
            FreeGB      = $freeGB
            PercentFree = $percentFree
            SmartStatus = $health
        }
    }
}
catch {}

# --- 5. SECURITY (Antivirus) ---
try {
    # Requires Admin often, but try anyway
    $av = Get-CimInstance -Namespace root\SecurityCenter2 -ClassName AntivirusProduct
    $Info.Security.Antivirus = if ($av) { $av.displayName } else { "Not Detected (Check Permissions)" }
}
catch {
    $Info.Security.Antivirus = "Access Denied / Unknown"
}

# --- 6. MONITORS (PnP Fallback) ---
try {
    # Attempt 1: WmiMonitorID (Best detail, failed previously due to perms)
    $monitors = Get-CimInstance -Namespace root\wmi -ClassName WmiMonitorID -ErrorAction SilentlyContinue
    
    if ($monitors) {
        foreach ($m in $monitors) {
            $man = if ($m.ManufacturerName) { [System.Text.Encoding]::ASCII.GetString($m.ManufacturerName).Trim([char]0) } else { 'Unknown' }
            $model = if ($m.UserFriendlyName) { [System.Text.Encoding]::ASCII.GetString($m.UserFriendlyName).Trim([char]0) } else { 'Unknown' }
            $Info.Monitors += @{ Type = "WMI"; Manufacturer = $man; Model = $model }
        }
    }
    else {
        # Attempt 2: PnP Devices (Fallback)
        $pnpMonitors = Get-PnpDevice -Class Monitor -Status OK | Where-Object { $_.FriendlyName -ne 'Generic PnP Monitor' }
        if (-not $pnpMonitors) {
            # Even Generic is better than nothing if no others
            $pnpMonitors = Get-PnpDevice -Class Monitor -Status OK 
        }

        foreach ($pm in $pnpMonitors) {
            $Info.Monitors += @{
                Type       = "PnP"
                Model      = $pm.FriendlyName
                InstanceId = $pm.InstanceId
            }
        }
    }
}
catch {
    $Info.Monitors += @{ Error = "Failed to retrieve monitor info" }
}

# --- OUTPUT ---
$Info | ConvertTo-Json -Depth 5 -Compress
