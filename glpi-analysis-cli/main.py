import argparse
import os
import logging
from dotenv import load_dotenv
from src.loader import DataLoader
from src.analyzer import DataAnalyzer
from src.reporter import Reporter

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GLPI-Analyst")

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="GLPI Data Analyst CLI")
    parser.add_argument("query", nargs="?", help="Natural language query for analysis")
    parser.add_argument("--export", action="store_true", help="Run data export first")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    # Export Step
    if args.export:
        logger.info("Running data export...")
        try:
            from exporter import fetch_data, save_by_year
            df = fetch_data()
            save_by_year(df)
            logger.info("Export finished.")
        except ImportError:
            logger.error("exporter.py not found or dependencies missing.")
            return
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return
        # If only exporting, stop here
        if not args.query and not args.interactive:
            return

    # Initialization
    base_path = os.path.join(os.getcwd(), "glpi-analysis-cli")
    # If running from inside the folder, adjust path
    if not os.path.exists(os.path.join(base_path, "dados_2023.csv")):
        base_path = os.getcwd() # Try current dir
    
    try:
        loader = DataLoader(base_path)
        df = loader.load_data()
        
        analyzer = DataAnalyzer(df, loader.get_context_info())
        reporter = Reporter(os.path.join(base_path, "output"))
        
    except Exception as e:
        logger.critical(f"Initialization failed: {e}")
        return

    # Interaction Loop
    if args.interactive:
        print("Welcome to GLPI Analyst (Type 'exit' to quit)")
        while True:
            query = input("\nAnalysis Request > ")
            if query.lower() in ['exit', 'quit']:
                break
            if not query.strip():
                continue
                
            result = analyzer.analyze(query)
            reporter.print_result(query, result)
            reporter.save_log(query, result)
            
    elif args.query:
        result = analyzer.analyze(args.query)
        reporter.print_result(args.query, result)
        reporter.save_log(args.query, result)
    else:
        if not args.export:
            parser.print_help()

if __name__ == "__main__":
    main()
