import { configManager } from "./config_loader";

export class InquiryConfigDriven {
  generateQuestion(fieldName: string): string {
    return configManager.getQuestion(fieldName);
  }
}
