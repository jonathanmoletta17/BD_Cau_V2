
import { AssetService } from '../src/services/asset_service';

async function unitTestAssetService() {
    console.log("--- Unit Testing AssetService ---");
    const service = new AssetService();

    const TEST_IP = "10.72.16.203";
    console.log(`Lookup IP: ${TEST_IP}`);

    try {
        const result = await service.identifyByIP(TEST_IP);

        if (result) {
            console.log("\n✅ SUCCESS: Asset Identified");
            console.log(JSON.stringify(result, null, 2));

            if (result.serial === 'PE0A2KN3') {
                console.log("Serial Verified.");
            } else {
                console.log("❌ Serial Mismatch.");
            }
        } else {
            console.log("\n❌ FAILED: Asset returned null.");
        }

    } catch (e: any) {
        console.error("\n❌ EXCEPTION:", e);
    }
}

unitTestAssetService();
