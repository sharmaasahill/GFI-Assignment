"""
Data Enrichment Module for Growth For Impact Assignment
Professional implementation for company data enrichment
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

class DataEnricher:
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
        """Find company website using intelligent pattern matching"""
        try:
            # Clean company name for URL generation
            clean_name = company_name.lower()
            clean_name = re.sub(r'[^a-z0-9\s]', '', clean_name)
            clean_name = clean_name.replace(' ', '')
            
            # Generate potential website URLs
            patterns = [
                f"https://{clean_name}.com",
                f"https://{clean_name}.org",
                f"https://{clean_name}.co.uk",
                f"https://www.{clean_name}.com",
                f"https://www.{clean_name}.org",
                f"https://{clean_name.replace(' ', '')}.com",
                f"https://{clean_name.replace(' ', '-')}.com"
            ]
            
            for pattern in patterns:
                try:
                    response = self.session.get(pattern, timeout=8)
                    if response.status_code == 200:
                        # Verify it's the right company
                        if self.verify_company_website(response.text, company_name):
                            logger.info(f"Found website for {company_name}: {pattern}")
                            return pattern
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding website for {company_name}: {e}")
            return None
    
    def verify_company_website(self, html_content, company_name):
        """Verify that the website belongs to the correct company"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            text_content = soup.get_text().lower()
            
            # Check for company name in title or content
            company_words = company_name.lower().split()
            matches = sum(1 for word in company_words if word in text_content)
            
            return matches >= len(company_words) // 2
            
        except:
            return True  # If we can't verify, assume it's correct
    
    def find_linkedin_url(self, company_name):
        """Find LinkedIn URL for company"""
        try:
            # Clean company name for LinkedIn URL
            clean_name = company_name.lower()
            clean_name = re.sub(r'[^a-z0-9\s]', '', clean_name)
            clean_name = clean_name.replace(' ', '-')
            
            linkedin_patterns = [
                f"https://www.linkedin.com/company/{clean_name}",
                f"https://linkedin.com/company/{clean_name}",
                f"https://www.linkedin.com/company/{clean_name.replace('-', '')}",
                f"https://www.linkedin.com/company/{clean_name.replace('-', '_')}"
            ]
            
            for pattern in linkedin_patterns:
                try:
                    response = self.session.get(pattern, timeout=8)
                    if response.status_code == 200:
                        logger.info(f"Found LinkedIn for {company_name}: {pattern}")
                        return pattern
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding LinkedIn for {company_name}: {e}")
            return None
    
    def find_careers_page(self, website_url):
        """Find careers page on company website with improved detection"""
        if not website_url:
            return None
            
        try:
            # Much more comprehensive careers page paths
            careers_paths = [
                '/careers', '/jobs', '/work-with-us', '/join-us', '/career',
                '/employment', '/hiring', '/opportunities', '/team', '/people',
                '/openings', '/vacancies', '/positions', '/roles', '/current-openings',
                '/job-openings', '/available-positions', '/we-are-hiring', '/work-at',
                '/join-our-team', '/career-opportunities', '/job-opportunities',
                '/work-here', '/employment-opportunities', '/current-jobs',
                '/job-listings', '/career-center', '/human-resources'
            ]
            
            for path in careers_paths:
                careers_url = urljoin(website_url, path)
                try:
                    response = self.session.get(careers_url, timeout=8)
                    if response.status_code == 200:
                        if self.is_careers_page(response.text):
                            logger.info(f"Found careers page: {careers_url}")
                            return careers_url
                except:
                    continue
            
            # If no direct paths work, try to find careers links on the main page
            try:
                response = self.session.get(website_url, timeout=8)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for careers links in navigation
                    careers_links = []
                    for link in soup.find_all('a', href=True):
                        link_text = link.get_text().lower().strip()
                        link_href = link.get('href', '').lower()
                        
                        if (any(keyword in link_text for keyword in ['career', 'job', 'work', 'join', 'hiring', 'employment']) or
                            any(keyword in link_href for keyword in ['career', 'job', 'work', 'join', 'hiring', 'employment'])):
                            careers_links.append(link.get('href'))
                    
                    # Test found links
                    for link in careers_links[:5]:  # Test first 5 links
                        if link.startswith('/'):
                            link = urljoin(website_url, link)
                        elif not link.startswith('http'):
                            continue
                            
                        try:
                            response = self.session.get(link, timeout=8)
                            if response.status_code == 200 and self.is_careers_page(response.text):
                                logger.info(f"Found careers page via navigation: {link}")
                                return link
                        except:
                            continue
            except:
                pass
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding careers page for {website_url}: {e}")
            return None
    
    def is_careers_page(self, html_content):
        """Check if the page is actually a careers page with improved detection"""
        careers_keywords = [
            'career', 'job', 'employment', 'hiring', 'opportunity',
            'position', 'opening', 'vacancy', 'recruitment', 'join',
            'work with us', 'join our team', 'current openings', 'available positions',
            'work at', 'join us', 'career opportunities', 'job opportunities',
            'we are hiring', 'open positions', 'job openings', 'careers',
            'work here', 'employment opportunities', 'current jobs',
            'job listings', 'career center', 'human resources', 'hr',
            'talent', 'team', 'people', 'staff'
        ]

        html_lower = html_content.lower()
        keyword_count = sum(1 for keyword in careers_keywords if keyword in html_lower)

        # Also check for job-related HTML elements
        soup = BeautifulSoup(html_content, 'html.parser')

        # Look for job-related elements
        job_elements = soup.find_all(['div', 'li', 'article'], class_=re.compile(r'job|career|position|opening|vacancy|role', re.I))
        job_links = soup.find_all('a', href=re.compile(r'job|career|position|opening|vacancy|role', re.I))

        # If we find job-related elements or links, it's likely a careers page
        has_job_elements = len(job_elements) > 0 or len(job_links) > 0

        # If we find at least 2 career-related keywords OR job elements, it's likely a careers page
        return keyword_count >= 2 or has_job_elements
    
    def is_job_listings_page(self, html_content, url):
        """Check if the page is specifically a job listings page (not just careers page)"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            html_lower = html_content.lower()
            
            # Strong indicators of job listings page
            job_listing_indicators = [
                'apply now', 'apply for this position', 'job description',
                'requirements', 'responsibilities', 'qualifications',
                'salary', 'benefits', 'full-time', 'part-time', 'contract',
                'remote', 'hybrid', 'on-site', 'location', 'posted',
                'job type', 'experience level', 'department'
            ]
            
            # Count job listing indicators
            indicator_count = sum(1 for indicator in job_listing_indicators if indicator in html_lower)
            
            # Look for specific job listing elements
            job_listing_elements = soup.find_all(['div', 'li', 'article'], class_=re.compile(
                r'job-listing|job-post|job-opening|position-listing|career-listing|vacancy', re.I))
            
            # Look for apply buttons/links
            apply_links = soup.find_all('a', href=re.compile(r'apply|application', re.I))
            apply_buttons = soup.find_all(['button', 'input'], value=re.compile(r'apply|submit', re.I))
            
            # Look for job titles (usually in h1, h2, h3 tags)
            job_titles = soup.find_all(['h1', 'h2', 'h3'], string=re.compile(r'engineer|developer|manager|analyst|specialist|coordinator|director|lead', re.I))
            
            # Check for job platform indicators
            platform_indicators = [
                'lever.co', 'greenhouse.io', 'zohorecruit.com', 'workday.com',
                'bamboohr.com', 'smartrecruiters.com', 'jobvite.com'
            ]
            
            has_platform = any(platform in html_lower for platform in platform_indicators)
            
            # Scoring system
            score = 0
            if indicator_count >= 3:
                score += 2
            if len(job_listing_elements) > 0:
                score += 2
            if len(apply_links) > 0 or len(apply_buttons) > 0:
                score += 2
            if len(job_titles) > 0:
                score += 1
            if has_platform:
                score += 3
            
            # If score is 4 or higher, it's likely a job listings page
            return score >= 4
            
        except Exception as e:
            logger.warning(f"Error checking job listings page: {e}")
            return False
    
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
        time.sleep(1)
    
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
    
    enricher = DataEnricher(excel_file)
    
    if enricher.load_data():
        logger.info("Starting data enrichment process...")
        enricher.enrich_all_companies()
        enricher.save_progress()
        logger.info("Data enrichment completed successfully!")
    else:
        logger.error("Failed to load data. Please check the Excel file path.")

if __name__ == "__main__":
    main()

