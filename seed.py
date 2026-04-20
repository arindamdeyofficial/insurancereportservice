"""Run: docker exec insuranceai-api-1 python seed.py"""
import os, sys
sys.path.insert(0, "/app")
os.environ.setdefault("DATABASE_URL", os.getenv("DATABASE_URL", ""))

from datetime import datetime, timezone, timedelta
from app.database import SessionLocal, Base, engine
from app.models import User, Article, Incident, Sentiment, RivalAd, Website

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ── clear existing data (preserve users) ──────────────────────────────────────
db.query(RivalAd).delete()
db.query(Incident).delete()
db.query(Sentiment).delete()
db.query(Article).delete()
db.query(Website).delete()
db.commit()

# ── WEBSITES ──────────────────────────────────────────────────────────────────
websites_data = [
    # English
    ("Times of India",         "https://timesofindia.indiatimes.com", "https://timesofindia.indiatimes.com/rssfeeds/1898055.cms", "english", True),
    ("The Hindu",              "https://www.thehindu.com",            "https://www.thehindu.com/business/Industry/feeder/default.rss", "english", True),
    ("Hindustan Times",        "https://www.hindustantimes.com",      "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml", "english", True),
    ("Economic Times",         "https://economictimes.indiatimes.com","https://economictimes.indiatimes.com/industry/banking/insurance/rssfeeds/13358259.cms", "english", True),
    ("The Indian Express",     "https://indianexpress.com",           "https://indianexpress.com/feed/", "english", True),
    ("Business Standard",      "https://www.business-standard.com",   "https://www.business-standard.com/rss/finance-3.rss", "english", True),
    ("Mint",                   "https://www.livemint.com",            "https://www.livemint.com/rss/money", "english", True),
    ("Financial Express",      "https://www.financialexpress.com",    "https://www.financialexpress.com/feed/", "english", True),
    ("Moneycontrol",           "https://www.moneycontrol.com",        "https://www.moneycontrol.com/rss/business.xml", "english", True),
    ("Telegraph India",        "https://www.telegraphindia.com",      "https://www.telegraphindia.com/rss/business.xml", "english", True),
    ("NDTV",                   "https://www.ndtv.com",                "https://feeds.feedburner.com/ndtvnews-top-stories", "english", True),
    ("India Today",            "https://www.indiatoday.in",           "https://www.indiatoday.in/rss/1206513", "english", False),
    ("The Print",              "https://theprint.in",                 "https://theprint.in/feed/", "english", False),
    ("New Indian Express",     "https://www.newindianexpress.com",    "https://www.newindianexpress.com/Nation/rss", "english", False),
    ("Deccan Herald",          "https://www.deccanherald.com",        "https://www.deccanherald.com/rss-feed/national", "english", False),
    # Hindi
    ("Dainik Bhaskar",         "https://www.bhaskar.com",             "https://www.bhaskar.com/rss-feed/1061/", "hindi", True),
    ("Dainik Jagran",          "https://www.jagran.com",              "https://www.jagran.com/rss/news-national.xml", "hindi", True),
    ("Amar Ujala",             "https://www.amarujala.com",           "https://www.amarujala.com/rss/breaking-news.xml", "hindi", True),
    ("Navbharat Times",        "https://navbharattimes.indiatimes.com","https://navbharattimes.indiatimes.com/rssfeedsdefault.cms", "hindi", True),
    ("Hindustan (Hindi)",      "https://www.livehindustan.com",       "https://www.livehindustan.com/rss/national.xml", "hindi", True),
    ("Rajasthan Patrika",      "https://www.patrika.com",             "https://www.patrika.com/rss/national-news.xml", "hindi", False),
    ("Jansatta",               "https://www.jansatta.com",            "https://www.jansatta.com/feed/", "hindi", False),
    ("Prabhat Khabar",         "https://www.prabhatkhabar.com",       "https://www.prabhatkhabar.com/feed", "hindi", False),
    ("Punjab Kesari",          "https://www.punjabkesari.in",         "https://www.punjabkesari.in/rss/national.xml", "hindi", False),
    ("Nai Duniya",             "https://www.naiduniya.com",           None, "hindi", False),
]

site_objs = []
for name, url, rss, lang, active in websites_data:
    s = Website(name=name, url=url, rss_url=rss, language=lang, is_active=active)
    db.add(s)
    site_objs.append(s)
db.flush()

# ── ARTICLES ──────────────────────────────────────────────────────────────────
now = datetime.now(timezone.utc)
def daysago(n): return now - timedelta(days=n)

