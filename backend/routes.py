from flask import Blueprint, jsonify, request, render_template, send_file
from flask_login import login_required, current_user
from backend.models import db, Region, Branch, Device, IpPool, AuditLog
from io import BytesIO
from datetime import datetime

routes = Blueprint("routes", __name__)

# ---- Yardımcılar ------------------------------------------------------------
def _getv(obj, *candidates):
    """obj üzerinde sırasıyla aday alan adlarını dener; ilk bulduğunu döner, yoksa ''."""
    for name in candidates:
        if hasattr(obj, name):
            val = getattr(obj, name)
            if val is not None:
                return val
    return ""

def _norm(val):
    """Boş ya da '-' gelenleri None yap."""
    if val is None:
        return None
    v = str(val).strip()
    if not v or v == "-":
        return None
    return v

def log_action(action):
    try:
        db.session.add(AuditLog(
            user_id=getattr(current_user, "id", None),
            action=action,
            timestamp=db.func.now()
        ))
        db.session.commit()
    except Exception:
        db.session.rollback()

# İstenen tablo başlıkları (sıra sabit)
ALL_COLUMNS = [
    "PGM No", "Müdürlük", "Amirlik", "Şube", "IP No", "MAC Adresi",
    "İşletim Sistemi", "PC Markası", "PC Modeli", "İşlemci",
    "Hard Disk", "RAM Boyutu", "RAM Modeli", "Bit tipi",
    "Ekran Kartı", "Ses Kartı", "Network Kartı", "Ana Kart",
    "Ekran", "Yazıcı", "Açıklama"
]

# ---- Sayfa ------------------------------------------------------------------
@routes.route("/dashboard")
@login_required
def dashboard():
    regions = Region.query.order_by(Region.name).all()
    return render_template("dashboard.html", regions=regions, all_columns=ALL_COLUMNS)

# ---- Bölge/Şube -------------------------------------------------------------
@routes.route("/branches")
@login_required
def get_branches():
    region_id = request.args.get("region_id", type=int)
    q = Branch.query
    if region_id:
        q = q.filter(Branch.region_id == region_id)
    items = q.order_by(Branch.name).all()
    return jsonify([{"id": b.id, "name": b.name} for b in items])

# ---- Cihaz listeleme (JSON) -------------------------------------------------
@routes.route("/devices")
@login_required
def get_devices():
    region_id = request.args.get("region_id", type=int)
    branch_id = request.args.get("branch_id", type=int)
    qtext = request.args.get("q", "").strip()

    q = Device.query

    # Şube filtresi (Device.branch_id yok; 'sube' metnine göre)
    if branch_id:
        br = Branch.query.get(branch_id)
        if br is not None and hasattr(Device, "sube"):
            q = q.filter(Device.sube.ilike(f"%{br.name}%"))

    # Serbest arama
    if qtext:
        like = f"%{qtext}%"
        from sqlalchemy import or_
        filters = []
        for field in ("pgm_no","ip_no","mac_adresi","isletim_sistemi",
                      "pc_markasi","pc_modeli","islemci","aciklama","sube",
                      "mudurluk","amirlik"):
            if hasattr(Device, field):
                filters.append(getattr(Device, field).ilike(like))
        if filters:
            q = q.filter(or_(*filters))

    devices = q.all()

    rows = []
    for d in devices:
        rows.append({
            "_id": getattr(d, "id", None),
            "PGM No":          _getv(d, "pgm_no"),
            "Müdürlük":        _getv(d, "mudurluk"),
            "Amirlik":         _getv(d, "amirlik"),
            "Şube":            _getv(d, "sube"),
            "IP No":           _getv(d, "ip_no"),
            "MAC Adresi":      _getv(d, "mac_adresi"),
            "İşletim Sistemi": _getv(d, "isletim_sistemi"),
            "PC Markası":      _getv(d, "pc_markasi"),
            "PC Modeli":       _getv(d, "pc_modeli"),
            "İşlemci":         _getv(d, "islemci"),
            "Hard Disk":       _getv(d, "hard_disk"),
            "RAM Boyutu":      _getv(d, "ram_boyutu"),
            "RAM Modeli":      _getv(d, "ram_modeli"),
            "Bit tipi":        _getv(d, "bit_tipi"),
            "Ekran Kartı":     _getv(d, "ekran_karti"),
            "Ses Kartı":       _getv(d, "ses_karti"),
            "Network Kartı":   _getv(d, "network_karti"),
            "Ana Kart":        _getv(d, "ana_kart"),
            "Ekran":           _getv(d, "ekran"),
            "Yazıcı":          _getv(d, "yazici"),
            "Açıklama":        _getv(d, "aciklama"),
        })

    return jsonify({"columns": ALL_COLUMNS, "rows": rows})

