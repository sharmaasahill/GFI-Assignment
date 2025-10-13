"""
Validation Script for Growth For Impact Assignment
Validates all scraped data and ensures quality
"""

import pandas as pd
import requests
import time
import logging
from urllib.parse import urlparse
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataValidator:
    def __init__(self, excel_file_path):
        self.excel_file_path = excel_file_path
        self.df = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def load_data(self):
        """Load the Excel file"""
        try:
            self.df = pd.read_excel(self.excel_file_path)
            logger.info(f"Loaded {len(self.df)} companies from Excel file")
            return True
        except Exception as e:
            logger.error(f"Error loading Excel file: {e}")
            return False
    
    def validate_url(self, url, url_type="URL"):
        """Validate if a URL is working"""
        if pd.isna(url) or not url:
            return False, "URL is empty"
        
        try:
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            response = self.session.get(url, timeout=10, allow_redirects=True)
            
            if response.status_code == 200:
                return True, "URL is working"
            else:
                return False, f"URL returned status code {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "URL timeout"
        except requests.exceptions.ConnectionError:
            return False, "Connection error"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def validate_company_data(self, row_index):
        """Validate data for a single company"""
        company_name = self.df.iloc[row_index]['Company Name']
        logger.info(f"Validating data for {company_name}")
        
        validation_results = {
            'company_name': company_name,
            'website_valid': False,
            'linkedin_valid': False,
            'careers_valid': False,
            'job_listings_valid': False,
            'total_jobs_found': 0,
            'issues': []
        }
        
        # Validate website URL
        website_url = self.df.iloc[row_index]['Website URL']
        if not pd.isna(website_url):
            is_valid, message = self.validate_url(website_url, "Website")
            validation_results['website_valid'] = is_valid
            if not is_valid:
                validation_results['issues'].append(f"Website: {message}")
        
        # Validate LinkedIn URL
        linkedin_url = self.df.iloc[row_index]['Linkedin URL']
        if not pd.isna(linkedin_url):
            is_valid, message = self.validate_url(linkedin_url, "LinkedIn")
            validation_results['linkedin_valid'] = is_valid
            if not is_valid:
                validation_results['issues'].append(f"LinkedIn: {message}")
        
        # Validate careers page URL
        careers_url = self.df.iloc[row_index]['Careers Page URL']
        if not pd.isna(careers_url):
            is_valid, message = self.validate_url(careers_url, "Careers")
            validation_results['careers_valid'] = is_valid
            if not is_valid:
                validation_results['issues'].append(f"Careers: {message}")
        
        # Validate job listings page URL
        job_listings_url = self.df.iloc[row_index]['Job listings page URL']
        if not pd.isna(job_listings_url):
            is_valid, message = self.validate_url(job_listings_url, "Job Listings")
            validation_results['job_listings_valid'] = is_valid
            if not is_valid:
                validation_results['issues'].append(f"Job Listings: {message}")
        
        # Count job postings
        job_count = 0
        for i in range(1, 4):  # Check job post1, job post2, job post3
            job_url = self.df.iloc[row_index][f'job post{i} URL']
            job_title = self.df.iloc[row_index][f'job post{i} title']
            
            if not pd.isna(job_url) and not pd.isna(job_title):
                job_count += 1
                # Validate job URL
                is_valid, message = self.validate_url(job_url, f"Job {i}")
                if not is_valid:
                    validation_results['issues'].append(f"Job {i}: {message}")
        
        validation_results['total_jobs_found'] = job_count
        
        return validation_results
    
    def validate_all_data(self):
        """Validate all company data"""
        logger.info("Starting data validation...")
        
        validation_results = []
        total_companies = len(self.df)
        companies_with_websites = 0
        companies_with_careers = 0
        companies_with_jobs = 0
        total_jobs_found = 0
        
        for i in range(total_companies):
            try:
                result = self.validate_company_data(i)
                validation_results.append(result)
                
                # Update counters
                if result['website_valid']:
                    companies_with_websites += 1
                if result['careers_valid']:
                    companies_with_careers += 1
                if result['total_jobs_found'] > 0:
                    companies_with_jobs += 1
                    total_jobs_found += result['total_jobs_found']
                
                # Add delay to be respectful
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error validating company {i}: {e}")
                continue
        
        # Generate summary report
        self.generate_validation_report(validation_results, {
            'total_companies': total_companies,
            'companies_with_websites': companies_with_websites,
            'companies_with_careers': companies_with_careers,
            'companies_with_jobs': companies_with_jobs,
            'total_jobs_found': total_jobs_found
        })
        
        return validation_results
    
    def generate_validation_report(self, validation_results, summary_stats):
        """Generate a validation report"""
        logger.info("=== VALIDATION REPORT ===")
        logger.info(f"Total companies processed: {summary_stats['total_companies']}")
        logger.info(f"Companies with working websites: {summary_stats['companies_with_websites']}")
        logger.info(f"Companies with careers pages: {summary_stats['companies_with_careers']}")
        logger.info(f"Companies with job postings: {summary_stats['companies_with_jobs']}")
        logger.info(f"Total job postings found: {summary_stats['total_jobs_found']}")
        
        # Find companies with issues
        companies_with_issues = [r for r in validation_results if r['issues']]
        if companies_with_issues:
            logger.info(f"\nCompanies with issues: {len(companies_with_issues)}")
            for result in companies_with_issues[:10]:  # Show first 10
                logger.info(f"- {result['company_name']}: {', '.join(result['issues'])}")
        
        # Check if we have enough job postings
        if summary_stats['total_jobs_found'] >= 200:
            logger.info("✅ SUCCESS: Found 200+ job postings!")
        else:
            logger.info(f"⚠️  WARNING: Only found {summary_stats['total_jobs_found']} job postings (target: 200)")
    
    def fix_common_issues(self):
        """Fix common data issues"""
        logger.info("Fixing common data issues...")
        
        for i in range(len(self.df)):
            # Fix missing protocols in URLs
            for col in ['Website URL', 'Linkedin URL', 'Careers Page URL', 'Job listings page URL']:
                url = self.df.iloc[i][col]
                if not pd.isna(url) and not url.startswith(('http://', 'https://')):
                    self.df.iloc[i, self.df.columns.get_loc(col)] = 'https://' + url
            
            # Fix job post URLs
            for j in range(1, 4):
                job_url = self.df.iloc[i][f'job post{j} URL']
                if not pd.isna(job_url) and not job_url.startswith(('http://', 'https://')):
                    self.df.iloc[i, self.df.columns.get_loc(f'job post{j} URL')] = 'https://' + job_url
        
        # Save fixed data
        self.save_data()
        logger.info("Common issues fixed and data saved")
    
    def save_data(self):
        """Save the validated data"""
        try:
            self.df.to_excel(self.excel_file_path, index=False)
            logger.info("Validated data saved to Excel file")
        except Exception as e:
            logger.error(f"Error saving data: {e}")

def main():
    """Main function to run data validation"""
    excel_file = "E:/growth_for_impact_assignment/data/Growth For Impact Data Assignment.xlsx"
    
    validator = DataValidator(excel_file)
    
    if validator.load_data():
        logger.info("Starting data validation process...")
        validator.fix_common_issues()
        validator.validate_all_data()
        logger.info("Data validation completed successfully!")
    else:
        logger.error("Failed to load data. Please check the Excel file path.")

if __name__ == "__main__":
    main()
