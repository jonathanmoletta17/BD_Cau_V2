import { ClassifierV2 } from '../services/classifier_v2';

async function testClassifier() {
    console.log("🚦 Starting ClassifierV2 Tests...\n");

    const classifier = new ClassifierV2();

    const scenarios = [
        "Meu mouse parou de funcionar",
        "Preciso de acesso ao FPE",
        "Minha impressora tá sem toner",
        "O wifi não conecta no meu celular"
    ];

    for (const input of scenarios) {
        console.log(`\n🧪 Testing Input: "${input}"`);
        try {
            const result = await classifier.classify(input);
            console.log("✅ Result:", JSON.stringify(result, null, 2));
        } catch (error) {
            console.error("❌ Error:", error);
        }
    }
}

testClassifier();
