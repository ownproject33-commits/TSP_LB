import logging
import io
import tempfile
import csv
from flask import Flask, request, jsonify, render_template, send_file, Response
from database import *

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import PageBreak
import io


# --------------------------------------------------
# LOGGING CONFIG
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger("PG_SYSTEM")


# --------------------------------------------------
# APP INIT
# --------------------------------------------------

app = Flask(__name__)

init_db()


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():

    logger.info("Dashboard opened")

    return render_template("index.html")


# --------------------------------------------------
# ADD FLOOR
# --------------------------------------------------

@app.route("/add_floor", methods=["POST"])
def add_floor_api():

    try:

        data = request.get_json()

        floor = data.get("floor")

        if not floor:
            return jsonify({"success": False, "error": "Floor missing"})

        success = add_floor(floor)

        return jsonify({"success": success})

    except Exception as e:

        logger.error(f"add_floor error: {e}")

        return jsonify({"success": False})


# --------------------------------------------------
# DELETE FLOOR
# --------------------------------------------------

@app.route("/delete_floor", methods=["POST"])
def delete_floor_api():

    try:

        data = request.get_json()

        floor = data.get("floor")

        success = delete_floor(floor)

        return jsonify({"success": success})

    except Exception as e:

        logger.error(f"delete_floor error: {e}")

        return jsonify({"success": False})


# --------------------------------------------------
# ADD ROOM
# --------------------------------------------------

@app.route("/add_room", methods=["POST"])
def add_room_api():

    try:

        data = request.get_json()

        floor = data.get("floor")
        room = data.get("room")

        success = create_room(floor, room)

        return jsonify({"success": success})

    except Exception as e:

        logger.error(f"add_room error: {e}")

        return jsonify({"success": False})


# --------------------------------------------------
# DELETE ROOM
# --------------------------------------------------

@app.route("/delete_room", methods=["POST"])
def delete_room_api():

    try:

        data = request.get_json()

        floor = data.get("floor")
        room = data.get("room")

        success = delete_room(floor, room)

        return jsonify({"success": success})

    except Exception as e:

        logger.error(f"delete_room error: {e}")

        return jsonify({"success": False})


# --------------------------------------------------
# ADD BEDS
# --------------------------------------------------

@app.route("/add_beds", methods=["POST"])
def add_beds_api():

    try:

        data = request.get_json()

        floor = data.get("floor")
        room = data.get("room")
        beds = int(data.get("beds"))

        success = add_beds(floor, room, beds)

        return jsonify({"success": success})

    except Exception as e:

        logger.error(f"add_beds error: {e}")

        return jsonify({"success": False})


# --------------------------------------------------
# DELETE BED
# --------------------------------------------------

@app.route("/delete_bed", methods=["POST"])
def delete_bed_api():

    try:

        data = request.get_json()

        floor = data.get("floor")
        room = data.get("room")
        bed = data.get("bed")

        success = delete_bed(floor, room, bed)

        return jsonify({"success": success})

    except Exception as e:

        logger.error(f"delete_bed error: {e}")

        return jsonify({"success": False})


# --------------------------------------------------
# GET ALL BEDS
# --------------------------------------------------

@app.route("/beds")
def get_all_beds():

    try:

        rows = get_beds()

        result = []

        for row in rows:

            result.append({

                "id": row["id"],
                "floor": row["floor"],
                "room": row["room"],
                "bed": row["bed"],

                "tenant": row["tenant_name"],
                "phone": row["phone"],
                "join_date": row["checkin_date"]

            })

        return jsonify(result)

    except Exception as e:

        logger.error(f"get_beds error: {e}")

        return jsonify([])


# --------------------------------------------------
# GET TENANT PROFILE
# --------------------------------------------------

