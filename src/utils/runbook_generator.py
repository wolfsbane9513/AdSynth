"""
Runbook generator module for AI Ad Generator.
Generates platform-specific production and uploading instructions.
"""

import os
from typing import Dict, Any

def generate_platform_runbook(platform: str, ad_script: str, product_info: Dict[str, Any]) -> str:
    """
    Generate a platform-specific runbook for producing and uploading the ad.
    
    Args:
        platform (str): The platform the ad is for (instagram, youtube, etc.)
        ad_script (str): The generated ad script
        product_info (Dict[str, Any]): The product information
        
    Returns:
        str: A markdown formatted runbook
    """
    # General runbook header
    runbook = f"""# Production Runbook: {product_info['product_name']} Ad for {platform.capitalize()}

## Generated Ad Script

```
{ad_script}
```

## Next Steps for Production and Upload

"""
    
    # Platform-specific instructions
    if platform == "instagram":
        runbook += """
### Instagram Ad Production Steps

1. **Visual Content Creation**
   - Design square (1080×1080px) or portrait (1080×1350px) image(s) based on the ad script
   - If creating a carousel, prepare 2-10 images that tell a sequential story
   - For Reels/Stories, storyboard a 15-30 second vertical video (1080×1920px)
   - Ensure text occupies less than 20% of the image area (Meta's recommendation)

2. **Copy Preparation**
   - Extract the primary text from the script (keep under 125 characters for best visibility)
   - Identify the strongest headline (30 character maximum)
   - Select 3-5 relevant hashtags from the script
   - Prepare a shortened URL for the call-to-action

3. **Production Tools Recommendation**
   - For images: Canva, Adobe Express, or GIMP (free)
   - For video: CapCut, InShot, or Adobe Premiere
   - Free stock photos: Unsplash, Pexels, or Pixabay

### Upload Instructions

1. **Using Instagram Business Account**
   - Log in to your Instagram Business account
   - Create a new post (Feed, Story, or Reel depending on your content)
   - Upload your created visual assets
   - Paste the caption from your script (edit as needed for length)
   - Add your selected hashtags
   - Include your shortened URL in your bio (mention "link in bio" in the caption)
   - Publish or schedule your post

2. **Using Meta Ads Manager**
   - Go to [Meta Ads Manager](https://www.facebook.com/adsmanager)
   - Create a new campaign with your marketing objective
   - Define your audience based on the target audience in your product info
   - Set your budget and schedule
   - Upload your creative assets and copy from the script
   - Add your destination URL
   - Review and launch your ad

### Performance Tracking

Monitor these key metrics after posting:
- Engagement rate (likes, comments, shares)
- Reach and impressions
- Profile visits and website clicks
- Follower growth
- Story completion rate (for Stories)
"""

    elif platform == "youtube":
        runbook += """
### YouTube Ad Production Steps

1. **Pre-Production Planning**
   - Break down the script into scenes and shots
   - Create a simple storyboard for each scene
   - Identify required actors, locations, and props
   - Plan for both visual content and voiceover/dialogue

2. **Video Production Guidelines**
   - Recommended resolution: 1920×1080px (16:9 aspect ratio)
   - Keep in-stream ads under 3 minutes (ideally 30-60 seconds)
   - Ensure high-quality audio (crucial for YouTube)
   - Include your key message in the first 5 seconds (for skippable ads)
   - End with a clear call-to-action

3. **Production Options**
   - **DIY approach**: Smartphone with stabilizer, basic lighting, simple editing
   - **Mid-range**: DSLR/mirrorless camera, basic lighting kit, Adobe Premiere
   - **Professional**: Hire a videographer/production company
   - **Alternative**: Use stock footage and motion graphics

4. **Recommended Tools**
   - Video editing: Adobe Premiere Pro, DaVinci Resolve (free), or CapCut
   - Motion graphics: Adobe After Effects or Canva Pro
   - Stock resources: Pexels, Unsplash, Artgrid, Epidemic Sound

### Upload Instructions

1. **Direct YouTube Upload**
   - Upload your video to your YouTube channel
   - Optimize title, description, and tags using keywords from your script
   - Add end screens and cards with CTAs
   - Set appropriate thumbnail

2. **Google Ads Campaign Setup**
   - Go to [Google Ads](https://ads.google.com/)
   - Create a new Video campaign
   - Select your campaign goal and campaign subtype
   - Define your targeting, budgeting, and bidding
   - Select your previously uploaded YouTube video or upload directly
   - Add companion banner ads if desired
   - Review and launch your campaign

### Ad Formats to Consider

Based on your script:
- **Skippable in-stream ads**: Played before or during videos
- **Non-skippable in-stream ads**: 15-20 second ads viewers must watch
- **Bumper ads**: 6-second non-skippable ads
- **Discovery ads**: Appear in search results and recommendations

### Performance Tracking

Monitor these key metrics:
- View rate
- Average view duration / watch time
- Click-through rate
- Conversion rate
- Cost per view
- Audience retention graph
"""

    elif platform == "tiktok":
        runbook += """
### TikTok Ad Production Steps

1. **Video Preparation**
   - Create vertical video (9:16 ratio, 1080×1920px)
   - Keep length between 9-15 seconds for optimal performance
   - Focus on quick, attention-grabbing opening (first 2 seconds)
   - Consider using trending sounds or music
   - Include on-screen text for key points

2. **Content Approach**
   - **Native style**: Make the ad feel like organic TikTok content
   - **Trend-based**: Leverage current TikTok trends in your niche
   - **Challenge format**: Create a challenge related to your product
   - **Tutorial style**: Quick how-to featuring your product
   - **Before/After**: Show transformation with your product

3. **Production Tools**
   - Use TikTok's native camera and editing tools for authentic feel
   - Alternative: CapCut (owned by ByteDance, TikTok's parent company)
   - Advanced: Use Premiere Pro/Final Cut and import to TikTok

### Upload Instructions

1. **Organic Posting First (Recommended)**
   - Post to your brand's TikTok account
   - Test performance organically
   - Use 3-5 relevant hashtags from your niche
   - Engage with comments to boost algorithm performance

2. **TikTok Ads Manager**
   - Go to [TikTok Ads Manager](https://ads.tiktok.com/)
   - Create new campaign and select your objective
   - Define audience targeting based on your product info
   - Set budget and schedule
   - Upload your video or use your existing TikTok post
   - Add display name, profile image, and ad text from your script
   - Select your CTA button
   - Submit for review

### Best Practices

- Keep it authentic and native to TikTok (avoid overly polished content)
- Show your product in action rather than just talking about it
- Use trending sounds when possible (but be aware of licensing for ads)
- Create a hook in the first 2 seconds
- Add captions/text overlay for viewers watching without sound

### Performance Tracking

Key metrics to monitor:
- Video views
- Completion rate
- Engagement rate (likes, comments, shares)
- Profile visits
- Click-through rate
- Conversion rate
"""

    elif platform == "facebook":
        runbook += """
### Facebook Ad Production Steps

1. **Visual Asset Preparation**
   - **Image ads**: 1200×628px (rectangular) or 1080×1080px (square)
   - **Video ads**: Landscape (16:9) or square (1:1)
   - **Carousel ads**: 2-10 images/videos with individual headlines
   - **Instant Experience**: Full-screen mobile experience

2. **Copy Elements to Prepare**
   - Primary text from your script (125 characters recommended for best visibility)
   - Headline (40 characters maximum)
   - Description (30 characters maximum)
   - CTA button text (from Facebook's predetermined options)

3. **Production Tools**
   - **Design**: Canva Pro, Adobe Express, or GIMP (free)
   - **Video**: Adobe Premiere, CapCut, or Clipchamp
   - **Stock resources**: Pexels, Unsplash, or Pixabay

### Upload Instructions

1. **Meta Ads Manager Process**
   - Go to [Meta Ads Manager](https://www.facebook.com/adsmanager)
   - Create a new campaign
   - Set your marketing objective (Awareness, Consideration, or Conversion)
   - Define your audience (use detailed targeting based on your product info)
   - Select placements (automatic or manual)
   - Set budget and schedule
   - Upload your creative assets
   - Input copy from your script
   - Add URL parameters for tracking
   - Review and launch campaign

2. **A/B Testing Recommendation**
   - Create 2-3 variations of your ad with different images or headlines
   - Run them simultaneously with equal budget
   - After 3-5 days, analyze which performs better
   - Scale the winning ad variation

### Ad Formats to Consider

Based on your script:
- **Feed ads**: Standard ads in Facebook News Feed
- **Story ads**: Full-screen vertical format
- **Carousel ads**: Multiple images/videos in a single ad
- **Video ads**: Engaging video content using your script

### Performance Tracking

Key metrics to monitor:
- Reach and frequency
- Engagement rate
- Click-through rate
- Cost per click
- Conversion rate
- Return on ad spend
"""

    elif platform == "video":
        runbook += """
### General Video Ad Production Steps

1. **Pre-Production**
   - Create a detailed storyboard from your script
   - Break down the script into scenes and shots
   - Identify locations, actors, and props needed
   - Prepare shot list and production schedule

2. **Production Essentials**
   - Choose appropriate equipment (camera, lighting, audio)
   - Ensure proper lighting and audio quality
   - Use a tripod or stabilizer for professional-looking footage
   - Film extra b-roll footage for flexibility in editing
   - Get multiple takes of key scenes

3. **Post-Production Workflow**
   - Organize and review footage
   - Create a rough cut following your script
   - Add music and sound effects
   - Color grade footage for professional look
   - Add text overlays, graphics, and animations
   - Include your logo and CTA
   - Export in appropriate formats for your target platforms

4. **Recommended Tools**
   - **Professional**: Adobe Premiere Pro, Final Cut Pro, DaVinci Resolve
   - **Mid-range**: Filmora, PowerDirector, Adobe Premiere Elements
   - **Budget**: CapCut, iMovie, Clipchamp
   - **Stock Resources**: Pexels, Unsplash, Artgrid, Epidemic Sound

### Multi-Platform Adaptation

1. **Aspect Ratio Versions**
   - YouTube/Web: 16:9 (landscape)
   - Instagram Feed: 1:1 (square) or 4:5 (vertical)
   - Stories/Reels/TikTok: 9:16 (vertical)
   - Facebook Feed: 16:9 or 1:1

2. **Length Adaptations**
   - TikTok/Reels: 15-30 seconds
   - YouTube Pre-roll: 15-30 seconds (key message in first 5 seconds)
   - Facebook/Instagram Feed: 15-60 seconds
   - Connected TV: 15-30 seconds

### Distribution Strategy

1. **Paid Advertising**
   - Upload to relevant ad platforms (Google Ads, Meta Ads Manager, TikTok Ads)
   - Create specific campaigns for each platform
   - Test different targeting options

2. **Organic Distribution**
   - Share on your brand's social channels
   - Upload to your YouTube channel
   - Embed on your website or landing pages
   - Share with email subscribers

### Performance Tracking

Create a unified tracking system across platforms:
- Views and impressions
- Engagement metrics
- Click-through rates
- Conversion rates
- Cost per acquisition
- Return on ad spend
"""

    else:  # general
        runbook += """
### General Social Media Ad Production Steps

1. **Visual Content Creation**
   - Create images or short video based on the ad script
   - Recommended sizes:
     - Square (1080×1080px) - works on most platforms
     - Landscape (1200×628px) - good for Facebook
     - Portrait (1080×1350px) - good for Instagram
   - Ensure visuals align with the message in the script
   - Include your logo and branded elements

2. **Copy Preparation**
   - Extract the primary message from the script
   - Create variations of different lengths:
     - Short version (1-2 sentences for Twitter)
     - Medium version (3-4 sentences for Facebook/LinkedIn)
     - Full version (for your website or blog)
   - Prepare hashtags if relevant to your platforms
   - Create a clear call-to-action

3. **Production Tools**
   - For images: Canva, Adobe Express, or Photoshop
   - For video: CapCut, Adobe Premiere, or InShot
   - For audio: Audacity or Adobe Audition
   - Stock resources: Unsplash, Pexels, or Envato Elements

### Platform Adaptation

Adjust your content for each platform:
- **Facebook**: Focus on engaging copy and strong visuals
- **Instagram**: Highly visual with concise copy and hashtags
- **Twitter**: Short, attention-grabbing copy with strong CTA
- **LinkedIn**: Professional tone with industry-relevant content
- **Pinterest**: Vertical imagery with descriptive text

### Upload Instructions

1. **Direct Platform Posting**
   - Post directly to each social platform
   - Schedule posts using tools like Hootsuite, Buffer, or Meta Business Suite
   - Customize copy slightly for each platform

2. **Paid Promotion**
   - Select the best-performing organic posts for paid promotion
   - Set up ads manager accounts on relevant platforms
   - Start with small test budgets ($5-10/day)
   - A/B test different audiences and placements

### Performance Monitoring

Key metrics to track:
- Engagement rate (likes, comments, shares)
- Click-through rate
- Conversion rate
- Cost per click/conversion
- Return on ad spend
- Audience growth
"""

    # Add budget considerations
    runbook += """
## Budget Considerations

### Low Budget Production (Under $500)
- **DIY Approach**:
  - Use smartphone with stabilizer ($50-150)
  - Natural lighting + reflectors ($20-50)
  - Royalty-free music from YouTube Audio Library (free)
  - Self-editing with Canva Pro ($13/month) or CapCut (free)

### Medium Budget Production ($500-$2,000)
- **Elevate Quality**:
  - Hire freelance designer/videographer ($300-800)
  - Stock footage and images ($50-200)
  - Professional editing on Fiverr or Upwork ($100-500)

### High Budget Production ($2,000+)
- **Professional Results**:
  - Agency services ($2,000-10,000+)
  - Professional talent/actors ($500-2,000)
  - Multiple assets for comprehensive campaign
  - Full-service management
"""

    return runbook

def save_runbook(platform: str, ad_script: str, product_info: Dict[str, Any], output_path: str = None) -> str:
    """
    Generate and save a platform-specific runbook.
    
    Args:
        platform (str): The platform the ad is for
        ad_script (str): The generated ad script
        product_info (Dict[str, Any]): The product information
        output_path (str, optional): Custom path to save the runbook
        
    Returns:
        str: Path to the saved runbook file
    """
    runbook_content = generate_platform_runbook(platform, ad_script, product_info)
    
    if not output_path:
        output_path = f"runbook_{platform}_{product_info['product_name'].replace(' ', '_').lower()}.md"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(runbook_content)
        
    print(f"Runbook saved to {output_path}")
    return output_path