articles_data = [
    ("Times of India",     "https://toi.in/art1",  "Guardian Insurance refuses claim of cancer patient citing pre-existing condition",
     "Guardian Insurance has come under fire after denying a claim filed by a 54-year-old cancer patient from Mumbai. The patient alleged that the insurer cited a pre-existing condition clause despite no such condition being disclosed at the time of policy issuance. Consumer forums have received multiple similar complaints against the insurer this month.", daysago(1)),
    ("The Hindu",          "https://thehindu.in/art2", "IRDAI orders audit of Guardian Insurance claim settlement process",
     "The Insurance Regulatory and Development Authority of India (IRDAI) has ordered a surprise audit of Guardian Insurance following a spike in unresolved complaints. The regulator noted that the claim settlement ratio of Guardian Insurance dropped to 82% in the last quarter, well below the industry average of 94%.", daysago(2)),
    ("Economic Times",     "https://et.in/art3",   "LIC launches 'Jeevan Labh' campaign with Rs 500 crore ad spend",
     "Life Insurance Corporation of India has launched a massive pan-India advertisement campaign named Jeevan Labh targeting middle-income families. The campaign features Bollywood actress Alia Bhatt and spans TV, OTT, and digital platforms with an estimated spend of Rs 500 crore for FY2026.", daysago(1)),
    ("Hindustan Times",    "https://ht.in/art4",   "Guardian Insurance agent arrested for policy fraud in Pune",
     "Pune police have arrested a Guardian Insurance agent for allegedly forging customer signatures on policies and siphoning premiums. The accused had issued fake policies to at least 47 customers over two years without their knowledge. Guardian Insurance has promised full reimbursement to affected policyholders.", daysago(3)),
    ("Business Standard",  "https://bs.in/art5",   "HDFC Ergo reports 28% growth in premium collection for FY2026",
     "HDFC Ergo General Insurance posted a 28% year-on-year growth in gross written premium for FY2026, driven by health and motor insurance segments. The company also launched a new 'Optima Secure' health plan targeting young professionals.", daysago(2)),
    ("Mint",               "https://mint.in/art6",  "Customer praises Guardian Insurance for quick claim after road accident",
     "A Bengaluru resident took to social media to praise Guardian Insurance after receiving his motor insurance claim within 48 hours of filing. The customer noted that the surveyor was professional and the digital process was seamless. Guardian Insurance responded by thanking the customer.", daysago(4)),
    ("Telegraph India",    "https://telegraph.in/art7", "Guardian Insurance misses premium refund deadline for lapsed policies",
     "Thousands of Guardian Insurance policyholders are reportedly still waiting for premium refunds on lapsed policies, months after the IRDAI-mandated deadline. Consumer advocacy groups say the insurer has been slow to process refunds, causing financial distress to rural customers.", daysago(5)),
    ("Financial Express",  "https://fe.in/art8",   "Bajaj Allianz launches AI-powered health insurance with cashless hospitals",
     "Bajaj Allianz Life Insurance introduced an AI-driven health insurance product that allows instant cashless hospitalisation at over 10,000 partner hospitals across India. The product uses machine learning to assess claims in under 30 minutes.", daysago(3)),
    ("Moneycontrol",       "https://mc.in/art9",   "ICICI Lombard's 'Complete Health Insurance' ad dominates IPL season",
     "ICICI Lombard has invested heavily in IPL 2026 sponsorships, with their 'Complete Health Insurance' campaign appearing across Star Sports and JioCinema. Industry analysts estimate the insurer's brand recall has increased by 35% during the cricket season.", daysago(6)),
    ("NDTV",               "https://ndtv.in/art10", "Guardian Insurance settles 10,000 COVID-era pending claims",
     "Guardian Insurance announced the settlement of over 10,000 COVID-era pending claims, disbursing Rs 420 crore to policyholders. The move comes after sustained pressure from IRDAI and consumer forums. The company's MD stated that all remaining claims will be resolved by Q2 FY2027.", daysago(7)),
    ("Dainik Bhaskar",     "https://db.in/art11",  "गार्डियन इंश्योरेंस के खिलाफ उपभोक्ता फोरम में 200 नई शिकायतें",
     "गार्डियन इंश्योरेंस के विरुद्ध देशभर के उपभोक्ता फोरमों में इस माह 200 से अधिक नई शिकायतें दर्ज की गई हैं। अधिकांश शिकायतें क्लेम अस्वीकृति और विलंबित भुगतान से संबंधित हैं। बीमा नियामक इरडाई ने कंपनी को नोटिस जारी किया है।", daysago(2)),
    ("Dainik Jagran",      "https://dj.in/art12",  "LIC की नई पॉलिसी 'जीवन उमंग' का ग्रामीण क्षेत्रों में जोरदार प्रचार",
     "भारतीय जीवन बीमा निगम ने अपनी नई योजना 'जीवन उमंग' का ग्रामीण और अर्ध-शहरी क्षेत्रों में व्यापक प्रचार अभियान शुरू किया है। इस अभियान में 5,000 से अधिक गाँवों में बीमा जागरूकता शिविर लगाए जा रहे हैं।", daysago(4)),
    ("Amar Ujala",         "https://au.in/art13",  "गार्डियन इंश्योरेंस की सेवाओं से संतुष्ट हैं 70% ग्राहक: सर्वे",
     "एक स्वतंत्र सर्वेक्षण के अनुसार गार्डियन इंश्योरेंस के 70% ग्राहक कंपनी की सेवाओं से संतुष्ट हैं। डिजिटल क्लेम प्रक्रिया और 24x7 हेल्पलाइन को सबसे अधिक सराहना मिली है।", daysago(3)),
    ("Navbharat Times",    "https://nbt.in/art14", "स्टार हेल्थ इंश्योरेंस का नया विज्ञापन अभियान 'सुरक्षा का वादा'",
     "स्टार हेल्थ एंड एलाइड इंश्योरेंस ने अपना नया विज्ञापन अभियान 'सुरक्षा का वादा' लॉन्च किया है। इस अभियान में क्रिकेटर विराट कोहली को ब्रांड एंबेसडर बनाया गया है और यह डिजिटल और प्रिंट मीडिया दोनों में चलाया जा रहा है।", daysago(5)),
    ("Hindustan (Hindi)",  "https://lh.in/art15",  "गार्डियन इंश्योरेंस पर जुर्माना: पॉलिसी नवीनीकरण में देरी का मामला",
     "बीमा नियामक इरडाई ने गार्डियन इंश्योरेंस पर 50 लाख रुपये का जुर्माना लगाया है। यह जुर्माना पॉलिसी नवीनीकरण प्रक्रिया में अनावश्यक विलंब और ग्राहकों को उचित जानकारी न देने के कारण लगाया गया है।", daysago(6)),
    ("Times of India",     "https://toi.in/art16", "Guardian Insurance wins 'Best Digital Insurer' award at FICCI summit",
     "Guardian Insurance was felicitated with the 'Best Digital Insurer 2025' award at the FICCI Insurance Summit in New Delhi. The award recognises the company's investment in AI-powered claims processing and its mobile app which has over 8 million downloads.", daysago(8)),
    ("The Hindu",          "https://thehindu.in/art17", "SBI Life's aggressive expansion targets tier-2 cities",
     "SBI Life Insurance has announced plans to open 200 new branches in tier-2 and tier-3 cities over the next 12 months. The company's new 'Smart Shield' campaign specifically targets first-time insurance buyers in smaller towns.", daysago(7)),
    ("Economic Times",     "https://et.in/art18",  "Guardian Insurance Q3 results: net profit up 12% despite claim surge",
     "Guardian Insurance reported a 12% increase in net profit for Q3 FY2026 despite a 30% surge in claims during the period. The CFO attributed the profitability to better risk underwriting and investment income from its Rs 12,000 crore portfolio.", daysago(9)),
    ("Mint",               "https://mint.in/art19", "Tata AIG's 'Sampoorna' campaign targets small business owners",
     "Tata AIG General Insurance has launched the 'Sampoorna' campaign aimed at small and medium enterprise owners. The campaign promotes bundled insurance products covering health, fire, and liability under a single policy.", daysago(10)),
    ("Business Standard",  "https://bs.in/art20",  "Guardian Insurance faces class action lawsuit over misleading policy terms",
     "A class action lawsuit has been filed against Guardian Insurance in the Bombay High Court by a consumer rights group representing 3,200 policyholders. The suit alleges that the insurer used misleading language in policy documents to deny legitimate claims.", daysago(11)),
]