@app.route("/tenant/<int:bed_id>")
def tenant_profile(bed_id):

    try:

        tenant = get_tenant(bed_id)

        if not tenant:
            return jsonify({})

        return jsonify({

            "tenant_name": tenant["tenant_name"],
            "phone": tenant["phone"],
            "email": tenant["email"],
            "father_name": tenant["father_name"],
            "mother_name": tenant["mother_name"],
            "address": tenant["address"],
            "street": tenant["street"],
            "area": tenant["area"],
            "pincode": tenant["pincode"],
            "dob": tenant["dob"],
            "aadhar_number": tenant["aadhar_number"],
            "office_name": tenant["office_name"],
            "office_address": tenant["office_address"],
            "deposit": tenant["deposit"],
            "rent": tenant["rent"],
            "room": tenant["room"],
            "bed": tenant["bed"],
            "room_type": tenant["room_type"],
            "checkin_date": tenant["checkin_date"],
            "emergency_name": tenant["emergency_name"],
            "emergency_phone": tenant["emergency_phone"],
            "emergency_relation": tenant["emergency_relation"]

        })

    except Exception as e:

        logger.error(f"tenant profile error: {e}")

        return jsonify({})


# --------------------------------------------------
# ADD TENANT
# --------------------------------------------------

@app.route("/add_tenant", methods=["POST"])
def add_pg_tenant():

    try:

        data = {

            "name": request.form.get("name"),
            "father": request.form.get("father"),
            "mother": request.form.get("mother"),

            "address": request.form.get("address"),
            "street": request.form.get("street"),
            "area": request.form.get("area"),
            "pincode": request.form.get("pincode"),

            "aadhar_number": request.form.get("aadhar_number"),
            "dob": request.form.get("dob"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),

            "office_name": request.form.get("office_name"),
            "office_address": request.form.get("office_address"),

            "deposit": request.form.get("deposit"),
            "rent": request.form.get("rent"),

            "room_type": request.form.get("room_type"),
            "checkin": request.form.get("checkin"),

            "emergency_name": request.form.get("emergency_name"),
            "emergency_phone": request.form.get("emergency_phone"),
            "emergency_relation": request.form.get("emergency_relation"),

            "floor": request.form.get("floor"),
            "room": request.form.get("room"),
            "bed": request.form.get("bed")

        }

        photo = request.files.get("photo")
        aadhar = request.files.get("aadhar")

        logger.info(f"Photo file received: {photo}")
        logger.info(f"Aadhar file received: {aadhar}")
        
        if photo:
            logger.info(f"Photo filename: {photo.filename}")
            logger.info(f"Photo content type: {photo.content_type}")
        
        if aadhar:
            logger.info(f"Aadhar filename: {aadhar.filename}")
            logger.info(f"Aadhar content type: {aadhar.content_type}")

        photo_data = photo.read() if photo else None
        aadhar_data = aadhar.read() if aadhar else None
        
        logger.info(f"Photo data size: {len(photo_data) if photo_data else 0} bytes")
        logger.info(f"Aadhar data size: {len(aadhar_data) if aadhar_data else 0} bytes")

        success = add_tenant(data, photo_data, aadhar_data)

        return jsonify({"success": success})

    except Exception as e:

        logger.error(f"add_tenant error: {e}")

        return jsonify({"success": False})
    
