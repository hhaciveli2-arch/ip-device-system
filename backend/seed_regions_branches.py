from backend.models import db, Region, Branch
from backend.app import app

# Bölgeler ve alt şubeler
data = {
    "Lefkoşa": [
        "Polis Genel Müdürlüğü",
        "Lefkoşa Polis Müdürlüğü",
        "Polis Okulu Müdürlüğü",
        "PÖH Müdürlüğü",
        "Narkotik - Mali Şube",
        "Alayköy Karakolu",
        "Demirhan Karakolu",
        "Gönyeli Karakolu (Polis Okulu/Gönyeli Karakolu)",
        "Akıncılar Karakolu",
        "Lefkoşa Sanayi İtfaiye",
        "Lefkoşa Araç Muayene",
        "Cumhurbaşkanlık",
        "KKTC Meclis"
    ],
    "Gazimağusa": [
        "Gazimağusa Polis Müdürlüğü",
        "Mağusa Limanı",
        "Mağusa Araç Muayene / İtfaiye",
        "Dörtyol / Mobil Karakol",
        "Geçitkale Karakolu",
        "Beyarmudu Karakolu",
        "Derinya KGK"
    ],
    "Girne": [
        "Girne Polis Müdürlüğü",
        "Girne Limanı",
        "Lapta Karakolu",
        "Esentepe Karakolu",
        "Çamlıbel Karakolu",
        "Boğaz Karakolu",
        "Girne İtfaye"
    ],
    "Güzelyurt": [
        "Güzelyurt Polis Müdürlüğü",
        "Lefke Karakolu",
        "Güzelyurt İtfaiye Amirliği",
        "Gemikonağı İtfaiye",
        "Bostancı KGK",
        "Yeşilırmak KGK"
    ],
    "İskele": [
        "İskele Polis Müdürlüğü",
        "Ziyamet Karakolu",
        "Dipkarpaz Karakolu",
        "Tatlısu Karakolu",
        "Karpaz Gate Marina"
    ],
    "Ercan Havalimanı": [],
    "Girne Limanı": [],
    "Gazimağusa Limanı": [],
    "Karpaz Gate Marina": [],
    "Metehan KGK": [],
    "Lokmacı KGK": [],
    "Ledra Palace KGK": [],
    "Beyarmudu KGK": [],
    "Akyar KGK": [],
    "Bostancı KGK": [],
    "Yeşilırmak KGK": [],
    "Aplıç KGK": [],
    "Derinya KGK": []
}

with app.app_context():
    db.drop_all()
    db.create_all()

    for region_name, branches in data.items():
        region = Region(name=region_name)
        db.session.add(region)
        db.session.flush()  # ID almak için

        for branch_name in branches:
            branch = Branch(name=branch_name, region_id=region.id)
            db.session.add(branch)

    db.session.commit()
    print("✅ Regions ve Branches başarıyla eklendi.")
