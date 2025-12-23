
export class CategoryRepository {
    constructor() {
        console.log("[CategoryRepository] Initialized (Empty State)");
    }

    public getAllCategories(): any[] {
        return [];
    }

    public findCategoryByName(name: string): any | undefined {
        return undefined;
    }
}