@app.route("/update_tenant", methods=["POST"])
def update_tenant():

    try:

        data = request.form

        photo = request.files.get("photo")
        aadhar = request.files.get("aadhar")

        logger.info(f"Update - Photo file received: {photo}")
        logger.info(f"Update - Aadhar file received: {aadhar}")
        
        if photo:
            logger.info(f"Update - Photo filename: {photo.filename}")
        
        if aadhar:
            logger.info(f"Update - Aadhar filename: {aadhar.filename}")

        photo_data = photo.read() if photo else None
        aadhar_data = aadhar.read() if aadhar else None
        
        logger.info(f"Update - Photo data size: {len(photo_data) if photo_data else 0} bytes")
        logger.info(f"Update - Aadhar data size: {len(aadhar_data) if aadhar_data else 0} bytes")

        floor = data.get("floor")
        room = data.get("room")
        bed = data.get("bed")

        conn = connect()
        cur = conn.cursor()

        # Build update query dynamically based on whether files are provided
        if photo_data or aadhar_data:
            cur.execute("""

            UPDATE rooms SET

            tenant_name=%s,
            father_name=%s,
            mother_name=%s,
            address=%s,
            street=%s,
            area=%s,
            pincode=%s,
            aadhar_number=%s,
            dob=%s,
            email=%s,
            phone=%s,
            office_name=%s,
            office_address=%s,
            deposit=%s,
            rent=%s,
            room_type=%s,
            checkin_date=%s,
            emergency_name=%s,
            emergency_phone=%s,
            emergency_relation=%s,
            photo=%s,
            aadhar=%s

            WHERE floor=%s AND room=%s AND bed=%s

            """,(
            data.get("name"),
            data.get("father"),
            data.get("mother"),
            data.get("address"),
            data.get("street"),
            data.get("area"),
            data.get("pincode"),
            data.get("aadhar_number"),
            data.get("dob"),
            data.get("email"),
            data.get("phone"),
            data.get("office_name"),
            data.get("office_address"),
            data.get("deposit"),
            data.get("rent"),
            data.get("room_type"),
            data.get("checkin"),
            data.get("emergency_name"),
            data.get("emergency_phone"),
            data.get("emergency_relation"),
            psycopg2.Binary(photo_data) if photo_data else None,
            psycopg2.Binary(aadhar_data) if aadhar_data else None,
            floor,
            room,
            bed

            ))
        else:
            cur.execute("""

            UPDATE rooms SET

            tenant_name=%s,
            father_name=%s,
            mother_name=%s,
            address=%s,
            street=%s,
            area=%s,
            pincode=%s,
            aadhar_number=%s,
            dob=%s,
            email=%s,
            phone=%s,
            office_name=%s,
            office_address=%s,
            deposit=%s,
            rent=%s,
            room_type=%s,
            checkin_date=%s,
            emergency_name=%s,
            emergency_phone=%s,
            emergency_relation=%s

            WHERE floor=%s AND room=%s AND bed=%s

            """,(
            data.get("name"),
            data.get("father"),
            data.get("mother"),
            data.get("address"),
            data.get("street"),
            data.get("area"),
            data.get("pincode"),
            data.get("aadhar_number"),
            data.get("dob"),
            data.get("email"),
            data.get("phone"),
            data.get("office_name"),
            data.get("office_address"),
            data.get("deposit"),
            data.get("rent"),
            data.get("room_type"),
            data.get("checkin"),
            data.get("emergency_name"),
            data.get("emergency_phone"),
            data.get("emergency_relation"),
            floor,
            room,
            bed

            ))

        conn.commit()

        return jsonify({"success":True})

    except Exception as e:

        logger.error(f"update_tenant error: {e}")
        print(e)

        return jsonify({"success":False})


# --------------------------------------------------
# REMOVE TENANT
# --------------------------------------------------

@app.route("/remove_tenant", methods=["POST"])
def remove_pg_tenant():

    try:

        data = request.get_json()

        floor = data.get("floor")
        room = data.get("room")
        bed = data.get("bed")

        success = remove_tenant(floor, room, bed)

        return jsonify({"success": success})

    except Exception as e:

        logger.error(f"remove_tenant error: {e}")

        return jsonify({"success": False})


# --------------------------------------------------
# GET PHOTO
# --------------------------------------------------

@app.route("/photo/<int:bed_id>")
def get_photo(bed_id):

    try:

        tenant = get_tenant(bed_id)

        if tenant and tenant["photo"]:

            return send_file(
                io.BytesIO(tenant["photo"]),
                mimetype="image/jpeg"
            )

        return "", 404

    except Exception as e:

        logger.error(f"photo error: {e}")

        return "", 500


# --------------------------------------------------
# GET AADHAAR
# --------------------------------------------------