art_objs = []
for source, url, title, text, pub in articles_data:
    a = Article(source=source, url=url, title=title, raw_text=text, published_at=pub)
    db.add(a)
    art_objs.append(a)
db.flush()

# ── INCIDENTS ────────────────────────────────────────────────────────────────
incidents_data = [
    (0, "Guardian Insurance denied a cancer patient's claim citing pre-existing conditions, leading to consumer forum complaint.", "high"),
    (1, "IRDAI ordered a surprise audit after Guardian Insurance's claim settlement ratio fell below industry average.", "high"),
    (3, "Guardian Insurance agent arrested for forging signatures and siphoning premiums from 47 customers.", "high"),
    (6, "Thousands of policyholders waiting for premium refunds on lapsed policies beyond IRDAI deadline.", "medium"),
    (10, "200 new consumer forum complaints filed against Guardian Insurance this month for claim rejections.", "medium"),
    (14, "IRDAI fined Guardian Insurance Rs 50 lakh for delays in policy renewal and insufficient customer communication.", "medium"),
    (19, "Guardian Insurance faces class action lawsuit in Bombay High Court over misleading policy terms.", "high"),
    (9,  "Guardian Insurance settled 10,000 COVID-era pending claims after pressure from regulators.", "low"),
]

for art_idx, summary, severity in incidents_data:
    db.add(Incident(article_id=art_objs[art_idx].id, summary=summary, severity=severity))

