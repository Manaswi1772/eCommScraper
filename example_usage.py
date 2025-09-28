#!/usr/bin/env python3
"""
Example usage of the Trustpilot API client

This script demonstrates how to use the TrustpilotAPIClient class
to fetch data from Trustpilot's public API.
"""

from trustpilotEndpoint import TrustpilotAPIClient, TrustpilotConfig, TrustpilotAPIError


def example_usage():
    """Example of how to use the Trustpilot API client"""
    
    # Replace with your actual API key
    API_KEY = "YOUR_API_KEY_HERE"
    
    if API_KEY == "YOUR_API_KEY_HERE":
        print("Please set your Trustpilot API key!")
        print("Get your API key from: https://business.trustpilot.com/integrations/developers")
        return
    
    # Initialize the client
    config = TrustpilotConfig(api_key=API_KEY)
    client = TrustpilotAPIClient(config)
    
    try:
        # Example: Find a business by domain
        domain = "example.com"  # Replace with the domain you want to search
        print(f"Searching for business with domain: {domain}")
        
        business_info = client.find_business_unit(domain)
        print(f"Found business: {business_info}")
        
        # Get the Business Unit ID
        buid = business_info.get('businessUnits', [{}])[0].get('id')
        if not buid:
            print("Could not find Business Unit ID")
            return
        
        print(f"Business Unit ID: {buid}")
        
        # Get business details
        business_details = client.get_business_unit_info(buid)
        print(f"Business Name: {business_details.get('displayName', 'N/A')}")
        print(f"Total Reviews: {business_details.get('numberOfReviews', 'N/A')}")
        print(f"TrustScore: {business_details.get('trustScore', 'N/A')}")
        
        # Get recent reviews
        reviews = client.get_reviews(buid, per_page=3)
        review_list = reviews.get('reviews', [])
        
        print(f"\nRecent Reviews ({len(review_list)}):")
        for i, review in enumerate(review_list, 1):
            print(f"\nReview {i}:")
            print(f"  Title: {review.get('title', 'N/A')}")
            print(f"  Rating: {review.get('stars', 'N/A')}/5")
            print(f"  Author: {review.get('consumer', {}).get('displayName', 'Anonymous')}")
            print(f"  Date: {review.get('createdAt', 'N/A')}")
            print(f"  Text: {review.get('text', 'N/A')[:100]}...")
        
    except TrustpilotAPIError as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    example_usage()