@app.route("/aadhar/<int:bed_id>")
def get_aadhar(bed_id):

    try:

        tenant = get_tenant(bed_id)

        if tenant and tenant["aadhar"]:

            return send_file(
                io.BytesIO(tenant["aadhar"]),
                mimetype="image/jpeg"
            )

        return "", 404

    except Exception as e:

        logger.error(f"aadhar error: {e}")

        return "", 500


# --------------------------------------------------
# EXPORT ALL TENANTS CSV
# --------------------------------------------------

@app.route("/export/all_tenants/csv")
def export_all_tenants_csv():
    try:
        conn = connect()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT tenant_name, father_name, mother_name, address, street, area, pincode,
                   aadhar_number, dob, email, phone, office_name, office_address,
                   deposit, rent, floor, room, bed, room_type, checkin_date,
                   emergency_name, emergency_phone, emergency_relation
            FROM rooms 
            WHERE tenant_name IS NOT NULL AND tenant_name != ''
            ORDER BY floor, room, bed
        """)
        
        tenants = cur.fetchall()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Tenant Name', 'Father Name', 'Mother Name', 'Address', 'Street', 'Area', 'Pincode',
                        'Aadhar Number', 'DOB', 'Email', 'Phone', 'Office Name', 'Office Address',
                        'Deposit', 'Rent', 'Floor', 'Room', 'Bed', 'Room Type', 'Checkin Date',
                        'Emergency Name', 'Emergency Phone', 'Emergency Relation'])
        
        # Data
        for tenant in tenants:
            writer.writerow(tenant)
        
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=all_tenants.csv'}
        )
        
    except Exception as e:
        logger.error(f"Export all tenants CSV error: {e}")
        return "Error exporting data", 500


# --------------------------------------------------
# EXPORT ALL TENANTS PDF
# --------------------------------------------------

@app.route("/export/all_tenants/pdf")
def export_all_tenants_pdf():
    try:
        conn = connect()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT tenant_name, father_name, mother_name, address, street, area, pincode,
                   aadhar_number, dob, email, phone, office_name, office_address,
                   deposit, rent, floor, room, bed, room_type, checkin_date,
                   emergency_name, emergency_phone, emergency_relation
            FROM rooms 
            WHERE tenant_name IS NOT NULL AND tenant_name != ''
            ORDER BY floor, room, bed
        """)
        
        tenants = cur.fetchall()
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Title
        elements.append(Paragraph("All Tenants Report", styles['Title']))
        elements.append(Spacer(1, 20))
        
        # Table data
        data = [['Tenant Name', 'Floor', 'Room', 'Bed', 'Phone', 'Email', 'Checkin Date', 'Rent']]
        
        for tenant in tenants:
            data.append([
                tenant[0],  # tenant_name
                tenant[15], # floor
                tenant[16], # room
                tenant[17], # bed
                tenant[10], # phone
                tenant[9],  # email
                tenant[18], # checkin_date
                f"₹{tenant[14]}"  # rent
            ])
        
        table = Table(data, colWidths=[80, 40, 40, 30, 60, 80, 50, 40])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name='all_tenants.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Export all tenants PDF error: {e}")
        return "Error exporting data", 500


# --------------------------------------------------
# EXPORT FORMER TENANTS CSV
# --------------------------------------------------

