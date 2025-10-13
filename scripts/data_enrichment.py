"""
Data Enrichment Script for Growth For Impact Assignment
Automatically finds company websites, LinkedIn URLs, and careers pages
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CompanyDataEnricher:
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
    
    def find_company_website(self, company_name):
        """Find company website using Google search"""
        try:
            # Simple Google search simulation
            search_query = f'"{company_name}" official website'
            # In real implementation, you'd use Google Search API or web scraping
            # For now, we'll use a placeholder approach
            
            # Common website patterns to try
            potential_domains = [
                f"https://{company_name.lower().replace(' ', '')}.com",
                f"https://{company_name.lower().replace(' ', '')}.org",
                f"https://www.{company_name.lower().replace(' ', '')}.com",
                f"https://www.{company_name.lower().replace(' ', '')}.org"
            ]
            
            for domain in potential_domains:
                try:
                    response = self.session.get(domain, timeout=10)
                    if response.status_code == 200:
                        logger.info(f"Found website for {company_name}: {domain}")
                        return domain
                except:
                    continue
            
            logger.warning(f"Could not find website for {company_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding website for {company_name}: {e}")
            return None
    
    def find_linkedin_url(self, company_name):
        """Find LinkedIn URL for company"""
        try:
            # Search LinkedIn for company
            linkedin_url = f"https://www.linkedin.com/company/{company_name.lower().replace(' ', '-')}"
            
            # Test if the URL exists
            response = self.session.get(linkedin_url, timeout=10)
            if response.status_code == 200:
                logger.info(f"Found LinkedIn for {company_name}: {linkedin_url}")
                return linkedin_url
            else:
                logger.warning(f"LinkedIn not found for {company_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error finding LinkedIn for {company_name}: {e}")
            return None
    
    def find_careers_page(self, website_url):
        """Find careers page on company website"""
        if not website_url:
            return None
            
        try:
            response = self.session.get(website_url, timeout=10)
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Common careers page patterns
            careers_patterns = [
                '/careers', '/jobs', '/work-with-us', '/join-us', 
                '/careers/', '/jobs/', '/work-with-us/', '/join-us/',
                '/career', '/job', '/employment', '/hiring'
            ]
            
            # Look for careers links in navigation
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').lower()
                if any(pattern in href for pattern in careers_patterns):
                    full_url = urljoin(website_url, link['href'])
                    logger.info(f"Found careers page: {full_url}")
                    return full_url
            
            # Try common careers page URLs
            for pattern in careers_patterns:
                careers_url = urljoin(website_url, pattern)
                try:
                    response = self.session.get(careers_url, timeout=10)
                    if response.status_code == 200:
                        logger.info(f"Found careers page: {careers_url}")
                        return careers_url
                except:
                    continue
            
            logger.warning(f"No careers page found for {website_url}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding careers page for {website_url}: {e}")
            return None
    
    def enrich_company_data(self, row_index):
        """Enrich data for a single company"""
        company_name = self.df.iloc[row_index]['Company Name']
        logger.info(f"Processing company: {company_name}")
        
        # Find website if not already present
        if pd.isna(self.df.iloc[row_index]['Website URL']):
            website_url = self.find_company_website(company_name)
            if website_url:
                self.df.iloc[row_index, self.df.columns.get_loc('Website URL')] = website_url
        
        # Find LinkedIn if not already present
        if pd.isna(self.df.iloc[row_index]['Linkedin URL']):
            linkedin_url = self.find_linkedin_url(company_name)
            if linkedin_url:
                self.df.iloc[row_index, self.df.columns.get_loc('Linkedin URL')] = linkedin_url
        
        # Find careers page
        website_url = self.df.iloc[row_index]['Website URL']
        if not pd.isna(website_url):
            careers_url = self.find_careers_page(website_url)
            if careers_url:
                self.df.iloc[row_index, self.df.columns.get_loc('Careers Page URL')] = careers_url
        
        # Add delay to be respectful
        time.sleep(2)
    
    def enrich_all_companies(self, start_index=0, end_index=None):
        """Enrich data for all companies"""
        if end_index is None:
            end_index = len(self.df)
        
        logger.info(f"Starting data enrichment for companies {start_index} to {end_index}")
        
        for i in range(start_index, end_index):
            try:
                self.enrich_company_data(i)
                
                # Save progress every 10 companies
                if i % 10 == 0:
                    self.save_progress()
                    
            except Exception as e:
                logger.error(f"Error processing company {i}: {e}")
                continue
        
        logger.info("Data enrichment completed")
    
    def save_progress(self):
        """Save current progress to Excel file"""
        try:
            self.df.to_excel(self.excel_file_path, index=False)
            logger.info("Progress saved to Excel file")
        except Exception as e:
            logger.error(f"Error saving progress: {e}")

def main():
    """Main function to run data enrichment"""
    excel_file = "E:/growth_for_impact_assignment/data/Growth For Impact Data Assignment.xlsx"
    
    enricher = CompanyDataEnricher(excel_file)
    
    if enricher.load_data():
        logger.info("Starting data enrichment process...")
        enricher.enrich_all_companies()
        enricher.save_progress()
        logger.info("Data enrichment completed successfully!")
    else:
        logger.error("Failed to load data. Please check the Excel file path.")

if __name__ == "__main__":
    main()
