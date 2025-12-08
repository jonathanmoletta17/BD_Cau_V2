import os
from datetime import datetime

class Reporter:
    def __init__(self, output_dir="output"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def print_result(self, query, result):
        print("\n" + "="*50)
        print(f"QUERY: {query}")
        print("-" * 50)
        print(f"RESULT:\n{result}")
        print("="*50 + "\n")

    def save_log(self, query, result):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_log_{timestamp}.txt"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Query: {query}\n\n")
            f.write(f"Result:\n{result}\n")
            
        return filepath
