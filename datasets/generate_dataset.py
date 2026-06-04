import pandas as pd
import random
from datetime import datetime, timedelta

# Sample fake news patterns
fake_news_titles = [
    "BREAKING: Scientists Discover Cure for All Diseases!",
    "Shocking Truth: Government Hiding Alien Contact",
    "Miracle Diet: Lose 50 Pounds in 1 Week!",
    "URGENT: Banks Will Collapse Tomorrow!",
    "Celebrity Secretly Controls World Government",
    "Amazing: This One Trick Doctors Don't Want You to Know",
    "WARNING: Your Phone is Spying on You Right Now!",
    "Unbelievable: Man Lives to 200 Years Using This Method",
    "EXPOSED: The Real Truth Behind Recent Events",
    "Incredible: Free Money for Everyone Starting Next Week!"
]

fake_news_content = [
    "According to unnamed sources, scientists have made an unprecedented discovery that will change everything we know about medicine...",
    "Leaked documents reveal shocking information that governments worldwide have been hiding from the public for decades...",
    "Doctors are furious about this simple trick that has helped thousands lose weight without any effort or exercise...",
    "Financial experts warn of imminent collapse, but mainstream media refuses to report the truth...",
    "Investigation reveals disturbing connections between powerful figures and secretive organizations...",
]

real_news_titles = [
    "Local Council Approves New Infrastructure Project",
    "Research Team Publishes Study on Climate Patterns",
    "Company Announces Quarterly Earnings Report",
    "City Opens New Community Center for Residents",
    "University Researchers Make Progress in Cancer Study",
    "Government Releases Annual Budget Proposal",
    "Tech Company Launches Updated Software Version",
    "Sports Team Wins Championship After Close Match",
    "Museum Hosts Exhibition of Historical Artifacts",
    "School District Implements New Education Program"
]

real_news_content = [
    "The city council voted 7-2 in favor of the new infrastructure project during Tuesday's meeting. The project includes...",
    "Researchers at the university published their findings in the Journal of Climate Science. The study examined...",
    "The company reported revenues of $X million for Q3, representing a Y% increase compared to the same period last year...",
    "The new community center, located on Main Street, opened its doors to residents this week. Facilities include...",
    "Scientists at the research institute have made significant progress in understanding cancer cell behavior. The team...",
]

def generate_fake_news_dataset(num_samples=1000):
    data = []
    
    for i in range(num_samples):
        if i % 2 == 0:  # Generate fake news
            title = random.choice(fake_news_titles) + f" {random.randint(1, 100)}"
            text = random.choice(fake_news_content) * random.randint(2, 4)
            label = 0  # Fake
        else:  # Generate real news
            title = random.choice(real_news_titles) + f" - {random.randint(1, 100)}"
            text = random.choice(real_news_content) * random.randint(2, 4)
            label = 1  # Real
        
        data.append({
            'id': i,
            'title': title,
            'text': text,
            'label': label
        })
    
    df = pd.DataFrame(data)
    df.to_csv('datasets/fake_news_data.csv', index=False)
    print(f"Generated {num_samples} samples")
    print(f"Fake news: {len(df[df['label']==0])}")
    print(f"Real news: {len(df[df['label']==1])}")
    return df

if __name__ == "__main__":
    generate_fake_news_dataset()