# ── SENTIMENTS ───────────────────────────────────────────────────────────────
sentiments_data = [
    (0,  -0.85, "negative", "Article reports claim denial causing public outrage against Guardian Insurance."),
    (1,  -0.78, "negative", "Regulatory audit signals serious concerns about Guardian Insurance practices."),
    (2,   0.10, "neutral",  "Report covers LIC campaign with no direct mention of Guardian Insurance."),
    (3,  -0.90, "negative", "Fraud by agent severely damages trust in Guardian Insurance brand."),
    (4,   0.10, "neutral",  "HDFC Ergo growth story with no direct Guardian Insurance reference."),
    (5,   0.88, "positive", "Customer publicly praised Guardian Insurance for fast claim settlement."),
    (6,  -0.70, "negative", "Policyholders distressed by missed refund deadlines from Guardian Insurance."),
    (7,   0.10, "neutral",  "Bajaj Allianz product launch coverage unrelated to Guardian Insurance."),
    (8,   0.05, "neutral",  "ICICI Lombard IPL campaign coverage."),
    (9,   0.55, "positive", "Guardian Insurance proactively settled 10,000 COVID claims, improving public sentiment."),
    (10, -0.72, "negative", "Hindi press reports surge in consumer complaints against Guardian Insurance."),
    (11,  0.05, "neutral",  "LIC campaign article with no Guardian Insurance mention."),
    (12,  0.65, "positive", "Survey shows 70% customer satisfaction with Guardian Insurance services."),
    (13,  0.05, "neutral",  "Star Health campaign article."),
    (14, -0.68, "negative", "IRDAI fine highlights Guardian Insurance's regulatory non-compliance."),
    (15,  0.72, "positive", "Guardian Insurance recognised as best digital insurer, strong brand sentiment."),
    (16,  0.05, "neutral",  "SBI Life expansion with no Guardian Insurance mention."),
    (17,  0.48, "positive", "Guardian Insurance Q3 profit growth shows financial resilience."),
    (18,  0.05, "neutral",  "Tata AIG campaign coverage."),
    (19, -0.82, "negative", "Class action lawsuit signals deep customer dissatisfaction with Guardian Insurance."),
]

for art_idx, score, label, reasoning in sentiments_data:
    db.add(Sentiment(article_id=art_objs[art_idx].id, score=score, label=label, reasoning=reasoning))

# ── RIVAL ADS ────────────────────────────────────────────────────────────────
rival_ads_data = [
    (2,  "LIC",           "Jeevan Labh pan-India campaign with Rs 500 crore spend featuring Alia Bhatt across TV and OTT."),
    (4,  "HDFC Ergo",     "Optima Secure health plan launch targeting young professionals with digital-first marketing."),
    (7,  "Bajaj Allianz", "AI-powered health insurance launch with cashless hospitalisation at 10,000+ hospitals."),
    (8,  "ICICI Lombard", "Complete Health Insurance IPL 2026 sponsorship campaign on Star Sports and JioCinema."),
    (11, "LIC",           "Jeevan Umang rural campaign covering 5,000 villages with insurance awareness camps."),
    (13, "Star Health",   "Suraksha Ka Vaada campaign with Virat Kohli as brand ambassador across digital and print."),
    (16, "SBI Life",      "Smart Shield campaign targeting first-time buyers in tier-2 and tier-3 cities."),
    (18, "Tata AIG",      "Sampoorna bundled SME insurance campaign covering health, fire, and liability."),
]

for art_idx, competitor, ad_summary in rival_ads_data:
    db.add(RivalAd(article_id=art_objs[art_idx].id, competitor_name=competitor, ad_summary=ad_summary))

db.commit()
db.close()
print(f"✓ Seeded {len(site_objs)} websites, {len(art_objs)} articles, {len(incidents_data)} incidents, {len(sentiments_data)} sentiments, {len(rival_ads_data)} rival ads.")
