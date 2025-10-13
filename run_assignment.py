"""
Main Runner Script for Growth For Impact Assignment
Runs the complete data enrichment and job scraping process
"""

import os
import sys
import logging
import time
from datetime import datetime

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from data_enrichment import CompanyDataEnricher
from job_scraping import JobScraper
from validation import DataValidator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('assignment_log.txt'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AssignmentRunner:
    def __init__(self):
        self.excel_file = "E:/growth_for_impact_assignment/data/Growth For Impact Data Assignment.xlsx"
        self.start_time = datetime.now()
        
    def run_complete_assignment(self):
        """Run the complete assignment process"""
        logger.info("Starting Growth For Impact Assignment")
        logger.info(f"Start time: {self.start_time}")
        
        try:
            # Step 1: Data Enrichment
            logger.info("\n" + "="*50)
            logger.info("STEP 1: DATA ENRICHMENT")
            logger.info("="*50)
            self.run_data_enrichment()
            
            # Step 2: Job Scraping
            logger.info("\n" + "="*50)
            logger.info("STEP 2: JOB SCRAPING")
            logger.info("="*50)
            self.run_job_scraping()
            
            # Step 3: Data Validation
            logger.info("\n" + "="*50)
            logger.info("STEP 3: DATA VALIDATION")
            logger.info("="*50)
            self.run_data_validation()
            
            # Step 4: Generate Final Report
            logger.info("\n" + "="*50)
            logger.info("STEP 4: FINAL REPORT")
            logger.info("="*50)
            self.generate_final_report()
            
            end_time = datetime.now()
            duration = end_time - self.start_time
            logger.info(f"\nAssignment completed successfully!")
            logger.info(f"Total time: {duration}")
            
        except Exception as e:
            logger.error(f"Assignment failed: {e}")
            raise
    
    def run_data_enrichment(self):
        """Run data enrichment process"""
        logger.info("Starting data enrichment...")
        
        enricher = CompanyDataEnricher(self.excel_file)
        
        if enricher.load_data():
            # Process companies in batches to avoid overwhelming servers
            batch_size = 20
            total_companies = len(enricher.df)
            
            for start_idx in range(0, total_companies, batch_size):
                end_idx = min(start_idx + batch_size, total_companies)
                logger.info(f"Processing companies {start_idx} to {end_idx}")
                
                enricher.enrich_all_companies(start_idx, end_idx)
                enricher.save_progress()
                
                # Break between batches
                if end_idx < total_companies:
                    logger.info("Waiting 30 seconds before next batch...")
                    time.sleep(30)
            
            logger.info("Data enrichment completed")
        else:
            logger.error("Failed to load data for enrichment")
    
    def run_job_scraping(self):
        """Run job scraping process"""
        logger.info("Starting job scraping...")
        
        scraper = JobScraper(self.excel_file)
        
        if scraper.load_data() and scraper.setup_driver():
            # Process companies in smaller batches for job scraping
            batch_size = 10
            total_companies = len(scraper.df)
            
            for start_idx in range(0, total_companies, batch_size):
                end_idx = min(start_idx + batch_size, total_companies)
                logger.info(f"Scraping jobs for companies {start_idx} to {end_idx}")
                
                scraper.scrape_all_jobs(start_idx, end_idx)
                scraper.save_progress()
                
                # Break between batches
                if end_idx < total_companies:
                    logger.info("Waiting 60 seconds before next batch...")
                    time.sleep(60)
            
            scraper.close_driver()
            logger.info("Job scraping completed")
        else:
            logger.error("Failed to load data or setup driver for job scraping")
    
    def run_data_validation(self):
        """Run data validation process"""
        logger.info("Starting data validation...")
        
        validator = DataValidator(self.excel_file)
        
        if validator.load_data():
            validator.fix_common_issues()
            validation_results = validator.validate_all_data()
            logger.info("Data validation completed")
        else:
            logger.error("Failed to load data for validation")
    
    def generate_final_report(self):
        """Generate final assignment report"""
        logger.info("Generating final report...")
        
        try:
            import pandas as pd
            df = pd.read_excel(self.excel_file)
            
            # Calculate statistics
            total_companies = len(df)
            companies_with_websites = df['Website URL'].notna().sum()
            companies_with_linkedin = df['Linkedin URL'].notna().sum()
            companies_with_careers = df['Careers Page URL'].notna().sum()
            companies_with_job_listings = df['Job listings page URL'].notna().sum()
            
            # Count job postings
            total_jobs = 0
            for i in range(1, 4):
                job_urls = df[f'job post{i} URL'].notna().sum()
                total_jobs += job_urls
            
            # Generate report
            report = f"""
FINAL ASSIGNMENT REPORT
========================

Data Enrichment Results:
- Total companies processed: {total_companies}
- Companies with websites: {companies_with_websites} ({companies_with_websites/total_companies*100:.1f}%)
- Companies with LinkedIn: {companies_with_linkedin} ({companies_with_linkedin/total_companies*100:.1f}%)
- Companies with careers pages: {companies_with_careers} ({companies_with_careers/total_companies*100:.1f}%)
- Companies with job listings: {companies_with_job_listings} ({companies_with_job_listings/total_companies*100:.1f}%)

Job Scraping Results:
- Total job postings found: {total_jobs}
- Target: 200 job postings
- Status: {'TARGET ACHIEVED' if total_jobs >= 200 else 'TARGET NOT MET'}

Assignment Status: {'COMPLETED SUCCESSFULLY' if total_jobs >= 200 else 'NEEDS MORE WORK'}

Output File: {self.excel_file}
Log File: assignment_log.txt
"""
            
            logger.info(report)
            
            # Save report to file
            with open('final_report.txt', 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info("Final report saved to 'final_report.txt'")
            
        except Exception as e:
            logger.error(f"Error generating final report: {e}")

def main():
    """Main function"""
    print("Growth For Impact Assignment Runner")
    print("=" * 50)
    print("This script will automatically:")
    print("1. Enrich company data (websites, LinkedIn, careers pages)")
    print("2. Scrape job postings from career pages")
    print("3. Validate all data and links")
    print("4. Generate final report")
    print("=" * 50)
    
    response = input("\nDo you want to start the assignment? (y/n): ")
    if response.lower() != 'y':
        print("Assignment cancelled.")
        return
    
    runner = AssignmentRunner()
    runner.run_complete_assignment()

if __name__ == "__main__":
    main()
