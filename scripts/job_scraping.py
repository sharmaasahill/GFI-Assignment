"""
Job Scraping Script for Growth For Impact Assignment
Automatically scrapes job postings from company career pages
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JobScraper:
    def __init__(self, excel_file_path):
        self.excel_file_path = excel_file_path
        self.df = None
        self.driver = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def setup_driver(self):
        """Setup Chrome driver for dynamic content"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            logger.info("Chrome driver setup successful")
            return True
        except Exception as e:
            logger.error(f"Error setting up Chrome driver: {e}")
            return False
    
    def load_data(self):
        """Load the Excel file"""
        try:
            self.df = pd.read_excel(self.excel_file_path)
            logger.info(f"Loaded {len(self.df)} companies from Excel file")
            return True
        except Exception as e:
            logger.error(f"Error loading Excel file: {e}")
            return False
    
    def detect_job_platform(self, careers_url):
        """Detect which job platform the company uses"""
        if not careers_url:
            return None
            
        url_lower = careers_url.lower()
        
        # Common job platforms
        platforms = {
            'lever': 'lever.co' in url_lower,
            'zoho_recruit': 'zohorecruit.com' in url_lower,
            'greenhouse': 'greenhouse.io' in url_lower,
            'workday': 'workday.com' in url_lower,
            'bamboo_hr': 'bamboohr.com' in url_lower,
            'custom': True  # Default to custom if no platform detected
        }
        
        for platform, is_present in platforms.items():
            if is_present:
                logger.info(f"Detected platform: {platform} for {careers_url}")
                return platform
        
        return 'custom'
    
    def scrape_lever_jobs(self, careers_url, max_jobs=3):
        """Scrape jobs from Lever platform"""
        try:
            self.driver.get(careers_url)
            time.sleep(3)
            
            jobs = []
            job_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.posting')
            
            for i, job_element in enumerate(job_elements[:max_jobs]):
                try:
                    # Get job title
                    title_element = job_element.find_element(By.CSS_SELECTOR, 'h5 a')
                    job_title = title_element.text.strip()
                    job_url = title_element.get_attribute('href')
                    
                    # Get job location
                    try:
                        location_element = job_element.find_element(By.CSS_SELECTOR, 'span.sort-by-location')
                        job_location = location_element.text.strip()
                    except:
                        job_location = "Not specified"
                    
                    jobs.append({
                        'title': job_title,
                        'url': job_url,
                        'location': job_location,
                        'date': "Recent"  # Lever doesn't always show dates
                    })
                    
                except Exception as e:
                    logger.warning(f"Error scraping job {i}: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} jobs from Lever")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping Lever jobs: {e}")
            return []
    
    def scrape_zoho_jobs(self, careers_url, max_jobs=3):
        """Scrape jobs from Zoho Recruit platform"""
        try:
            self.driver.get(careers_url)
            time.sleep(3)
            
            jobs = []
            job_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.job-item')
            
            for i, job_element in enumerate(job_elements[:max_jobs]):
                try:
                    # Get job title and URL
                    title_element = job_element.find_element(By.CSS_SELECTOR, 'a.job-title')
                    job_title = title_element.text.strip()
                    job_url = title_element.get_attribute('href')
                    
                    # Get job location
                    try:
                        location_element = job_element.find_element(By.CSS_SELECTOR, 'span.job-location')
                        job_location = location_element.text.strip()
                    except:
                        job_location = "Not specified"
                    
                    jobs.append({
                        'title': job_title,
                        'url': job_url,
                        'location': job_location,
                        'date': "Recent"
                    })
                    
                except Exception as e:
                    logger.warning(f"Error scraping job {i}: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} jobs from Zoho Recruit")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping Zoho jobs: {e}")
            return []
    
    def scrape_greenhouse_jobs(self, careers_url, max_jobs=3):
        """Scrape jobs from Greenhouse platform"""
        try:
            self.driver.get(careers_url)
            time.sleep(3)
            
            jobs = []
            job_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.opening')
            
            for i, job_element in enumerate(job_elements[:max_jobs]):
                try:
                    # Get job title and URL
                    title_element = job_element.find_element(By.CSS_SELECTOR, 'a')
                    job_title = title_element.text.strip()
                    job_url = title_element.get_attribute('href')
                    
                    # Get job location
                    try:
                        location_element = job_element.find_element(By.CSS_SELECTOR, 'span.location')
                        job_location = location_element.text.strip()
                    except:
                        job_location = "Not specified"
                    
                    jobs.append({
                        'title': job_title,
                        'url': job_url,
                        'location': job_location,
                        'date': "Recent"
                    })
                    
                except Exception as e:
                    logger.warning(f"Error scraping job {i}: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} jobs from Greenhouse")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping Greenhouse jobs: {e}")
            return []
    
    def scrape_custom_jobs(self, careers_url, max_jobs=3):
        """Scrape jobs from custom career pages"""
        try:
            response = self.session.get(careers_url, timeout=10)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            jobs = []
            
            # Look for common job listing patterns
            job_selectors = [
                'div.job', 'div.job-listing', 'div.career-item', 'div.position',
                'li.job', 'li.job-listing', 'li.career-item', 'li.position',
                'article.job', 'article.job-listing', 'article.career-item'
            ]
            
            job_elements = []
            for selector in job_selectors:
                elements = soup.select(selector)
                if elements:
                    job_elements = elements
                    break
            
            for i, job_element in enumerate(job_elements[:max_jobs]):
                try:
                    # Try to find job title and URL
                    title_link = job_element.find('a')
                    if title_link:
                        job_title = title_link.get_text(strip=True)
                        job_url = urljoin(careers_url, title_link.get('href', ''))
                    else:
                        # Look for title in headings
                        title_heading = job_element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                        if title_heading:
                            job_title = title_heading.get_text(strip=True)
                            job_url = careers_url
                        else:
                            continue
                    
                    # Try to find location
                    location_text = job_element.get_text()
                    location_match = re.search(r'(Remote|Hybrid|On-site|Office|Location:?\s*[^\\n]+)', location_text, re.IGNORECASE)
                    job_location = location_match.group(1) if location_match else "Not specified"
                    
                    jobs.append({
                        'title': job_title,
                        'url': job_url,
                        'location': job_location,
                        'date': "Recent"
                    })
                    
                except Exception as e:
                    logger.warning(f"Error scraping custom job {i}: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} jobs from custom page")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping custom jobs: {e}")
            return []
    
    def scrape_jobs_for_company(self, row_index):
        """Scrape jobs for a single company"""
        company_name = self.df.iloc[row_index]['Company Name']
        careers_url = self.df.iloc[row_index]['Careers Page URL']
        
        if pd.isna(careers_url):
            logger.info(f"No careers page for {company_name}")
            return
        
        logger.info(f"Scraping jobs for {company_name} from {careers_url}")
        
        # Detect platform and scrape accordingly
        platform = self.detect_job_platform(careers_url)
        
        if platform == 'lever':
            jobs = self.scrape_lever_jobs(careers_url)
        elif platform == 'zoho_recruit':
            jobs = self.scrape_zoho_jobs(careers_url)
        elif platform == 'greenhouse':
            jobs = self.scrape_greenhouse_jobs(careers_url)
        else:
            jobs = self.scrape_custom_jobs(careers_url)
        
        # Update Excel with job data
        if jobs:
            for i, job in enumerate(jobs[:3]):  # Max 3 jobs
                job_num = i + 1
                self.df.iloc[row_index, self.df.columns.get_loc(f'job post{job_num} URL')] = job['url']
                self.df.iloc[row_index, self.df.columns.get_loc(f'job post{job_num} title')] = job['title']
            
            logger.info(f"Added {len(jobs)} jobs for {company_name}")
        else:
            logger.warning(f"No jobs found for {company_name}")
        
        # Add delay to be respectful
        time.sleep(3)
    
    def scrape_all_jobs(self, start_index=0, end_index=None):
        """Scrape jobs for all companies"""
        if end_index is None:
            end_index = len(self.df)
        
        logger.info(f"Starting job scraping for companies {start_index} to {end_index}")
        
        for i in range(start_index, end_index):
            try:
                self.scrape_jobs_for_company(i)
                
                # Save progress every 5 companies
                if i % 5 == 0:
                    self.save_progress()
                    
            except Exception as e:
                logger.error(f"Error processing company {i}: {e}")
                continue
        
        logger.info("Job scraping completed")
    
    def save_progress(self):
        """Save current progress to Excel file"""
        try:
            self.df.to_excel(self.excel_file_path, index=False)
            logger.info("Progress saved to Excel file")
        except Exception as e:
            logger.error(f"Error saving progress: {e}")
    
    def close_driver(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()

def main():
    """Main function to run job scraping"""
    excel_file = "E:/growth_for_impact_assignment/data/Growth For Impact Data Assignment.xlsx"
    
    scraper = JobScraper(excel_file)
    
    if scraper.load_data() and scraper.setup_driver():
        logger.info("Starting job scraping process...")
        scraper.scrape_all_jobs()
        scraper.save_progress()
        scraper.close_driver()
        logger.info("Job scraping completed successfully!")
    else:
        logger.error("Failed to load data or setup driver.")

if __name__ == "__main__":
    main()
