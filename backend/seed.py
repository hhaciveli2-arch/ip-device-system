from flask import Flask
from backend.models import db, User, Region, Branch, IpPool
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pgm_system.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()

    # demo kullanıcı
    db.session.add(User(sicil_no="1001", password=generate_password_hash("12345")))

    # bölgeler/şubeler
    lef = Region(name="Lefkoşa"); mag = Region(name="Mağusa")
    db.session.add_all([lef, mag]); db.session.flush()
    db.session.add_all([
        Branch(name="Lefkoşa Merkez", region_id=lef.id),
        Branch(name="Lefkoşa Terminal", region_id=lef.id),
        Branch(name="Mağusa Merkez", region_id=mag.id),
    ])

    # boş IP havuzu
    for ip in ["192.168.1.10","192.168.1.11","192.168.1.12"]:
        db.session.add(IpPool(ip_address=ip, is_assigned=False))

    db.session.commit()
    print("✅ Veritabanı kuruldu ve tohum veriler eklendi.")
