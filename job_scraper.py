"""
Job Scraping Module for Growth For Impact Assignment
Professional implementation for job posting extraction
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

class JobScraper:
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
    
    def detect_job_platform(self, careers_url):
        """Detect which job platform the company uses with improved detection"""
        if not careers_url:
            return None
            
        url_lower = careers_url.lower()
        
        # Check for specific job platforms with more patterns
        if any(pattern in url_lower for pattern in ['lever.co', 'jobs.lever.co', 'lever']):
            return 'lever'
        elif any(pattern in url_lower for pattern in ['zohorecruit.com', 'zohorecruit', 'zoho']):
            return 'zoho_recruit'
        elif any(pattern in url_lower for pattern in ['greenhouse.io', 'boards.greenhouse.io', 'greenhouse']):
            return 'greenhouse'
        elif any(pattern in url_lower for pattern in ['workday.com', 'workday']):
            return 'workday'
        elif any(pattern in url_lower for pattern in ['bamboohr.com', 'bamboohr']):
            return 'bamboo_hr'
        elif any(pattern in url_lower for pattern in ['ashbyhq.com', 'ashby']):
            return 'ashby'
        elif any(pattern in url_lower for pattern in ['smartrecruiters.com', 'smartrecruiters']):
            return 'smartrecruiters'
        elif any(pattern in url_lower for pattern in ['jobvite.com', 'jobvite']):
            return 'jobvite'
        else:
            return 'custom'
    
    def scrape_lever_jobs(self, careers_url, max_jobs=3):
        """Scrape jobs from Lever platform"""
        try:
            response = self.session.get(careers_url, timeout=10)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            jobs = []
            
            # Look for job postings
            job_selectors = [
                'div.posting',
                'div[data-qa="posting"]',
                'div.job-posting',
                'div.posting-item'
            ]
            
            job_elements = []
            for selector in job_selectors:
                elements = soup.select(selector)
                if elements:
                    job_elements = elements
                    break
            
            for i, job_element in enumerate(job_elements[:max_jobs]):
                try:
                    # Get job title and URL
                    title_link = job_element.find('a')
                    if title_link:
                        job_title = title_link.get_text(strip=True)
                        job_url = title_link.get('href', '')
                        if not job_url.startswith('http'):
                            job_url = urljoin(careers_url, job_url)
                        
                        # Get job location
                        location_element = job_element.find('span', class_='sort-by-location')
                        if not location_element:
                            location_element = job_element.find('div', class_='location')
                        job_location = location_element.get_text(strip=True) if location_element else "Not specified"
                        
                        jobs.append({
                            'title': job_title,
                            'url': job_url,
                            'location': job_location,
                            'date': "Recent"
                        })
                        
                except Exception as e:
                    logger.warning(f"Error scraping Lever job {i}: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} jobs from Lever")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping Lever jobs: {e}")
            return []
    
    def scrape_zoho_jobs(self, careers_url, max_jobs=3):
        """Scrape jobs from Zoho Recruit platform"""
        try:
            response = self.session.get(careers_url, timeout=10)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            jobs = []
            
            # Look for job postings
            job_selectors = [
                'div.job-item',
                'div.job-listing',
                'div[data-job-id]',
                'div.job-card'
            ]
            
            job_elements = []
            for selector in job_selectors:
                elements = soup.select(selector)
                if elements:
                    job_elements = elements
                    break
            
            for i, job_element in enumerate(job_elements[:max_jobs]):
                try:
                    # Get job title and URL
                    title_link = job_element.find('a')
                    if title_link:
                        job_title = title_link.get_text(strip=True)
                        job_url = title_link.get('href', '')
                        if not job_url.startswith('http'):
                            job_url = urljoin(careers_url, job_url)
                        
                        # Get job location
                        location_element = job_element.find('span', class_='job-location')
                        if not location_element:
                            location_element = job_element.find('div', class_='location')
                        job_location = location_element.get_text(strip=True) if location_element else "Not specified"
                        
                        jobs.append({
                            'title': job_title,
                            'url': job_url,
                            'location': job_location,
                            'date': "Recent"
                        })
                        
                except Exception as e:
                    logger.warning(f"Error scraping Zoho job {i}: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} jobs from Zoho Recruit")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping Zoho jobs: {e}")
            return []
    
    def scrape_greenhouse_jobs(self, careers_url, max_jobs=3):
        """Scrape jobs from Greenhouse platform"""
        try:
            response = self.session.get(careers_url, timeout=10)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            jobs = []
            
            # Look for job postings
            job_selectors = [
                'div.opening',
                'div.job',
                'div[data-qa="opening"]',
                'div.job-listing'
            ]
            
            job_elements = []
            for selector in job_selectors:
                elements = soup.select(selector)
                if elements:
                    job_elements = elements
                    break
            
            for i, job_element in enumerate(job_elements[:max_jobs]):
                try:
                    # Get job title and URL
                    title_link = job_element.find('a')
                    if title_link:
                        job_title = title_link.get_text(strip=True)
                        job_url = title_link.get('href', '')
                        if not job_url.startswith('http'):
                            job_url = urljoin(careers_url, job_url)
                        
                        # Get job location
                        location_element = job_element.find('span', class_='location')
                        if not location_element:
                            location_element = job_element.find('div', class_='location')
                        job_location = location_element.get_text(strip=True) if location_element else "Not specified"
                        
                        jobs.append({
                            'title': job_title,
                            'url': job_url,
                            'location': job_location,
                            'date': "Recent"
                        })
                        
                except Exception as e:
                    logger.warning(f"Error scraping Greenhouse job {i}: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} jobs from Greenhouse")
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping Greenhouse jobs: {e}")
            return []
    
    def scrape_custom_jobs(self, careers_url, max_jobs=3):
        """Scrape jobs from custom career pages with aggressive detection"""
        try:
            response = self.session.get(careers_url, timeout=10)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            jobs = []
            
            # Much more aggressive job detection with many more selectors
            job_selectors = [
                # Common job listing patterns
                'div.job', 'div.job-listing', 'div.career-item', 'div.position',
                'li.job', 'li.job-listing', 'li.career-item', 'li.position',
                'article.job', 'article.job-listing', 'article.career-item',
                'div[class*="job"]', 'div[class*="career"]', 'div[class*="position"]',
                'div[class*="opening"]', 'div[class*="vacancy"]', 'div[class*="role"]',
                
                # More specific patterns
                'div.job-card', 'div.job-item', 'div.job-post', 'div.job-opening',
                'div.career-card', 'div.career-item', 'div.career-post',
                'div.position-card', 'div.position-item', 'div.position-post',
                'div.opportunity', 'div.opportunity-card', 'div.opportunity-item',
                
                # List patterns
                'li[class*="job"]', 'li[class*="career"]', 'li[class*="position"]',
                'li[class*="opening"]', 'li[class*="vacancy"]', 'li[class*="role"]',
                
                # Table patterns
                'tr[class*="job"]', 'tr[class*="career"]', 'tr[class*="position"]',
                'td[class*="job"]', 'td[class*="career"]', 'td[class*="position"]',
                
                # Generic patterns that might contain jobs
                'div[class*="list"]', 'div[class*="item"]', 'div[class*="card"]',
                'div[class*="post"]', 'div[class*="entry"]', 'div[class*="content"]',
                
                # Look for any div with job-related text
                'div:contains("job")', 'div:contains("career")', 'div:contains("position")',
                'div:contains("opening")', 'div:contains("vacancy")', 'div:contains("role")'
            ]
            
            job_elements = []
            for selector in job_selectors:
                try:
                    elements = soup.select(selector)
                    if elements:
                        # Filter elements that actually contain job-related content
                        filtered_elements = []
                        for elem in elements:
                            text_content = elem.get_text().lower()
                            if any(keyword in text_content for keyword in ['job', 'career', 'position', 'opening', 'vacancy', 'role', 'apply', 'hiring']):
                                filtered_elements.append(elem)
                        
                        if filtered_elements:
                            job_elements = filtered_elements
                            logger.info(f"Found {len(job_elements)} potential job elements with selector: {selector}")
                            break
                except:
                    continue
            
            # If no specific selectors work, try to find any links that might be jobs
            if not job_elements:
                all_links = soup.find_all('a', href=True)
                job_links = []
                for link in all_links:
                    link_text = link.get_text().strip().lower()
                    link_href = link.get('href', '').lower()
                    if (any(keyword in link_text for keyword in ['job', 'career', 'position', 'opening', 'vacancy', 'role', 'apply']) or
                        any(keyword in link_href for keyword in ['job', 'career', 'position', 'opening', 'vacancy', 'role'])):
                        job_links.append(link)
                
                if job_links:
                    logger.info(f"Found {len(job_links)} potential job links")
                    job_elements = job_links[:max_jobs]
            
            for i, job_element in enumerate(job_elements[:max_jobs]):
                try:
                    # Get job title and URL
                    job_title = ""
                    job_url = ""
                    
                    # Try different ways to get title and URL
                    if job_element.name == 'a':
                        job_title = job_element.get_text(strip=True)
                        job_url = job_element.get('href', '')
                    else:
                        # Look for links within the element
                        title_link = job_element.find('a')
                        if title_link:
                            job_title = title_link.get_text(strip=True)
                            job_url = title_link.get('href', '')
                        else:
                            # Try to get title from text content
                            job_title = job_element.get_text(strip=True)
                            job_url = careers_url
                    
                    # Clean up title
                    if job_title:
                        job_title = re.sub(r'\s+', ' ', job_title).strip()
                        # Remove common prefixes/suffixes
                        job_title = re.sub(r'^(job|career|position|opening|vacancy|role):\s*', '', job_title, flags=re.IGNORECASE)
                        job_title = re.sub(r'\s*(job|career|position|opening|vacancy|role)$', '', job_title, flags=re.IGNORECASE)
                    
                    if not job_title or len(job_title) < 3:
                        continue
                    
                    # Make URL absolute
                    if job_url and not job_url.startswith('http'):
                        job_url = urljoin(careers_url, job_url)
                    
                    # Get job location
                    job_location = "Not specified"
                    location_text = job_element.get_text()
                    location_patterns = [
                        r'(Remote|Hybrid|On-site|Office|Location:?\s*[^\\n]+)',
                        r'(Full-time|Part-time|Contract|Permanent)',
                        r'(New York|London|San Francisco|Berlin|Paris|Toronto|Sydney)',
                        r'([A-Z][a-z]+,\s*[A-Z]{2})',  # City, State pattern
                        r'([A-Z][a-z]+,\s*[A-Z][a-z]+)'  # City, Country pattern
                    ]
                    
                    for pattern in location_patterns:
                        location_match = re.search(pattern, location_text, re.IGNORECASE)
                        if location_match:
                            job_location = location_match.group(1)
                            break
                    
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
    
    def find_alternative_careers_urls(self, careers_url):
        """Find alternative career page URLs to try"""
        try:
            base_url = careers_url.rstrip('/')
            alternative_paths = [
                '/jobs', '/work-with-us', '/join-us', '/career', '/employment',
                '/hiring', '/opportunities', '/team', '/people', '/openings',
                '/vacancies', '/positions', '/roles', '/current-openings',
                '/job-openings', '/available-positions', '/we-are-hiring'
            ]
            
            alternative_urls = []
            for path in alternative_paths:
                alt_url = base_url + path
                alternative_urls.append(alt_url)
            
            return alternative_urls
            
        except Exception as e:
            logger.error(f"Error finding alternative URLs: {e}")
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
        logger.info(f"Detected platform: {platform}")
        
        # Try platform-specific scraping first
        if platform == 'lever':
            jobs = self.scrape_lever_jobs(careers_url)
        elif platform == 'zoho_recruit':
            jobs = self.scrape_zoho_jobs(careers_url)
        elif platform == 'greenhouse':
            jobs = self.scrape_greenhouse_jobs(careers_url)
        else:
            jobs = self.scrape_custom_jobs(careers_url)
        
        # If no jobs found with platform-specific method, try custom method as fallback
        if not jobs and platform != 'custom':
            logger.info(f"No jobs found with {platform} method, trying custom method...")
            jobs = self.scrape_custom_jobs(careers_url)
        
        # If still no jobs, try alternative career page URLs
        if not jobs:
            logger.info("No jobs found, trying alternative career page URLs...")
            alternative_urls = self.find_alternative_careers_urls(careers_url)
            for alt_url in alternative_urls:
                if alt_url != careers_url:
                    logger.info(f"Trying alternative URL: {alt_url}")
                    alt_jobs = self.scrape_custom_jobs(alt_url)
                    if alt_jobs:
                        jobs = alt_jobs
                        break
        
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
        time.sleep(2)
    
    def scrape_all_jobs(self, start_index=0, end_index=None):
        """Scrape jobs for all companies"""
        if end_index is None:
            end_index = len(self.df)
        
        logger.info(f"Starting job scraping for companies {start_index} to {end_index}")
        
        total_jobs_found = 0
        
        for i in range(start_index, end_index):
            try:
                initial_jobs = self.count_existing_jobs(i)
                self.scrape_jobs_for_company(i)
                final_jobs = self.count_existing_jobs(i)
                new_jobs = final_jobs - initial_jobs
                total_jobs_found += new_jobs
                
                logger.info(f"Company {i+1}/{end_index}: {new_jobs} new jobs found. Total so far: {total_jobs_found}")
                
                # Save progress every 5 companies
                if i % 5 == 0:
                    self.save_progress()
                
                # Stop if we have enough jobs
                if total_jobs_found >= 200:
                    logger.info(f"Target of 200 jobs reached! Stopping at company {i+1}")
                    break
                    
            except Exception as e:
                logger.error(f"Error processing company {i}: {e}")
                continue
        
        logger.info(f"Job scraping completed. Total jobs found: {total_jobs_found}")
    
    def count_existing_jobs(self, row_index):
        """Count existing jobs for a company"""
        count = 0
        for i in range(1, 4):
            job_url = self.df.iloc[row_index][f'job post{i} URL']
            if not pd.isna(job_url) and job_url:
                count += 1
        return count
    
    def save_progress(self):
        """Save current progress to Excel file"""
        try:
            self.df.to_excel(self.excel_file_path, index=False)
            logger.info("Progress saved to Excel file")
        except Exception as e:
            logger.error(f"Error saving progress: {e}")

def main():
    """Main function to run job scraping"""
    excel_file = "E:/growth_for_impact_assignment/data/Growth For Impact Data Assignment.xlsx"
    
    scraper = JobScraper(excel_file)
    
    if scraper.load_data():
        logger.info("Starting job scraping process...")
        scraper.scrape_all_jobs()
        scraper.save_progress()
        logger.info("Job scraping completed successfully!")
    else:
        logger.error("Failed to load data.")

if __name__ == "__main__":
    main()

