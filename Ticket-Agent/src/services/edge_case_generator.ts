import { CategoryRepository } from '../repositories/category_repository';

export interface EdgeCaseTicket {
    name: string;
    content: string;
    urgency: number;
    itilcategories_id?: number;
    description_scenario: string;
}

export class EdgeCaseGenerator {
    private repo: CategoryRepository;

    constructor() {
        this.repo = new CategoryRepository();
    }

    /**
     * Generates a suite of edge case tickets for testing.
     */
    public generateEdgeCases(): EdgeCaseTicket[] {
        const cases: EdgeCaseTicket[] = [];
        const categories = this.repo.getAllCategories();
        
        // Scenario 1: Max Length Title (GLPI usually limits to 255)
        cases.push({
            name: "A".repeat(255),
            content: "Testing max length title (255 chars).",
            urgency: 3,
            description_scenario: "Max Length Title (255 chars)"
        });

        // Scenario 2: Title Exceeding Limit (Should be truncated or error)
        cases.push({
            name: "B".repeat(300),
            content: "Testing title exceeding limit (300 chars).",
            urgency: 3,
            description_scenario: "Title Exceeding Limit (300 chars)"
        });

        // Scenario 3: Large Content (e.g. 50KB text)
        cases.push({
            name: "Large Content Ticket",
            content: "Lorem ipsum ".repeat(5000), // ~60KB
            urgency: 1,
            description_scenario: "Large Content Payload (~60KB)"
        });

        // Scenario 4: Special Characters and SQL Injection attempts (benign)
        cases.push({
            name: "Special Chars & SQLi Test",
            content: "Testing: ' OR 1=1; -- <script>alert('xss')</script> 😊 ¥€$",
            urgency: 3,
            description_scenario: "Special Characters and Injection Vectors"
        });

        // Scenario 5: Valid Category Assignment (if categories exist)
        if (categories.length > 0) {
            const randomCat = categories[Math.floor(Math.random() * categories.length)];
            cases.push({
                name: `Category Test: ${randomCat.name}`,
                content: `Testing assignment to category ID ${randomCat.id}`,
                urgency: 3,
                itilcategories_id: randomCat.id,
                description_scenario: `Valid Category Assignment (${randomCat.name})`
            });
        }

        // Scenario 6: Invalid Category ID
        cases.push({
            name: "Invalid Category Test",
            content: "Testing assignment to non-existent category ID 999999",
            urgency: 3,
            itilcategories_id: 999999,
            description_scenario: "Invalid Category ID (999999)"
        });

        // Scenario 7: Max Urgency (GLPI uses 1-5 usually)
        cases.push({
            name: "Max Urgency Test",
            content: "Testing urgency 5",
            urgency: 5,
            description_scenario: "Max Urgency (5)"
        });

        return cases;
    }
}
