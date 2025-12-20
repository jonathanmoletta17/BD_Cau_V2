
import { PayloadMapper } from "../services/payload_mapper";

const mockPayload = {
    description: "My printer is broken",
    location: "2nd Floor"
};

const mockSystemInfo = {
    System: { Hostname: "TEST-PC", OS: "Windows 11" },
    Network: { IP: "10.72.16.3" },
    Hardware: { SerialNumber: "PE0A2QGW" }
};

console.log("--- Testing PayloadMapper Footer ---");
const result = PayloadMapper.mapToTicket("printer_issue", mockPayload, 1, mockSystemInfo);

console.log("\n[generated content start]");
console.log(result.content);
console.log("[generated content end]\n");

if (result.content.includes("N/S: PE0A2QGW<br>") && result.content.includes("IP: 10.72.16.3")) {
    console.log("✅ SUCCESS: Footer format matches requirements.");
} else {
    console.log("❌ FAILURE: Footer format incorrect.");
}