@app.route("/export/former_tenants/csv")
def export_former_tenants_csv():
    try:
        conn = connect()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT tenant_name, father_name, mother_name, address, street, area, pincode,
                   aadhar_number, dob, email, phone, office_name, office_address,
                   deposit, rent, floor, room, bed, room_type, checkin_date, leaving_date,
                   emergency_name, emergency_phone, emergency_relation
            FROM former_tenants 
            ORDER BY leaving_date DESC, created_at DESC
        """)
        
        tenants = cur.fetchall()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Tenant Name', 'Father Name', 'Mother Name', 'Address', 'Street', 'Area', 'Pincode',
                        'Aadhar Number', 'DOB', 'Email', 'Phone', 'Office Name', 'Office Address',
                        'Deposit', 'Rent', 'Floor', 'Room', 'Bed', 'Room Type', 'Checkin Date', 'Leaving Date',
                        'Emergency Name', 'Emergency Phone', 'Emergency Relation'])
        
        # Data
        for tenant in tenants:
            writer.writerow(tenant)
        
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=former_tenants.csv'}
        )
        
    except Exception as e:
        logger.error(f"Export former tenants CSV error: {e}")
        return "Error exporting data", 500


# --------------------------------------------------
# EXPORT FORMER TENANTS PDF
# --------------------------------------------------

@app.route("/export/former_tenants/pdf")
def export_former_tenants_pdf():
    try:
        conn = connect()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT tenant_name, father_name, mother_name, address, street, area, pincode,
                   aadhar_number, dob, email, phone, office_name, office_address,
                   deposit, rent, floor, room, bed, room_type, checkin_date, leaving_date,
                   emergency_name, emergency_phone, emergency_relation
            FROM former_tenants 
            ORDER BY leaving_date DESC, created_at DESC
        """)
        
        tenants = cur.fetchall()
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Title
        elements.append(Paragraph("Former Tenants Report", styles['Title']))
        elements.append(Spacer(1, 20))
        
        # Table data
        data = [['Tenant Name', 'Floor', 'Room', 'Bed', 'Phone', 'Email', 'Checkin Date', 'Leaving Date', 'Rent']]
        
        for tenant in tenants:
            data.append([
                tenant[0],  # tenant_name
                tenant[15], # floor
                tenant[16], # room
                tenant[17], # bed
                tenant[10], # phone
                tenant[9],  # email
                tenant[18], # checkin_date
                tenant[19], # leaving_date
                f"₹{tenant[14]}"  # rent
            ])
        
        table = Table(data, colWidths=[80, 40, 40, 30, 60, 80, 50, 50, 40])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name='former_tenants.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Export former tenants PDF error: {e}")
        return "Error exporting data", 500


# --------------------------------------------------
# DOWNLOAD TENANT PDF
# --------------------------------------------------

