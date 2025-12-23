
import { GlpiClient } from './glpi';
import { configManager } from '../config';

export interface AssetDetails {
    id: number;
    name: string;
    serial: string;
    model: string;
    locationId: number;
    os?: string;
    os_license?: string;
    ip?: string;
    network_adapter?: string;
    monitors_count?: number;
}

export class AssetService {
    private client: GlpiClient;

    constructor() {
        this.client = new GlpiClient(configManager.getGlpiConfig());
    }

    /**
     * Finds a computer by its IP Address.
     * Field 126 = IP in GLPI Computer Search Options.
     */
    async identifyByIP(ip: string): Promise<AssetDetails | null> {
        // Validation: Ignore localhost or empty
        if (!ip || ip === '::1' || ip === '127.0.0.1') return null;

        console.log(`[AssetService] Identifying Asset by IP: ${ip}`);

        try {
            await this.client.initSession();

            // Strategy: Traversal via NetworkName (Field 13 = IP, Field 21 = ID)
            const criteria = {
                criteria: [{ field: 13, searchtype: 'contains', value: ip }],
                forcedisplay: [21]
            };

            const searchResult = await this.client.request('search/NetworkName', 'GET', criteria);

            if (searchResult.totalcount === 0) {
                console.log(`[AssetService] No NetworkName found for IP ${ip}`);
                return null;
            }

            // Get first match
            const raw = searchResult.data[0];
            // Field 21 seems to be the NetworkPort ID (Parent) in this context, or GLPI quirks.
            // Debug showed value 2011, which matches the NetworkPort ID.
            const netPortId = raw['21'] || raw.id;

            if (!netPortId) return null;

            // Traversal: NetworkPort -> Computer
            // We skip fetching NetworkName because we apparently got the Port ID directly.
            const netPort = await this.client.request(`NetworkPort/${netPortId}`);
            if (netPort.itemtype !== 'Computer') return null;

            return await this.enrichAssetDetails(netPort.items_id);

        } catch (e: any) {
            console.error(`[AssetService] Identification failed: ${e.message}`);
            return null;
        } finally {
            await this.client.killSession();
        }
    }

    /**
     * Fetches detailed info for a regular Ticket Footer.
     */
    private async enrichAssetDetails(computerId: number): Promise<AssetDetails> {
        // Fetch Core
        const comp = await this.client.request(`Computer/${computerId}`);

        const details: AssetDetails = {
            id: comp.id,
            name: comp.name,
            serial: comp.serial,
            model: "Unknown", // Need Model lookup or search field
            locationId: comp.locations_id,
        };

        // Parallel Fetch for richness
        const [osItems, ports, monitors] = await Promise.allSettled([
            this.client.request(`Computer/${computerId}/Item_OperatingSystem`),
            this.client.request(`Computer/${computerId}/NetworkPort`),
            this.client.request(`Computer/${computerId}/Monitor`) // Direct link check
        ]);

        // 1. OS Info
        if (osItems.status === 'fulfilled' && osItems.value.length > 0) {
            // We need to resolve the name. usually it gives IDs.
            // For now, let's just indicate existence or raw ID. 
            // The Search API returns solved names (values), distinct GET returns IDs. 
            // To get names we'd need to fetch OperatingSystem table. 
            // Let's rely on what we have: License Key is directly here.
            details.os_license = osItems.value[0].licenseid;
            details.os = "Detected"; // Placeholder until we resolve IDs
        }

        // 2. Network Info
        if (ports.status === 'fulfilled' && ports.value.length > 0) {
            const primary = ports.value[0];
            details.network_adapter = primary.instantiation_type; // e.g. NetworkPortWifi
            // MAC is usually in the port details
            if (primary.mac) details.network_adapter += ` (${primary.mac})`;
        }

        // 3. Monitors
        if (monitors.status === 'fulfilled') {
            details.monitors_count = monitors.value.length;
        }

        return details;
    }

    /**
     * Format the details into a Markdown Footer
     */
    formatTicketFooter(details: AssetDetails): string {
        return `
---------------------------------------------------
🖥️ **Identificação Automática de Ativo**
**Hostname:** ${details.name}
**Serial:** ${details.serial}
**Rede:** ${details.network_adapter || 'N/A'}
**OS Key:** ${details.os_license || 'N/A'}
**Monitores:** ${details.monitors_count || 0} vinculados.
---------------------------------------------------
`;
    }
}
