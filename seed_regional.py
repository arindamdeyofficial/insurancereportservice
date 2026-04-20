"""Seed regional Indian ePapers across all languages.
Run: docker exec insuranceai-api-1 python seed_regional.py
"""
import os, sys
sys.path.insert(0, "/app")

from app.database import SessionLocal, Base, engine
from app.models.website import Website

Base.metadata.create_all(bind=engine)
db = SessionLocal()

existing_names = {w.name for w in db.query(Website.name).all()}

REGIONAL = [
    # ── Bengali ──────────────────────────────────────────────────────────────
    ("Anandabazar Patrika",  "https://www.anandabazar.com",       "https://www.anandabazar.com/feeds/latest-news",               "bengali", True),
    ("Ei Samay",             "https://eisamay.com",               "https://eisamay.indiatimes.com/rssfeedsdefault.cms",           "bengali", True),
    ("Sangbad Pratidin",     "https://sangbadpratidin.in",        "https://sangbadpratidin.in/feed",                             "bengali", True),
    ("Bartaman Patrika",     "https://bartamanpatrika.com",       None,                                                           "bengali", True),
    ("Ganashakti",           "https://ganashakti.com",            "https://ganashakti.com/feed",                                 "bengali", False),
    ("Uttarbanga Sambad",    "https://uttarbangasambad.com",      "https://uttarbangasambad.com/feed",                           "bengali", False),
    ("Aajkaal",              "https://www.aajkaal.in",            None,                                                           "bengali", False),

    # ── Tamil ────────────────────────────────────────────────────────────────
    ("Dinamalar",            "https://www.dinamalar.com",         "https://www.dinamalar.com/rss/topnews.xml",                   "tamil",   True),
    ("Dinamani",             "https://www.dinamani.com",          "https://www.dinamani.com/rss-feeds/",                         "tamil",   True),
    ("Daily Thanthi",        "https://www.dailythanthi.com",      "https://www.dailythanthi.com/rss/home/",                      "tamil",   True),
    ("Dinakaran",            "https://www.dinakaran.com",         "https://www.dinakaran.com/feed",                              "tamil",   True),
    ("Maalai Malar",         "https://www.maalaimalar.com",       "https://www.maalaimalar.com/rss",                             "tamil",   False),
    ("Murasoli",             "https://murasoli.in",               None,                                                           "tamil",   False),

    # ── Telugu ───────────────────────────────────────────────────────────────
    ("Eenadu",               "https://www.eenadu.net",            "https://www.eenadu.net/rss/topnews.xml",                      "telugu",  True),
    ("Sakshi",               "https://www.sakshi.com",            "https://www.sakshi.com/feeds/telugu-news",                    "telugu",  True),
    ("Andhra Jyothi",        "https://www.andhrajyothy.com",      "https://www.andhrajyothy.com/rss",                            "telugu",  True),
    ("Andhra Prabha",        "https://www.andhraprabha.com",      "https://www.andhraprabha.com/feed",                           "telugu",  True),
    ("Vaartha",              "https://www.vaartha.com",           "https://www.vaartha.com/feed",                                "telugu",  False),
    ("Prajasakti",           "https://www.prajasakti.com",        "https://www.prajasakti.com/feed",                             "telugu",  False),
    ("Visalaandhra",         "https://www.visalaandhra.com",      None,                                                           "telugu",  False),

    # ── Malayalam ────────────────────────────────────────────────────────────
    ("Malayala Manorama",    "https://www.manoramaonline.com",    "https://www.manoramaonline.com/news/kerala.rss",               "malayalam", True),
    ("Mathrubhumi",          "https://www.mathrubhumi.com",       "https://www.mathrubhumi.com/rss/latest-news.rss",             "malayalam", True),
    ("Madhyamam",            "https://www.madhyamam.com",         "https://www.madhyamam.com/feeds/rss",                         "malayalam", True),
    ("Kerala Kaumudi",       "https://keralakaumudi.com",         "https://keralakaumudi.com/feed",                              "malayalam", True),
    ("Deshabhimani",         "https://www.deshabhimani.com",      "https://www.deshabhimani.com/rss-feed",                       "malayalam", False),
    ("Deepika",              "https://www.deepika.com",           "https://www.deepika.com/rss/topnews.aspx",                    "malayalam", False),
    ("Mangalam",             "https://www.mangalam.com",          None,                                                           "malayalam", False),
    ("Janmabhumi",           "https://janmabhumi.in",             "https://janmabhumi.in/feed",                                  "malayalam", False),

    # ── Kannada ──────────────────────────────────────────────────────────────
    ("Vijaya Karnataka",     "https://vijaykarnataka.com",        "https://vijaykarnataka.com/rssfeedsdefault.cms",               "kannada", True),
    ("Prajavani",            "https://www.prajavani.net",         "https://www.prajavani.net/feed",                              "kannada", True),
    ("Udayavani",            "https://www.udayavani.com",         "https://www.udayavani.com/feed",                              "kannada", True),
    ("Kannada Prabha",       "https://www.kannadaprabha.com",     "https://www.kannadaprabha.com/feed",                          "kannada", True),
    ("Samyukta Karnataka",   "https://www.samyuktakarnataka.com", None,                                                           "kannada", False),
    ("Hosa Diganta",         "https://www.hosadiganta.com",       "https://www.hosadiganta.com/feed",                            "kannada", False),
    ("Vishwavani",           "https://www.vishwavani.news",       "https://www.vishwavani.news/feed",                            "kannada", False),

    # ── Marathi ──────────────────────────────────────────────────────────────
    ("Maharashtra Times",    "https://maharashtratimes.com",      "https://maharashtratimes.indiatimes.com/rssfeedsdefault.cms",  "marathi", True),
    ("Lokmat",               "https://www.lokmat.com",            "https://www.lokmat.com/rss/feed.xml",                         "marathi", True),
    ("Sakal",                "https://www.sakal.com",             "https://www.sakal.com/feeds",                                 "marathi", True),
    ("Loksatta",             "https://www.loksatta.com",          "https://www.loksatta.com/feed/",                              "marathi", True),
    ("Pudhari",              "https://pudhari.news",              "https://pudhari.news/feed",                                   "marathi", False),
    ("Tarun Bharat (Nagpur)","https://www.tarunbharat.com",       "https://www.tarunbharat.com/feed",                            "marathi", False),
    ("Divya Marathi",        "https://www.divyamarathi.bhaskar.com","https://www.divyamarathi.bhaskar.com/rss-feed/",            "marathi", False),

    # ── Gujarati ─────────────────────────────────────────────────────────────
    ("Gujarat Samachar",     "https://www.gujaratsamachar.com",   "https://www.gujaratsamachar.com/rss/gujarati-news.xml",       "gujarati", True),
    ("Divya Bhaskar",        "https://www.divyabhaskar.co.in",    "https://www.divyabhaskar.co.in/rss-feed/",                    "gujarati", True),
    ("Sandesh",              "https://sandesh.com",               "https://sandesh.com/feed",                                    "gujarati", True),
    ("Nav Gujarat Samay",    "https://navgujaratsamay.com",       "https://navgujaratsamay.com/feed",                            "gujarati", False),
    ("Akila",                "https://www.akilanews.com",         None,                                                           "gujarati", False),

    # ── Punjabi ──────────────────────────────────────────────────────────────
    ("Ajit (Punjabi)",       "https://www.ajitjalandhar.com",     "https://www.ajitjalandhar.com/rss.aspx",                      "punjabi", True),
    ("Jagbani",              "https://www.jagbani.com",           "https://www.jagbani.com/rss.aspx",                            "punjabi", True),
    ("Desh Sewak",           "https://www.deshsewak.com",         None,                                                           "punjabi", False),
    ("Nawan Zamana",         "https://www.nawanzamana.com",       None,                                                           "punjabi", False),
    ("Rozana Spokesman",     "https://rozanaspokesman.in",        "https://rozanaspokesman.in/feed",                             "punjabi", False),

    # ── Odia ─────────────────────────────────────────────────────────────────
    ("Sambad",               "https://sambad.in",                 "https://sambad.in/feed",                                      "odia",    True),
    ("Samaja",               "https://www.thesamaja.com",         "https://www.thesamaja.com/rss-feed/",                         "odia",    True),
    ("Dharitri",             "https://www.dharitri.com",          "https://www.dharitri.com/feed",                               "odia",    True),
    ("Pragativadi",          "https://pragativadi.com",           "https://pragativadi.com/feed",                                "odia",    False),
    ("Prajatantra",          "https://www.prajatantra.co.in",     None,                                                           "odia",    False),
    ("Aajira Odisha",        "https://aajiraodisha.in",           "https://aajiraodisha.in/feed",                                "odia",    False),

    # ── Assamese ─────────────────────────────────────────────────────────────
    ("Asomiya Pratidin",     "https://asomiyapratidin.in",        "https://asomiyapratidin.in/feed",                             "assamese", True),
    ("Dainik Agradoot",      "https://agradoot.in",               "https://agradoot.in/feed",                                    "assamese", True),
    ("Amar Asom",            "https://www.amarasom.com",          "https://www.amarasom.com/feed",                               "assamese", True),
    ("Dainik Janasadharan",  "https://www.janasadharan.in",       None,                                                           "assamese", False),
    ("Natun Asomiya Patrika","https://natun.in",                  None,                                                           "assamese", False),

    # ── Urdu ─────────────────────────────────────────────────────────────────
    ("Inquilab",             "https://www.inquilab.com",          "https://www.inquilab.com/feed",                               "urdu",    True),
    ("Siasat Daily",         "https://www.siasat.com",            "https://www.siasat.com/feed",                                 "urdu",    True),
    ("Etemaad",              "https://www.etemaaddaily.com",      "https://www.etemaaddaily.com/feed",                           "urdu",    True),
    ("Munsif Daily",         "https://www.munsif.net",            None,                                                           "urdu",    False),
    ("Rashtriya Sahara Urdu","https://www.rashtriyasahara.com",   "https://www.rashtriyasahara.com/feed",                        "urdu",    False),
    ("Roznama Sahara",       "https://www.saharasamay.com",       None,                                                           "urdu",    False),

    # ── Marathi (Goa/Konkani) ────────────────────────────────────────────────
    ("Gomantak",             "https://www.gomantak.com",          "https://www.gomantak.com/feed",                               "konkani", True),
    ("Tarun Bharat (Goa)",   "https://www.tarunbharatonline.com", "https://www.tarunbharatonline.com/feed",                      "konkani", True),
    ("Goa Today",            "https://www.goatoday.net",          None,                                                           "konkani", False),

    # ── Nepali ───────────────────────────────────────────────────────────────
    ("Hamro Patro (Sikkim)", "https://www.hamropatro.com",        None,                                                           "nepali",  False),
    ("Sikkim Express",       "https://www.sikkimexpress.com",     None,                                                           "nepali",  False),
    ("Himalayan Darpan",     "https://himalayandarpan.com",       None,                                                           "nepali",  False),

    # ── Maithili / Bhojpuri region ───────────────────────────────────────────
    ("Dainik Bhaskar (Bihar)","https://www.bhaskar.com/bihar",   "https://www.bhaskar.com/rss-feed/1221/",                      "maithili", False),
    ("Hindustan (Patna)",    "https://www.livehindustan.com/bihar","https://www.livehindustan.com/rss/state-news.xml",           "maithili", False),

    # ── Manipuri ─────────────────────────────────────────────────────────────
    ("Poknapham",            "https://www.poknapham.in",          "https://www.poknapham.in/feed",                               "manipuri", False),
    ("Naharolgi Thoudang",   "https://www.naharolgithoudang.com", None,                                                           "manipuri", False),
    ("The Sangai Express",   "https://www.thesangaiexpress.com",  "https://www.thesangaiexpress.com/feed",                       "manipuri", False),

    # ── Tripuri / Kokborok ───────────────────────────────────────────────────
    ("Dainik Sambad (Tripura)","https://www.dainiks.com",        None,                                                           "bengali",  False),

    # ── North East (Mizo / Naga) ─────────────────────────────────────────────
    ("Mizoram Express",      "https://mizoramexpress.com",        "https://mizoramexpress.com/feed",                             "mizo",    False),
    ("Nagaland Post",        "https://nagalandpost.com",          "https://nagalandpost.com/feed",                               "english", False),
    ("Morung Express",       "https://morungexpress.com",         "https://morungexpress.com/feed",                              "english", False),
    ("The Sentinel (Assam)", "https://www.sentinelassam.com",     "https://www.sentinelassam.com/feed",                          "english", False),

    # ── Kashmiri ─────────────────────────────────────────────────────────────
    ("Kashmir Times",        "https://www.kashmirtimes.com",      "https://www.kashmirtimes.com/feed",                           "kashmiri", False),
    ("Daily Excelsior",      "https://www.dailyexcelsior.com",    "https://www.dailyexcelsior.com/feed",                         "english",  True),
    ("Greater Kashmir",      "https://www.greaterkashmir.com",    "https://www.greaterkashmir.com/feed",                         "english",  False),

    # ── Rajasthani (Rajasthan regional) ──────────────────────────────────────
    ("Rajasthan Patrika",    "https://www.patrika.com",           "https://www.patrika.com/rss/national-news.xml",               "hindi",   True),
    ("Dainik Navjyoti",      "https://www.navjyoti.com",          "https://www.navjyoti.com/feed",                               "hindi",   False),

    # ── Chhattisgarh ────────────────────────────────────────────────────────
    ("Haribhoomi",           "https://www.haribhoomi.com",        "https://www.haribhoomi.com/rss-feed/",                        "hindi",   False),
    ("Deshbandhu (Raipur)",  "https://www.deshbandhu.co.in",      "https://www.deshbandhu.co.in/feed",                           "hindi",   False),

    # ── Jharkhand ────────────────────────────────────────────────────────────
    ("Prabhat Khabar",       "https://www.prabhatkhabar.com",     "https://www.prabhatkhabar.com/feed",                          "hindi",   True),
    ("Ranchi Express",       "https://www.ranchiexpress.com",     None,                                                           "hindi",   False),
]

added = 0
skipped = 0
for name, url, rss, lang, active in REGIONAL:
    if name in existing_names:
        skipped += 1
        continue
    db.add(Website(name=name, url=url, rss_url=rss, language=lang, is_active=active))
    existing_names.add(name)
    added += 1

db.commit()
db.close()

from collections import Counter
langs = Counter(r[3] for r in REGIONAL if r[0] not in {r[0] for r in REGIONAL[:0]})
print(f"✓ Added {added} regional websites, skipped {skipped} duplicates.")
print("Languages covered: Bengali, Tamil, Telugu, Malayalam, Kannada, Marathi, Gujarati,")
print("  Punjabi, Odia, Assamese, Urdu, Konkani, Nepali, Manipuri, Mizo, Kashmiri, Hindi regional")