@app.route("/download_tenant/<int:bed_id>")
def download_tenant(bed_id):

    tenant = get_tenant(bed_id)

    if not tenant:
        return "Tenant not found", 404

    buffer = io.BytesIO()

    styles = getSampleStyleSheet()
    elements = []

    # -------------------------
    # HEADER
    # -------------------------

    elements.append(Paragraph("PG TENANT REGISTRATION FORM", styles['Title']))
    elements.append(Spacer(1, 20))

    photo = ""

    if tenant["photo"]:
        photo = Image(io.BytesIO(tenant["photo"]), 1.8*inch, 2*inch)

    header_data = [

        ["Name", tenant["tenant_name"], photo],
        ["Phone", tenant["phone"], ""],
        ["Email", tenant["email"], ""],

    ]

    header_table = Table(header_data, colWidths=[120, 260, 120])

    header_table.setStyle(TableStyle([
        ("GRID",(0,0),(1,-1),1,colors.grey),
        ("SPAN",(2,0),(2,2)),
        ("ALIGN",(2,0),(2,2),"CENTER"),
        ("VALIGN",(2,0),(2,2),"MIDDLE")
    ]))

    elements.append(header_table)
    elements.append(Spacer(1,20))

    # -------------------------
    # PERSONAL DETAILS
    # -------------------------

    personal_data = [

        ["Name", tenant["tenant_name"]],
        ["Father Name", tenant["father_name"]],
        ["Mother Name", tenant["mother_name"]],
        ["DOB", tenant["dob"]],
        ["Phone", tenant["phone"]],
        ["Email", tenant["email"]],

    ]

    table = Table(personal_data, colWidths=[200,350])

    table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),1,colors.grey),
        ("BACKGROUND",(0,0),(0,-1),colors.lightgrey)
    ]))

    elements.append(Paragraph("Personal Details", styles['Heading2']))
    elements.append(table)
    elements.append(Spacer(1,20))

    # -------------------------
    # ADDRESS DETAILS
    # -------------------------

    address_data = [

        ["Address", tenant["address"]],
        ["Street", tenant["street"]],
        ["Area", tenant["area"]],
        ["Pincode", tenant["pincode"]],
        ["Aadhar Number", tenant["aadhar_number"]]

    ]

    table = Table(address_data, colWidths=[200,350])

    table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),1,colors.grey),
        ("BACKGROUND",(0,0),(0,-1),colors.lightgrey)
    ]))

    elements.append(Paragraph("Address Details", styles['Heading2']))
    elements.append(table)
    elements.append(Spacer(1,20))

    # -------------------------
    # STAY DETAILS
    # -------------------------

    stay_data = [

        ["Room", tenant["room"]],
        ["Bed", tenant["bed"]],
        ["Room Type", tenant["room_type"]],
        ["Checkin Date", tenant["checkin_date"]]

    ]

    table = Table(stay_data, colWidths=[200,350])

    table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),1,colors.grey),
        ("BACKGROUND",(0,0),(0,-1),colors.lightgrey)
    ]))

    elements.append(Paragraph("Stay Details", styles['Heading2']))
    elements.append(table)
    elements.append(Spacer(1,20))

    # -------------------------
    # PAYMENT DETAILS
    # -------------------------

    payment_data = [

        ["Deposit", tenant["deposit"]],
        ["Rent", tenant["rent"]]

    ]

    table = Table(payment_data, colWidths=[200,350])

    table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),1,colors.grey),
        ("BACKGROUND",(0,0),(0,-1),colors.lightgrey)
    ]))

    elements.append(Paragraph("Payment Details", styles['Heading2']))
    elements.append(table)
    elements.append(Spacer(1,20))

    # -------------------------
    # EMERGENCY CONTACT
    # -------------------------

    emergency_data = [

        ["Emergency Name", tenant["emergency_name"]],
        ["Emergency Phone", tenant["emergency_phone"]],
        ["Relation", tenant["emergency_relation"]]

    ]

    table = Table(emergency_data, colWidths=[200,350])

    table.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),1,colors.grey),
        ("BACKGROUND",(0,0),(0,-1),colors.lightgrey)
    ]))

    elements.append(Paragraph("Emergency Contact", styles['Heading2']))
    elements.append(table)
    elements.append(Spacer(1,25))

    # -------------------------
    # AADHAAR IMAGE
    # -------------------------

    if tenant["aadhar"]:

        elements.append(PageBreak())

        elements.append(Paragraph("Aadhaar Card", styles['Title']))
        elements.append(Spacer(1,20))

        aadhar = Image(io.BytesIO(tenant["aadhar"]))

        aadhar.drawHeight = 4 * inch
        aadhar.drawWidth = 7 * inch

        elements.append(aadhar)
        elements.append(Spacer(1,25))

    # -------------------------
    # SIGNATURE SECTION
    # -------------------------

    signature_data = [

        ["Tenant Signature", "", "Owner Signature"]

    ]

    sign_table = Table(signature_data, colWidths=[200,200,200])

    sign_table.setStyle(TableStyle([
        ("LINEABOVE",(0,0),(0,0),1,colors.black),
        ("LINEABOVE",(2,0),(2,0),1,colors.black),
        ("ALIGN",(0,0),(2,0),"CENTER")
    ]))

    elements.append(sign_table)

    doc = SimpleDocTemplate(buffer, pagesize=A4)
    doc.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{tenant['tenant_name']}_tenant.pdf",
        mimetype="application/pdf"
    )

@app.route("/favicon.ico")
def favicon():
    return "", 204

# --------------------------------------------------
# START SERVER
# --------------------------------------------------

if __name__ == "__main__":

    logger.info("PG Management Server Started")

    app.run(debug=True)