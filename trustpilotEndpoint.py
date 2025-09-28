#!/usr/bin/env python3
"""
Trustpilot Public API Client

This script provides functionality to interact with Trustpilot's public API
to fetch business information, reviews, and other data.

Requirements:
- API key from Trustpilot Business account
- Business Unit ID (BUID) for the target business

Usage:
    python trustpilotEndpoint.py
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class TrustpilotConfig:
    """Configuration class for Trustpilot API"""
    api_key: str
    base_url: str = "https://api.trustpilot.com/v1"
    timeout: int = 30
    rate_limit_delay: float = 0.1  # Delay between requests to respect rate limits


class TrustpilotAPIError(Exception):
    """Custom exception for Trustpilot API errors"""
    pass


class TrustpilotAPIClient:
    """Client for interacting with Trustpilot's public API"""
    
    def __init__(self, config: TrustpilotConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'apikey': config.api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'TrustpilotAPIClient/1.0'
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a request to the Trustpilot API with error handling"""
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.get(
                url, 
                params=params, 
                timeout=self.config.timeout
            )
            
            # Add small delay to respect rate limits
            time.sleep(self.config.rate_limit_delay)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise TrustpilotAPIError("Invalid API key or unauthorized access")
            elif response.status_code == 404:
                raise TrustpilotAPIError("Resource not found")
            elif response.status_code == 429:
                raise TrustpilotAPIError("Rate limit exceeded. Please wait before making more requests.")
            else:
                raise TrustpilotAPIError(f"API request failed with status {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout as exc:
            raise TrustpilotAPIError("Request timed out") from exc
        except requests.exceptions.ConnectionError as exc:
            raise TrustpilotAPIError("Connection error occurred") from exc
        except requests.exceptions.RequestException as e:
            raise TrustpilotAPIError(f"Request failed: {str(e)}") from e
    
    def find_business_unit(self, domain: str) -> Dict[str, Any]:
        """
        Find business unit by domain name
        
        Args:
            domain: The domain name to search for (e.g., 'example.com')
            
        Returns:
            Dictionary containing business unit information
        """
        endpoint = "business-units/find"
        params = {'name': domain}
        return self._make_request(endpoint, params)
    
    def get_business_unit_info(self, buid: str) -> Dict[str, Any]:
        """
        Get detailed information about a business unit
        
        Args:
            buid: Business Unit ID
            
        Returns:
            Dictionary containing business unit details
        """
        endpoint = f"business-units/{buid}"
        return self._make_request(endpoint)
    
    def get_reviews(self, buid: str, per_page: int = 20, page: int = 1) -> Dict[str, Any]:
        """
        Get reviews for a business unit
        
        Args:
            buid: Business Unit ID
            per_page: Number of reviews per page (max 100)
            page: Page number to retrieve
            
        Returns:
            Dictionary containing reviews and pagination info
        """
        endpoint = f"business-units/{buid}/reviews"
        params = {
            'perPage': min(per_page, 100),  # Trustpilot limits to 100 per page
            'page': page
        }
        return self._make_request(endpoint, params)
    
    def get_all_reviews(self, buid: str, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all reviews for a business unit (handles pagination automatically)
        
        Args:
            buid: Business Unit ID
            max_pages: Maximum number of pages to fetch (None for all)
            
        Returns:
            List of all reviews
        """
        all_reviews = []
        page = 1
        
        while True:
            if max_pages and page > max_pages:
                break
                
            try:
                response = self.get_reviews(buid, per_page=100, page=page)
                reviews = response.get('reviews', [])
                
                if not reviews:
                    break
                    
                all_reviews.extend(reviews)
                page += 1
                
                # Check if we've reached the last page
                if len(reviews) < 100:
                    break
                    
            except TrustpilotAPIError as e:
                print(f"Error fetching page {page}: {e}")
                break
        
        return all_reviews
    
    def get_business_statistics(self, buid: str) -> Dict[str, Any]:
        """
        Get business statistics and summary
        
        Args:
            buid: Business Unit ID
            
        Returns:
            Dictionary containing business statistics
        """
        endpoint = f"business-units/{buid}/statistics"
        return self._make_request(endpoint)


def format_review(review: Dict[str, Any]) -> str:
    """Format a review for display"""
    title = review.get('title', 'No title')
    text = review.get('text', 'No text')
    stars = review.get('stars', 0)
    created_at = review.get('createdAt', 'Unknown date')
    author = review.get('consumer', {}).get('displayName', 'Anonymous')
    
    return f"""
Title: {title}
Author: {author}
Rating: {stars}/5 stars
Date: {created_at}
Review: {text}
{'='*50}
"""


def main():
    """Main function demonstrating API usage"""
    
    # Configuration - Replace with your actual API key
    API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key
    
    if API_KEY == "YOUR_API_KEY_HERE":
        print("Please set your Trustpilot API key in the script!")
        print("You can get an API key from: https://business.trustpilot.com/integrations/developers")
        return
    
    # Initialize the client
    config = TrustpilotConfig(api_key=API_KEY)
    client = TrustpilotAPIClient(config)
    
    try:
        # Example 1: Find business unit by domain
        print("=== Finding Business Unit ===")
        domain = "trustpilot.com"  # Example domain
        business_info = client.find_business_unit(domain)
        print(f"Found business: {json.dumps(business_info, indent=2)}")
        
        # Extract BUID from the response
        buid = business_info.get('businessUnits', [{}])[0].get('id')
        if not buid:
            print("Could not find Business Unit ID")
            return
        
        print(f"Business Unit ID: {buid}")
        
        # Example 2: Get business unit details
        print("\n=== Business Unit Details ===")
        business_details = client.get_business_unit_info(buid)
        print(f"Business Name: {business_details.get('displayName', 'N/A')}")
        print(f"Domain: {business_details.get('domain', 'N/A')}")
        print(f"Total Reviews: {business_details.get('numberOfReviews', 'N/A')}")
        print(f"TrustScore: {business_details.get('trustScore', 'N/A')}")
        
        # Example 3: Get business statistics
        print("\n=== Business Statistics ===")
        stats = client.get_business_statistics(buid)
        print(f"Statistics: {json.dumps(stats, indent=2)}")
        
        # Example 4: Get recent reviews
        print("\n=== Recent Reviews ===")
        reviews = client.get_reviews(buid, per_page=5)
        review_list = reviews.get('reviews', [])
        
        for review in review_list:
            print(format_review(review))
        
        # Example 5: Get all reviews (be careful with this - it can be a lot of data!)
        print("\n=== Getting All Reviews (First 3 pages only) ===")
        all_reviews = client.get_all_reviews(buid, max_pages=3)
        print(f"Total reviews fetched: {len(all_reviews)}")
        
        # Example 6: Analyze review ratings
        if all_reviews:
            ratings = [review.get('stars', 0) for review in all_reviews]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            print(f"Average rating: {avg_rating:.2f}")
            
            # Count rating distribution
            rating_counts = {}
            for rating in ratings:
                rating_counts[rating] = rating_counts.get(rating, 0) + 1
            print(f"Rating distribution: {rating_counts}")
        
    except TrustpilotAPIError as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