# ---- Export (Excel / PDF) ---------------------------------------------------
@routes.route("/export")
@login_required
def export_devices():
    fmt = request.args.get("format", "excel")
    cols = request.args.get("cols")
    if cols:
        chosen = [c.strip() for c in cols.split(",") if c.strip() in ALL_COLUMNS]
        columns = chosen if chosen else ALL_COLUMNS
    else:
        columns = ALL_COLUMNS

    # /devices ile aynı filtre mantığı
    region_id = request.args.get("region_id", type=int)
    branch_id = request.args.get("branch_id", type=int)
    qtext = request.args.get("q", "").strip()

    q = Device.query
    if branch_id:
        br = Branch.query.get(branch_id)
        if br is not None and hasattr(Device, "sube"):
            q = q.filter(Device.sube.ilike(f"%{br.name}%"))
    if qtext:
        like = f"%{qtext}%"
        from sqlalchemy import or_
        filters = []
        for field in ("pgm_no","ip_no","mac_adresi","isletim_sistemi",
                      "pc_markasi","pc_modeli","islemci","aciklama",
                      "sube","mudurluk","amirlik"):
            if hasattr(Device, field):
                filters.append(getattr(Device, field).ilike(like))
        if filters:
            q = q.filter(or_(*filters))

    devices = q.all()

    rows = []
    for d in devices:
        row = {
            "PGM No":          _getv(d, "pgm_no"),
            "Müdürlük":        _getv(d, "mudurluk"),
            "Amirlik":         _getv(d, "amirlik"),
            "Şube":            _getv(d, "sube"),
            "IP No":           _getv(d, "ip_no"),
            "MAC Adresi":      _getv(d, "mac_adresi"),
            "İşletim Sistemi": _getv(d, "isletim_sistemi"),
            "PC Markası":      _getv(d, "pc_markasi"),
            "PC Modeli":       _getv(d, "pc_modeli"),
            "İşlemci":         _getv(d, "islemci"),
            "Hard Disk":       _getv(d, "hard_disk"),
            "RAM Boyutu":      _getv(d, "ram_boyutu"),
            "RAM Modeli":      _getv(d, "ram_modeli"),
            "Bit tipi":        _getv(d, "bit_tipi"),
            "Ekran Kartı":     _getv(d, "ekran_karti"),
            "Ses Kartı":       _getv(d, "ses_karti"),
            "Network Kartı":   _getv(d, "network_karti"),
            "Ana Kart":        _getv(d, "ana_kart"),
            "Ekran":           _getv(d, "ekran"),
            "Yazıcı":          _getv(d, "yazici"),
            "Açıklama":        _getv(d, "aciklama"),
        }
        rows.append({k: row.get(k, "") for k in columns})

    if fmt == "excel":
        import pandas as pd
        from openpyxl import Workbook  # noqa
        buf = BytesIO()
        df = pd.DataFrame(rows, columns=columns)
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Cihazlar")
        buf.seek(0)
        filename = f"cihazlar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        log_action("export_excel")
        return send_file(buf, as_attachment=True, download_name=filename,
                         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    elif fmt == "pdf":
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=landscape(A4))
        data = [columns] + [[str(r.get(c, "")) for c in columns] for r in rows]
        table = Table(data, repeatRows=1)
        style = TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0d6efd")),
            ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
            ("ALIGN",      (0,0), (-1,-1), "LEFT"),
            ("GRID",       (0,0), (-1,-1), 0.25, colors.grey),
            ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0), (-1,0), 10),
            ("FONTSIZE",   (0,1), (-1,-1), 8),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.HexColor("#f7f7f7")]),
        ])
        table.setStyle(style)
        doc.build([table])
        buf.seek(0)
        filename = f"cihazlar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        log_action("export_pdf")
        return send_file(buf, as_attachment=True, download_name=filename,
                         mimetype="application/pdf")

    return jsonify({"error": "unsupported_format"}), 400

