# Growth For Impact Assignment

## Project Overview
This project implements automated data enrichment and job scraping for the Growth For Impact assignment. The solution processes company data, enriches missing information, and extracts job postings from various career platforms.

## Features
- **Data Enrichment**: Automatically finds company websites, LinkedIn profiles, and careers pages
- **Job Scraping**: Extracts job postings from multiple platforms (Lever, Zoho Recruit, Greenhouse, custom sites)
- **Data Validation**: Validates all URLs and ensures data quality
- **Progress Tracking**: Saves progress automatically and provides detailed logging

## Project Structure
```
growth_for_impact_assignment/
├── data/
│   └── Growth For Impact Data Assignment.xlsx  # Main data file
├── data_enrichment.py                          # Data enrichment module
├── job_scraper.py                              # Job scraping module
├── data_validator.py                           # Data validation module
├── main.py                                     # Main execution script
├── requirements.txt                            # Python dependencies
├── README.md                                   # This file
├── assignment_log.txt                          # Execution logs (generated)
└── final_report.txt                            # Final report (generated)
```

## Installation
1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage
Run the complete assignment:
```bash
python main.py
```

The script will:
1. Enrich company data (websites, LinkedIn, careers pages)
2. Scrape job postings from career pages
3. Validate all data and links
4. Generate final report

## Output Files
- **Excel File**: Updated with enriched data and job postings
- **Log File**: Detailed execution logs
- **Report File**: Summary statistics and results

## Technical Implementation
- **Data Enrichment**: Uses pattern matching and content validation
- **Job Scraping**: Platform-specific selectors for different job boards
- **Validation**: URL testing and data quality checks
- **Error Handling**: Robust error handling with progress saving

## Requirements
- Python 3.7+
- Internet connection for web scraping
- Excel file with company data

## Notes
- The script includes respectful delays between requests
- Progress is saved automatically every 10-25 companies
- Target: 200+ job postings from 150+ companies