from serpapi import GoogleSearch

  # replace with your key
API_KEY = "c4eab0aa7fecb68944b4bfcfc5ea1d6038a5dc1c14951da36e43eae99eaed41a"
# 1️⃣ Google Ads: Online Python Course
print("📌 Google Ads:")
google_params = {
    "engine": "google",      
    "q": "online python course",  
    "location": "India",     
    "api_key": API_KEY
}

try:
    google_search = GoogleSearch(google_params)
    google_results = google_search.get_dict()
    
    # Check for ads
    if "ads" in google_results:
        for ad in google_results.get("ads", []):
            print("-", ad.get("title"), "|", ad.get("displayed_link"))
    else:
        print("- No ads found in results")
        
    # Also check for shopping results which are ad-like
    if "shopping_results" in google_results:
        print("Shopping Ads:")
        for item in google_results.get("shopping_results", [])[:3]:
            print("-", item.get("title"), "|", item.get("price"))
            
except Exception as e:
    print(f"Error with Google search: {e}")


print("\n LinkedIn Posts/Jobs (via Google search):")
linkedin_params = {
    "engine": "google",   
    "q": "site:linkedin.com data science certification",  
    "location": "India",
    "api_key": API_KEY
}

try:
    linkedin_search = GoogleSearch(linkedin_params)
    linkedin_results = linkedin_search.get_dict()
    
    if "organic_results" in linkedin_results:
        for result in linkedin_results.get("organic_results", [])[:5]:
            if "linkedin.com" in result.get("link", ""):
                print("-", result.get("title"), "|", result.get("link"))
    else:
        print("- No LinkedIn results found")
        
except Exception as e:
    print(f"Error with LinkedIn search: {e}")

print("\n📌 Bing Ads:")
bing_params = {
    "engine": "bing",    
    "q": "online course",  
    "location": "India",
    "api_key": API_KEY
}

try:
    bing_search = GoogleSearch(bing_params)
    bing_results = bing_search.get_dict()
    
    if "ads" in bing_results:
        for ad in bing_results.get("ads", []):
            title = ad.get("title", "")
            link = ad.get("displayed_link", "")
            print(f"- {title} | {link}")
    else:
        print("- No ads found in Bing results")
        
except Exception as e:
    print(f"Error with Bing search: {e}")

# 4️⃣ Alternative: YouTube Ads (supported by SerpApi)
print("\n📌 YouTube Search Results (includes promoted videos):")
youtube_params = {
    "engine": "youtube",    
    "search_query": "online python course",  
    "api_key": API_KEY
}

try:
    youtube_search = GoogleSearch(youtube_params)
    youtube_results = youtube_search.get_dict()
    
    if "video_results" in youtube_results:
        for video in youtube_results.get("video_results", [])[:5]:
            title = video.get("title", "")
            channel = video.get("channel", {}).get("name", "")
            print(f"- {title} | Channel: {channel}")
    else:
        print("- No YouTube results found")
        
except Exception as e:
    print(f"Error with YouTube search: {e}")

print("\n📌 Note: SerpApi supported engines include:")
supported_engines = [
    "google", "bing", "baidu", "yandex", "yahoo", "youtube", 
    "amazon", "ebay", "google_scholar", "google_maps", 
    "google_news", "google_images", "duckduckgo"
]
print("Supported:", ", ".join(supported_engines))
print("Not supported: linkedin, facebook_ads, instagram_ads")

print("\nFor LinkedIn and Meta ads, you would need their official APIs:")
print("- LinkedIn Marketing API: https://docs.microsoft.com/en-us/linkedin/marketing/")
print("- Meta Marketing API: https://developers.facebook.com/docs/marketing-apis/")