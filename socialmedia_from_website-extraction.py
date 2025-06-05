import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# User-Agent header to mimic a browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_domain(url):
    """Extract domain from URL"""
    parsed = urlparse(url)
    return parsed.netloc

def find_email(soup, domain):
    """Find email addresses in the page"""
    # Common email patterns
    email_patterns = [
        r'[\w\.-]+@[\w\.-]+\.\w+',  # standard email format
        r'[\w\.-]+\[at\][\w\.-]+\.\w+',  # obfuscated with [at]
        r'[\w\.-]+\(at\)[\w\.-]+\.\w+',  # obfuscated with (at)
        r'[\w\.-]+\s*@\s*[\w\.-]+\.\w+'  # with spaces around @
    ]
    
    emails = set()
    
    # Check text content
    text = soup.get_text()
    for pattern in email_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            # Clean up the email
            clean_email = match.replace('[at]', '@').replace('(at)', '@').replace(' ', '')
            if domain.lower() in clean_email.lower():  # prefer emails matching domain
                emails.add(clean_email)
    
    # Check mailto links
    for link in soup.find_all('a', href=True):
        if link['href'].lower().startswith('mailto:'):
            email = link['href'][7:].split('?')[0]  # remove mailto: and parameters
            emails.add(email)
    
    # Return the first email found (or None)
    return next(iter(emails), None) if emails else None

def find_social_links(soup, domain):
    """Find social media links in the page"""
    social_links = {
        'twitter': None,
        'telegram': None,
        'linkedin': None
    }
    
    # Find all links in the page
    for link in soup.find_all('a', href=True):
        href = link['href'].lower()
        
        # Check for Twitter
        if not social_links['twitter']:
            if 'twitter.com' in href:
                social_links['twitter'] = href
            elif 'x.com' in href:  # New Twitter domain
                social_links['twitter'] = href
        
        # Check for Telegram
        if not social_links['telegram']:
            if 't.me' in href or 'telegram.me' in href or 'telegram.com' in href:
                social_links['telegram'] = href
        
        # Check for LinkedIn
        if not social_links['linkedin']:
            if 'linkedin.com' in href or 'linked.in' in href:
                social_links['linkedin'] = href
    
    # Also check meta tags for social media links
    for meta in soup.find_all('meta'):
        if 'property' in meta.attrs and 'content' in meta.attrs:
            if 'twitter:url' in meta['property'].lower():
                social_links['twitter'] = meta['content']
            elif 'og:telegram' in meta['property'].lower():
                social_links['telegram'] = meta['content']
            elif 'og:linkedin' in meta['property'].lower():
                social_links['linkedin'] = meta['content']
    
    return social_links

def process_website(url):
    """Process a single website to extract social links and email"""
    try:
        print(f"Processing: {url}")
        
        # Send HTTP request
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get domain
        domain = get_domain(url)
        
        # Find social links
        social_links = find_social_links(soup, domain)
        
        # Find email
        email = find_email(soup, domain)
        
        # Clean up the links
        for platform, link in social_links.items():
            if link and 'http' not in link:
                if platform == 'twitter' and link.startswith('@'):
                    social_links[platform] = f"https://twitter.com/{link[1:]}"
                elif platform == 'telegram' and link.startswith('@'):
                    social_links[platform] = f"https://t.me/{link[1:]}"
                elif link.startswith('www.'):
                    social_links[platform] = f"https://{link}"
        
        return {
            'Website': url,
            'Domain': domain,
            'Twitter': social_links['twitter'],
            'Telegram': social_links['telegram'],
            'LinkedIn': social_links['linkedin'],
            'Email': email
        }
    
    except requests.exceptions.RequestException as e:
        print(f"Error processing {url}: {str(e)}")
        return {
            'Website': url,
            'Domain': get_domain(url),
            'Twitter': None,
            'Telegram': None,
            'LinkedIn': None,
            'Email': None,
            'Error': str(e)
        }
    except Exception as e:
        print(f"Unexpected error processing {url}: {str(e)}")
        return {
            'Website': url,
            'Domain': get_domain(url),
            'Twitter': None,
            'Telegram': None,
            'LinkedIn': None,
            'Email': None,
            'Error': str(e)
        }

def main():
    # List of websites to process
       # List of websites to process
    websites = [
        "https://o3.network/#/",
        "https://rabby.io/",
        "https://www.dcentwallet.com/en",
        "https://holdstation.com/",
        "https://1inch.io/",
        "https://kirifuda.co.jp/",
        "https://wigwam.app/",
        "https://www.zeetox.io/",
        "https://fewcha.app/",
        "https://coin.space/",
        "https://sortedwallet.com/",
        "https://glue.net/",
        "https://web3.bitget.com/en",
        "https://www.friend.tech/",
        "https://www.coolwallet.io/",
        "https://www.fxwallet.com/",
        "https://virgocx.ca/",
        "https://wallet.near.org/",
        "https://nightly.app/",
        "https://www.fxwallet.com/",
        "https://polkasafe.xyz/",
        "https://myabcwallet.io/en",
        "https://fearlesswallet.io/",
        "https://gemwallet.com/",
        "https://www.summonplatform.com/",
        "https://unisat.io/",
        "https://redimi.net/",
        "https://www.ethos.io/",
        "https://oisy.com/",
        "https://klever.org/",
        "https://www.actpass.com/",
        "https://blockbolt.io/",
        "https://emoney.io/",
        "https://wallet.human.tech/",
        "https://nuron.banksocial.io/",
        "https://www.banksocial.io/media-requests-and-information",
        "https://corporate.yamgo.com/",
        "https://guarda.com/",
        "https://app.godex.ai/",
        "https://app.polimec.org/project/sEypaBabuUjevfEoRyls",
        "https://termix.ai/",
        "https://uxuy.com/",
        "https://www.argent.xyz/argent-x",
        "https://dex.org/"
    ]
    
    # Remove duplicates
    websites = list(set(websites))
    
    results = []
    
    # Process websites with threading for better performance
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_website, url) for url in websites]
        
        for future in as_completed(futures):
            results.append(future.result())
            time.sleep(1)  # Be polite with requests
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Reorder columns
    df = df[['Website', 'Domain', 'Email', 'Twitter', 'Telegram', 'LinkedIn', 'Error']]
    
    # Save to Excel
    output_file = 'website_contacts.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    main()