# ---- Boş IP listesi ---------------------------------------------------------
@routes.route("/empty-ips")
@login_required
def empty_ips():
    ips = IpPool.query.filter_by(is_assigned=False).order_by(IpPool.ip_address).all()
    return jsonify([{"id": i.id, "ip": i.ip_address} for i in ips])

# ---- PGM / Açıklama güncelle ------------------------------------------------
@routes.route("/device/<int:dev_id>/update", methods=["PATCH"])
@login_required
def update_device(dev_id):
    d = db.session.get(Device, dev_id)
    if not d:
        return jsonify({"error": "not found"}), 404
    payload = request.get_json(force=True) or {}
    if "pgm_no" in payload:
        d.pgm_no = _norm(payload["pgm_no"])
    if "aciklama" in payload:
        d.aciklama = _norm(payload["aciklama"])
    try:
        db.session.commit()
        log_action(f"device_update:{dev_id}")
        return jsonify({"ok": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "update_failed", "detail": str(e)}), 500

# ---- Sil (IP’yi havuza geri bırak) -----------------------------------------
@routes.route("/device/<int:dev_id>", methods=["DELETE"])
@login_required
def delete_device(dev_id):
    d = db.session.get(Device, dev_id)
    if not d:
        return jsonify({"error": "not_found"}), 404

    ip_before = (d.ip_no or "").strip()
    try:
        db.session.delete(d)
        db.session.flush()

        if ip_before:
            pool = IpPool.query.filter_by(ip_address=ip_before).first()
            if pool:
                pool.is_assigned = False
            else:
                db.session.add(IpPool(ip_address=ip_before, is_assigned=False))

        db.session.commit()
        log_action(f"device_delete:{dev_id}")
        return jsonify({"ok": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "delete_failed", "detail": str(e)}), 500

# ---- Manuel cihaz ekle ------------------------------------------------------
@routes.route("/device", methods=["POST"])
@login_required
def create_device():
    payload = request.get_json(force=True) or {}
    d = Device(
        pgm_no=_norm(payload.get("pgm_no")),
        mudurluk=_norm(payload.get("mudurluk")),
        amirlik=_norm(payload.get("amirlik")),
        sube=_norm(payload.get("sube")),
        ip_no=_norm(payload.get("ip_no")),
        mac_adresi=_norm(payload.get("mac_adresi")),
        isletim_sistemi=_norm(payload.get("isletim_sistemi")),
        pc_markasi=_norm(payload.get("pc_markasi")),
        pc_modeli=_norm(payload.get("pc_modeli")),
        islemci=_norm(payload.get("islemci")),
        hard_disk=_norm(payload.get("hard_disk")),
        ram_boyutu=_norm(payload.get("ram_boyutu")),
        ram_modeli=_norm(payload.get("ram_modeli")),
        bit_tipi=_norm(payload.get("bit_tipi")),
        ekran_karti=_norm(payload.get("ekran_karti")),
        ses_karti=_norm(payload.get("ses_karti")),
        network_karti=_norm(payload.get("network_karti")),
        ana_kart=_norm(payload.get("ana_kart")),
        ekran=_norm(payload.get("ekran")),
        yazici=_norm(payload.get("yazici")),
        aciklama=_norm(payload.get("aciklama")),
    )
    try:
        db.session.add(d)
        db.session.flush()
        if d.ip_no:
            pool = IpPool.query.filter_by(ip_address=d.ip_no).first()
            if pool:
                pool.is_assigned = True
            else:
                db.session.add(IpPool(ip_address=d.ip_no, is_assigned=True))
        db.session.commit()
        log_action(f"device_create:{d.id}")
        return jsonify({"ok": True, "id": d.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "create_failed", "detail": str(e)}), 500

# ---- Mock: Şimdi Tara (WMIC gateway geldiğinde gerçeklenecek) --------------
@routes.route("/scan-now", methods=["POST"])
@login_required
def scan_now():
    target = (request.get_json(silent=True) or {}).get("target")
    log_action(f"scan_now:{target or 'N/A'}")
    return jsonify({"ok": True, "message": "Gateway bağlandığında burada gerçek WMIC taraması olacak."})
