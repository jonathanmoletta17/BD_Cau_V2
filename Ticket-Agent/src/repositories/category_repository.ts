import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export interface Category {
    id: number;
    name: string;
    completename: string;
    level: number;
    comment: string;
}

export interface Entity {
    id: number;
    name: string;
    completename: string;
}

export class CategoryRepository {
    private categories: Category[] = [];
    private entities: Entity[] = [];
    private dataPath: string;

    constructor(dataPath?: string) {
        this.dataPath = dataPath || path.resolve(__dirname, '../../data_harvest');
        this.loadData();
    }

    private loadData() {
        try {
            const catPath = path.join(this.dataPath, 'prod_categories.json');
            if (fs.existsSync(catPath)) {
                this.categories = JSON.parse(fs.readFileSync(catPath, 'utf-8'));
                console.log(`[CategoryRepository] Loaded ${this.categories.length} categories.`);
            } else {
                console.warn(`[CategoryRepository] Warning: ${catPath} not found.`);
            }

            const entPath = path.join(this.dataPath, 'prod_entities.json');
            if (fs.existsSync(entPath)) {
                this.entities = JSON.parse(fs.readFileSync(entPath, 'utf-8'));
                console.log(`[CategoryRepository] Loaded ${this.entities.length} entities.`);
            } else {
                console.warn(`[CategoryRepository] Warning: ${entPath} not found.`);
            }
        } catch (error) {
            console.error('[CategoryRepository] Error loading data:', error);
        }
    }

    public getAllCategories(): Category[] {
        return this.categories;
    }

    public findCategoryByName(name: string): Category | undefined {
        return this.categories.find(c => c.name.toLowerCase() === name.toLowerCase() || c.completename.toLowerCase().includes(name.toLowerCase()));
    }

    public getCategoryById(id: number): Category | undefined {
        return this.categories.find(c => c.id === id);
    }

    public getAllEntities(): Entity[] {
        return this.entities;
    }
}
