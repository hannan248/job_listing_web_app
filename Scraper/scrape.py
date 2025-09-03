import time
import re
import os
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
import json

class ActuaryListScraper:
    def __init__(self, headless=False):
        self.driver = None
        self.jobs_data = []
        self.base_url = "https://www.actuarylist.com"
        self.jobs_url = "https://www.actuarylist.com"
        self.headless = headless
        self.setup_driver()
    
    def setup_driver(self):
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_argument("--silent")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.driver.implicitly_wait(10)
            print("Chrome WebDriver initialized successfully")
            
        except Exception as e:
            print(f"Error setting up WebDriver: {str(e)}")
            print("Make sure ChromeDriver is installed and in your PATH")
            raise
    
    def wait_for_page_load(self, timeout=20):
        """Wait for page to load completely with enhanced waiting"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            print("Page loaded, waiting for dynamic content...")
            
            time.sleep(5)
            
            loading_selectors = [
                "[class*='loading']", "[class*='spinner']", "[id*='loading']",
                ".loader", "#loader", ".loading-overlay"
            ]
            
            for selector in loading_selectors:
                try:
                    WebDriverWait(self.driver, 3).until(
                        EC.invisibility_of_element_located((By.CSS_SELECTOR, selector))
                    )
                except:
                    continue
                    
        except TimeoutException:
            print("Page load timeout, continuing anyway...")
    
    def handle_cookie_consent(self):
        """Handle cookie consent popup if present"""
        try:
            cookie_selectors = [
                "button[aria-label*='Accept']",
                "button[aria-label*='accept']",
                "button:contains('Accept')",
                "button:contains('OK')",
                "button:contains('Agree')",
                ".cookie-accept",
                "#cookie-accept",
                "[data-testid*='accept']",
                ".accept-cookies",
                "#accept-cookies"
            ]
            
            for selector in cookie_selectors:
                try:
                    cookie_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    cookie_button.click()
                    print("Cookie consent handled")
                    time.sleep(2)
                    return
                except:
                    continue
                    
        except Exception as e:
            print("No cookie consent found or could not handle it")
    
    def smart_scroll_and_load(self):
        """Smart scrolling to load dynamic content"""
        print("Attempting to load all jobs...")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        jobs_loaded_count = 0
        attempts = 0
        max_attempts = 10
        
        while attempts < max_attempts:
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(f"Scrolled to bottom (attempt {attempts + 1})")
            
            # Wait for new content to load
            time.sleep(3)
            
            # Check for "Load More" type buttons
            load_more_buttons = [
                "button:contains('Load More')", "button:contains('Show More')",
                "button:contains('Load more')", "button:contains('Show more')",
                ".load-more", "#load-more", ".show-more", "#show-more",
                "[data-testid*='load']", "[data-testid*='more']"
            ]
            
            for selector in load_more_buttons:
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if button.is_displayed() and button.is_enabled():
                        self.driver.execute_script("arguments[0].click();", button)
                        print(f"Clicked load more button")
                        time.sleep(3)
                        break
                except:
                    continue
            
            # Check if new content loaded
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # Also check for job-like elements
            current_job_count = len(self.driver.find_elements(By.CSS_SELECTOR, "*"))  # Get total elements
            
            if new_height == last_height and current_job_count == jobs_loaded_count:
                print("No new content loaded, stopping...")
                break
            
            last_height = new_height
            jobs_loaded_count = current_job_count
            attempts += 1
        
        # Scroll back to top to ensure all elements are in view
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
    
    def find_job_elements(self):
        """Enhanced job element detection specifically for actuarylist.com"""
        print("Searching for job elements...")
        
        # Based on the debug output, try specific ActuaryList.com selectors first
        actuarylist_selectors = [
            '[class*="Job_job-card"]',  
            '.Job_job-card__YgDAV',
            'div[class*="job-card"]',
            'div[class*="Job_job"]',
            '[class*="job-"]'
        ]
        
        job_elements = []
        successful_selector = None
        
        # Try ActuaryList specific selectors first
        for selector in actuarylist_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    # Filter out very small elements or duplicate elements
                    valid_elements = []
                    seen_texts = set()
                    
                    for element in elements:
                        try:
                            text_content = element.text.strip()
                            if len(text_content) > 20 and text_content not in seen_texts:
                                valid_elements.append(element)
                                seen_texts.add(text_content)
                        except:
                            continue
                    
                    if valid_elements:
                        job_elements = valid_elements
                        successful_selector = selector
                        print(f"Found {len(valid_elements)} job elements using ActuaryList selector: {selector}")
                        break
                        
            except Exception as e:
                continue
        
        # If ActuaryList selectors don't work, try generic ones
        if not job_elements:
            generic_selectors = [
                '[class*="job"]', '[id*="job"]',
                '[class*="listing"]', '[id*="listing"]',
                '[class*="position"]', '[id*="position"]',
                '.card', '.item', '.entry', '.post',
                'li[class*="job"]', 'li[class*="listing"]',
                'a[href*="/job"]', 'a[href*="/jobs"]'
            ]
            
            for selector in generic_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    valid_elements = []
                    for element in elements:
                        try:
                            text_content = element.text.strip()
                            if len(text_content) > 20:
                                valid_elements.append(element)
                        except:
                            continue
                    
                    if valid_elements:
                        job_elements = valid_elements
                        successful_selector = selector
                        print(f"Found {len(valid_elements)} job elements using generic selector: {selector}")
                        break
                        
                except Exception as e:
                    continue
        
        return job_elements, successful_selector
    
    def extract_job_data_enhanced(self, job_element):
        """Enhanced job data extraction with better parsing logic"""
        job_data = {
            'title': '',
            'company': '',
            'location': '',
            'posting_date': datetime.now(),
            'job_type': 'Full-time',
            'tags': [],
            'description': '',
            'url': ''
        }
        
        try:
            # Get all text content
            all_text = job_element.text.strip()
            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
            
            # Extract URL first
            try:
                link_element = job_element.find_element(By.TAG_NAME, "a")
                href = link_element.get_attribute("href")
                if href:
                    job_data['url'] = href if href.startswith('http') else self.base_url + href
            except:
                pass
            
            # Parse based on ActuaryList structure (from debug output)
            # Expected structure: Company, Title, Location flag, Location, Tags...
            if lines:
                # First non-empty line is often the company or title
                potential_company = lines[0] if lines else ""
                potential_title = lines[1] if len(lines) > 1 else ""
                
                # Look for location indicators (🇬🇧, 🇺🇸, etc.)
                location_info = []
                title_candidates = []
                company_candidates = []
                
                for i, line in enumerate(lines):
                    # Check for emoji flags (location indicators)
                    if any(emoji in line for emoji in ['🇬🇧', '🇺🇸', '🇨🇦', '🇦🇺', '🇩🇪', '🇫🇷']):
                        # This line and potentially next ones are location
                        location_parts = [line]
                        if i + 1 < len(lines) and not any(keyword in lines[i + 1].lower() 
                                                        for keyword in ['actuary', 'analyst', 'manager', 'director', 'senior', 'junior']):
                            location_parts.append(lines[i + 1])
                        location_info = location_parts
                        continue
                    
                    # Check for job titles (containing actuary-related terms)
                    if any(keyword in line.lower() for keyword in ['actuary', 'analyst', 'manager', 'director', 'senior', 'junior', 'consultant']):
                        if len(line) < 100:  # Reasonable title length
                            title_candidates.append(line)
                    
                    # Check for company names (shorter, corporate-sounding)
                    elif len(line) < 50 and i < 3:  # Company usually in first few lines
                        company_candidates.append(line)
                
                # Assign title
                if title_candidates:
                    job_data['title'] = title_candidates[0]
                elif len(lines) > 1:
                    job_data['title'] = lines[1]  # Default to second line
                else:
                    job_data['title'] = lines[0] if lines else "Actuarial Position"
                
                # Assign company - prefer shorter names that appear early
                if company_candidates:
                    # Choose the shortest reasonable company name
                    company_candidates.sort(key=len)
                    for candidate in company_candidates:
                        if 3 <= len(candidate) <= 50:  # Reasonable company name length
                            job_data['company'] = candidate
                            break
                
                # If still no company, use first line if it's not the title
                if not job_data['company'] and lines:
                    if lines[0] != job_data['title']:
                        job_data['company'] = lines[0]
                
                # Assign location
                if location_info:
                    job_data['location'] = ' '.join(location_info).replace('🇬🇧', 'UK').replace('🇺🇸', 'USA')
                else:
                    # Look for location patterns in text
                    location_patterns = [
                        r'(London|New York|Chicago|Toronto|Sydney|Berlin|Paris|Remote|Hybrid)',
                        r'([A-Z][a-z]+,\s*[A-Z]{2})',  # City, ST
                        r'(UK|USA|US|Canada|Australia|Germany|France)'
                    ]
                    
                    for pattern in location_patterns:
                        match = re.search(pattern, all_text, re.IGNORECASE)
                        if match:
                            job_data['location'] = match.group(1)
                            break
                
                # Extract tags from remaining lines
                tag_keywords = ['actuary', 'fellow', 'life', 'investments', 'pensions', 'insurance', 'risk', 'analytics']
                for line in lines:
                    line_lower = line.lower()
                    if any(keyword in line_lower for keyword in tag_keywords) and len(line) < 30:
                        if line not in job_data['tags']:
                            job_data['tags'].append(line)
                
                # Set description
                job_data['description'] = ' '.join(lines[:5])  # First 5 lines as description
            
            # Fallback values to ensure required fields
            if not job_data['title']:
                job_data['title'] = "Actuarial Position"
            if not job_data['company']:
                job_data['company'] = "Unknown Company"
            if not job_data['location']:
                job_data['location'] = "Location Not Specified"
            
            # Clean up fields
            job_data['title'] = job_data['title'][:100]  # Limit length
            job_data['company'] = job_data['company'][:100]
            job_data['location'] = job_data['location'][:100]
            job_data['description'] = job_data['description'][:500]
            
        except Exception as e:
            print(f"Error extracting job data: {str(e)}")
            # Set minimum required fields even on error
            if not job_data['title']:
                job_data['title'] = "Actuarial Position"
            if not job_data['company']:
                job_data['company'] = "Unknown Company"
            if not job_data['location']:
                job_data['location'] = "Location Not Specified"
        
        return job_data
    
    def scrape_jobs(self, max_jobs=10, debug=True):
        """Main scraping method with enhanced parsing"""
        try:
            print(f"Navigating to {self.jobs_url}")
            self.driver.get(self.jobs_url)
            self.wait_for_page_load()
            
            # Handle cookie consent
            self.handle_cookie_consent()
            
            # Smart scroll to load content
            self.smart_scroll_and_load()
            
            # Find job elements
            job_elements, successful_selector = self.find_job_elements()
            
            if job_elements:
                print(f" Found {len(job_elements)} job elements")
                print(f"Processing up to {min(len(job_elements), max_jobs)} jobs...")
                
                processed = 0
                for i, job_element in enumerate(job_elements[:max_jobs]):
                    try:
                        job_data = self.extract_job_data_enhanced(job_element)
                        
                        # Always add the job (we ensure required fields in extraction)
                        self.jobs_data.append(job_data)
                        processed += 1
                        print(f" Job {processed}: {job_data['title']} at {job_data['company']}")
                        print(f"   Location: {job_data['location']}")
                        if job_data['url']:
                            print(f"   URL: {job_data['url']}")
                            
                    except Exception as e:
                        print(f" Error processing job element {i}: {str(e)}")
                        continue
                
                print(f"\n Successfully scraped {len(self.jobs_data)} jobs")
            else:
                print(" No job elements could be found")
                # Try to extract from page source as last resort
                self.extract_from_page_source(max_jobs)
            
            return self.jobs_data
            
        except Exception as e:
            print(f" Error in scrape_jobs: {str(e)}")
            return []
    
    def extract_from_page_source(self, max_jobs):
        """Last resort: extract job info from page source"""
        try:
            print("Attempting to extract jobs from page source...")
            page_source = self.driver.page_source
            
            # Look for job-related URLs in the page source
            job_url_pattern = r'href="([^"]*(?:job|actuarial)[^"]*)"'
            job_urls = re.findall(job_url_pattern, page_source, re.IGNORECASE)
            
            # Look for company names and titles in the source
            # This is very basic but might catch something
            title_patterns = [
                r'(Senior\s+\w+\s+Actuary)',
                r'(Actuarial\s+\w+)',
                r'(\w+\s+Actuary)',
                r'(Risk\s+Analyst)',
                r'(Insurance\s+\w+)'
            ]
            
            found_titles = []
            for pattern in title_patterns:
                matches = re.findall(pattern, page_source, re.IGNORECASE)
                found_titles.extend(matches[:5])  # Limit to 5 per pattern
            
            # Create basic job entries
            for i, title in enumerate(found_titles[:max_jobs]):
                job_data = {
                    'title': title,
                    'company': f"Company {i+1}",  # Placeholder
                    'location': "Location Not Specified",
                    'posting_date': datetime.now(),
                    'job_type': 'Full-time',
                    'tags': ['Actuary'],
                    'description': f"Actuarial position: {title}",
                    'url': job_urls[i] if i < len(job_urls) else ''
                }
                self.jobs_data.append(job_data)
            
            if self.jobs_data:
                print(f"Extracted {len(self.jobs_data)} jobs from page source")
                
        except Exception as e:
            print(f" Error extracting from page source: {str(e)}")
    
    def save_to_json(self, filename='scraped_jobs.json'):
        """Save scraped data to JSON file"""
        try:
            json_data = []
            for job in self.jobs_data:
                job_copy = job.copy()
                if isinstance(job_copy['posting_date'], datetime):
                    job_copy['posting_date'] = job_copy['posting_date'].isoformat()
                json_data.append(job_copy)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f" Data saved to {filename}")
            return True
        except Exception as e:
            print(f" Error saving to JSON: {str(e)}")
            return False
    
    def send_to_api(self, api_url='http://localhost:5000/api/jobs'):
        """Send scraped data to Flask API with better error handling"""
        if not self.jobs_data:
            print("No job data to send to API")
            return 0, 0
            
        success_count = 0
        error_count = 0
        
        for job in self.jobs_data:
            try:
                api_data = {
                    'title': job['title'],
                    'company': job['company'],
                    'location': job['location'],
                    'job_type': job['job_type'],
                    'tags': job['tags'] if job['tags'] else ['Actuary'],
                    'description': job.get('description', ''),
                    'url': job.get('url', ''),
                    'posting_date': job['posting_date'].isoformat() if isinstance(job['posting_date'], datetime) else job['posting_date']
                }
                
                # Ensure all required fields have values
                for required_field in ['title', 'company', 'location']:
                    if not api_data[required_field] or api_data[required_field].strip() == '':
                        api_data[required_field] = f"Not specified"
                
                response = requests.post(api_url, json=api_data, timeout=10)
                
                if response.status_code == 201:
                    success_count += 1
                    print(f" Sent to API: {job['title']}")
                else:
                    error_count += 1
                    try:
                        error_detail = response.json()
                        print(f" Error sending {job['title']}: {error_detail}")
                    except:
                        print(f" Error sending {job['title']}: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                error_count += 1
                print(f" Network error sending job to API: {str(e)}")
            except Exception as e:
                error_count += 1
                print(f" Error sending job to API: {str(e)}")
        
        print(f" API upload complete: {success_count} successful, {error_count} errors")
        return success_count, error_count
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            print(" WebDriver closed")


def main():
    scraper = None
    try:
        print(" Starting Enhanced Actuary List Scraper...")
        scraper = ActuaryListScraper(headless=False)
        
        jobs = scraper.scrape_jobs(max_jobs=10, debug=True)
        
        if jobs:
            print(f"\n Summary:")
            print(f"   Total jobs scraped: {len(jobs)}")
            print(f"   Jobs with titles: {sum(1 for job in jobs if job['title'])}")
            print(f"   Jobs with companies: {sum(1 for job in jobs if job['company'])}")
            print(f"   Jobs with locations: {sum(1 for job in jobs if job['location'])}")
            
            # Save to JSON file
            scraper.save_to_json('scraped_jobs.json')
            
            # Try to send to API
            try:
                success, errors = scraper.send_to_api()
                print(f"📡 Sent {success} jobs to API with {errors} errors")
            except Exception as e:
                print(f" Could not connect to API: {str(e)}")
                print("Make sure the Flask API is running on http://localhost:5000")
        else:
            print(" No jobs were scraped successfully")
    
    except KeyboardInterrupt:
        print("  Scraping interrupted by user")
    except Exception as e:
        print(f" Scraping failed: {str(e)}")
    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    main()