# ---- WMIC Upsert ------------------------------------------------------------
@routes.route("/wmic/upsert", methods=["POST"])
@login_required
def wmic_upsert():
    """
    Collector (wmic_collector.py) tarafından gönderilen veriyi DB’ye kaydeder veya günceller.
    MOCK_MODE=true iken burası çalışmaz; sadece MOCK_MODE=false iken devreye girer.
    """
    import os
    from backend.models import Device, IpPool

    api_key_required = os.environ.get("WMIC_API_KEY")
    if api_key_required:
        sent = request.headers.get("X-API-Key")
        if sent != api_key_required:
            return jsonify({"error": "forbidden"}), 403

    payload = request.get_json(force=True) or {}

    # Eşleşme kriterleri
    match_ip  = _norm(payload.get("ip_no") or payload.get("IP No"))
    match_pgm = _norm(payload.get("pgm_no") or payload.get("PGM No"))
    hostname  = _norm(payload.get("hostname") or payload.get("HOSTNAME"))

    q = Device.query
    if match_ip:
        q = q.filter(Device.ip_no == match_ip)
    elif match_pgm:
        q = q.filter(Device.pgm_no == match_pgm)
    elif hostname and hasattr(Device, "aciklama"):
        q = q.filter(Device.aciklama.ilike(f"%{hostname}%"))

    dev = q.first()

    mapped = {
        "pgm_no":          _norm(payload.get("pgm_no") or payload.get("PGM No")),
        "mudurluk":        _norm(payload.get("mudurluk") or payload.get("Müdürlük")),
        "amirlik":         _norm(payload.get("amirlik") or payload.get("Amirlik")),
        "sube":            _norm(payload.get("sube") or payload.get("Şube")),
        "ip_no":           _norm(payload.get("ip_no") or payload.get("IP No")),
        "mac_adresi":      _norm(payload.get("mac_adresi") or payload.get("MAC Adresi")),
        "isletim_sistemi": _norm(payload.get("isletim_sistemi") or payload.get("İşletim Sistemi")),
        "pc_markasi":      _norm(payload.get("pc_markasi") or payload.get("PC Markası")),
        "pc_modeli":       _norm(payload.get("pc_modeli") or payload.get("PC Modeli")),
        "islemci":         _norm(payload.get("islemci") or payload.get("İşlemci")),
        "hard_disk":       _norm(payload.get("hard_disk") or payload.get("Hard Disk")),
        "ram_boyutu":      _norm(payload.get("ram_boyutu") or payload.get("RAM Boyutu")),
        "ram_modeli":      _norm(payload.get("ram_modeli") or payload.get("RAM Modeli")),
        "bit_tipi":        _norm(payload.get("bit_tipi") or payload.get("Bit tipi")),
        "ekran_karti":     _norm(payload.get("ekran_karti") or payload.get("Ekran Kartı")),
        "ses_karti":       _norm(payload.get("ses_karti") or payload.get("Ses Kartı")),
        "network_karti":   _norm(payload.get("network_karti") or payload.get("Network Kartı")),
        "ana_kart":        _norm(payload.get("ana_kart") or payload.get("Ana Kart")),
        "ekran":           _norm(payload.get("ekran") or payload.get("Ekran")),
        "yazici":          _norm(payload.get("yazici") or payload.get("Yazıcı")),
        "aciklama":        _norm(payload.get("aciklama") or payload.get("Açıklama")),
    }

    try:
        if dev is None:
            # Yeni cihaz oluştur
            dev = Device(**mapped)
            db.session.add(dev)
            db.session.flush()

            if dev.ip_no:
                pool = IpPool.query.filter_by(ip_address=dev.ip_no).first()
                if pool:
                    pool.is_assigned = True
                else:
                    db.session.add(IpPool(ip_address=dev.ip_no, is_assigned=True))

            log_action(f"wmic_create:{dev.id}")
        else:
            # Güncelle
            for k, v in mapped.items():
                if v is not None:
                    setattr(dev, k, v)
            log_action(f"wmic_update:{dev.id}")

        db.session.commit()
        return jsonify({"ok": True, "id": dev.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "upsert_failed", "detail": str(e)}), 500

