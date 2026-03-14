import os
import logging
import psycopg2
from datetime import datetime
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# --------------------------------------------------
# LOAD ENV VARIABLES
# --------------------------------------------------

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL not found in .env file")

# --------------------------------------------------
# LOGGING CONFIG
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger("PG_DATABASE")

# --------------------------------------------------
# CONNECTION POOL
# --------------------------------------------------

connection_pool = psycopg2.pool.SimpleConnectionPool(
    1,
    10,
    DATABASE_URL
)

logger.info("PostgreSQL connection pool created")

# --------------------------------------------------
# CONNECTION HELPERS
# --------------------------------------------------

def connect():
    return connection_pool.getconn()

def release(conn):
    connection_pool.putconn(conn)

# --------------------------------------------------
# INITIALIZE DATABASE
# --------------------------------------------------

def init_db():

    conn = connect()
    cur = conn.cursor()

    try:

        cur.execute("""

        CREATE TABLE IF NOT EXISTS rooms(

            id SERIAL PRIMARY KEY,

            floor TEXT,
            room TEXT,
            bed TEXT,

            tenant_name TEXT,
            father_name TEXT,
            mother_name TEXT,

            address TEXT,
            street TEXT,
            area TEXT,
            pincode TEXT,

            aadhar_number TEXT,
            dob TEXT,
            email TEXT,
            phone TEXT,

            office_name TEXT,
            office_address TEXT,

            deposit TEXT,
            rent TEXT,

            room_type TEXT,
            checkin_date TEXT,

            emergency_name TEXT,
            emergency_phone TEXT,
            emergency_relation TEXT,

            photo BYTEA,
            aadhar BYTEA

        )

        """)

        cur.execute("""

        CREATE TABLE IF NOT EXISTS former_tenants (
            id SERIAL PRIMARY KEY,
            tenant_name VARCHAR(255),
            father_name VARCHAR(255),
            mother_name VARCHAR(255),
            address TEXT,
            street VARCHAR(255),
            area VARCHAR(255),
            pincode VARCHAR(20),
            aadhar_number VARCHAR(20),
            dob DATE,
            email VARCHAR(255),
            phone VARCHAR(20),
            office_name VARCHAR(255),
            office_address TEXT,
            deposit VARCHAR(20),
            rent VARCHAR(20),
            floor VARCHAR(100),
            room VARCHAR(100),
            bed VARCHAR(100),
            room_type VARCHAR(255),
            checkin_date DATE,
            leaving_date DATE,
            emergency_name VARCHAR(255),
            emergency_phone VARCHAR(20),
            emergency_relation VARCHAR(255),
            photo BYTEA,
            aadhar BYTEA,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )

        """)

        conn.commit()

        logger.info("Database initialized")

    except Exception as e:

        conn.rollback()
        logger.error(f"init_db error: {e}")

    finally:

        cur.close()
        release(conn)

# --------------------------------------------------
# ADD FLOOR
# --------------------------------------------------

def add_floor(floor):

    conn = connect()
    cur = conn.cursor()

    try:

        cur.execute(
            "SELECT id FROM rooms WHERE floor=%s AND room='' AND bed=''",
            (floor,)
        )

        if cur.fetchone():
            return True

        cur.execute(
            "INSERT INTO rooms (floor,room,bed) VALUES (%s,'','')",
            (floor,)
        )

        conn.commit()

        logger.info(f"Floor added {floor}")

        return True

    except Exception as e:

        conn.rollback()
        logger.error(e)

        return False

    finally:

        cur.close()
        release(conn)

# --------------------------------------------------
# CREATE ROOM
# --------------------------------------------------

def create_room(floor, room):

    conn = connect()
    cur = conn.cursor()

    try:

        cur.execute(
            "SELECT id FROM rooms WHERE floor=%s AND room=%s AND bed=''",
            (floor, room)
        )

        if cur.fetchone():
            return True

        cur.execute(
            "INSERT INTO rooms (floor,room,bed) VALUES (%s,%s,'')",
            (floor, room)
        )

        conn.commit()

        logger.info(f"Room created {floor}-{room}")

        return True

    except Exception as e:

        conn.rollback()
        logger.error(e)

        return False

    finally:

        cur.close()
        release(conn)

# --------------------------------------------------
# ADD BEDS
# --------------------------------------------------

def add_beds(floor, room, beds):

    conn = connect()
    cur = conn.cursor()

    try:

        for i in range(1, beds + 1):

            bed = f"Bed{i}"

            cur.execute(
                "SELECT id FROM rooms WHERE floor=%s AND room=%s AND bed=%s",
                (floor, room, bed)
            )

            if not cur.fetchone():

                cur.execute(
                    "INSERT INTO rooms (floor,room,bed) VALUES (%s,%s,%s)",
                    (floor, room, bed)
                )

        conn.commit()

        logger.info(f"{beds} beds added to {floor}-{room}")

        return True

    except Exception as e:

        conn.rollback()
        logger.error(e)

        return False

    finally:

        cur.close()
        release(conn)

# --------------------------------------------------
# GET ALL BEDS
# --------------------------------------------------

def get_beds():

    conn = connect()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:

        cur.execute("""

        SELECT *
        FROM rooms
        ORDER BY floor, room, bed

        """)

        return cur.fetchall()

    except Exception as e:

        logger.error(f"get_beds error: {e}")

        return []

    finally:

        cur.close()
        release(conn)
# --------------------------------------------------
# GET TENANT
# --------------------------------------------------

def get_tenant(bed_id):

    conn = connect()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:

        cur.execute(
            "SELECT * FROM rooms WHERE id=%s",
            (bed_id,)
        )

        return cur.fetchone()

    except Exception as e:

        logger.error(e)
        return None

    finally:

        cur.close()
        release(conn)

# --------------------------------------------------
# ADD TENANT
# --------------------------------------------------

def add_tenant(data, photo, aadhar):

    conn = connect()
    cur = conn.cursor()

    try:

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
        AND bed <> ''

        """, (

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
            psycopg2.Binary(photo) if photo else None,
            psycopg2.Binary(aadhar) if aadhar else None,
            data.get("floor"),
            data.get("room"),
            data.get("bed")

        ))

        conn.commit()

        logger.info("Tenant added successfully")

        return True

    except Exception as e:

        conn.rollback()
        logger.error(e)

        return False

    finally:

        cur.close()
        release(conn)

# --------------------------------------------------
# MOVE TENANT TO FORMER TENANTS
# --------------------------------------------------

def move_to_former_tenants(floor, room, bed):
    
    conn = connect()
    cur = conn.cursor()
    
    try:
        
        logger.info(f"Attempting to remove tenant from {floor}-{room}-{bed}")
        
        # Get tenant data before removing
        cur.execute("""
            SELECT tenant_name, father_name, mother_name, address, street, area, pincode,
                   aadhar_number, dob, email, phone, office_name, office_address,
                   deposit, rent, room_type, checkin_date, emergency_name, 
                   emergency_phone, emergency_relation, photo, aadhar
            FROM rooms 
            WHERE floor=%s AND room=%s AND bed=%s
        """, (floor, room, bed))
        
        tenant_data = cur.fetchone()
        logger.info(f"Found tenant data: {tenant_data}")
        
        if tenant_data:
            # Move to former_tenants table - reorder the values to match column order
            cur.execute("""
                INSERT INTO former_tenants (
                    tenant_name, father_name, mother_name, address, street, area, pincode,
                    aadhar_number, dob, email, phone, office_name, office_address,
                    deposit, rent, floor, room, bed, room_type, checkin_date, leaving_date,
                    emergency_name, emergency_phone, emergency_relation, photo, aadhar
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                tenant_data[0],  # tenant_name
                tenant_data[1],  # father_name
                tenant_data[2],  # mother_name
                tenant_data[3],  # address
                tenant_data[4],  # street
                tenant_data[5],  # area
                tenant_data[6],  # pincode
                tenant_data[7],  # aadhar_number
                tenant_data[8],  # dob
                tenant_data[9],  # email
                tenant_data[10], # phone
                tenant_data[11], # office_name
                tenant_data[12], # office_address
                tenant_data[13], # deposit
                tenant_data[14], # rent
                floor,           # floor
                room,            # room
                bed,             # bed
                tenant_data[15], # room_type
                tenant_data[16], # checkin_date
                datetime.now().date(), # leaving_date
                tenant_data[17], # emergency_name
                tenant_data[18], # emergency_phone
                tenant_data[19], # emergency_relation
                tenant_data[20], # photo
                tenant_data[21]  # aadhar
            ))
            
            logger.info("Data inserted into former_tenants table")
            
            # Clear tenant data from rooms table
            cur.execute("""
                UPDATE rooms SET
                    tenant_name=NULL, father_name=NULL, mother_name=NULL,
                    address=NULL, street=NULL, area=NULL, pincode=NULL,
                    aadhar_number=NULL, dob=NULL, email=NULL, phone=NULL,
                    office_name=NULL, office_address=NULL, deposit=NULL, rent=NULL,
                    room_type=NULL, checkin_date=NULL, emergency_name=NULL,
                    emergency_phone=NULL, emergency_relation=NULL, photo=NULL, aadhar=NULL
                WHERE floor=%s AND room=%s AND bed=%s
            """, (floor, room, bed))
            
            logger.info("Tenant data cleared from rooms table")
            
            conn.commit()
            logger.info(f"Tenant moved to former tenants: {floor}-{room}-{bed}")
            return True
            
        else:
            logger.warning(f"No tenant data found for {floor}-{room}-{bed}")
        return False
        
    except Exception as e:
        conn.rollback()
        logger.error(f"move_to_former_tenants error: {e}")
        return False
        
    finally:
        cur.close()
        release(conn)


# --------------------------------------------------
# GET FORMER TENANTS
# --------------------------------------------------

def get_former_tenants():
    
    conn = connect()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        
        cur.execute("""
            SELECT * FROM former_tenants 
            ORDER BY leaving_date DESC, created_at DESC
        """)
        
        return cur.fetchall()
        
    except Exception as e:
        logger.error(f"get_former_tenants error: {e}")
        return []
        
    finally:
        cur.close()
        release(conn)


# --------------------------------------------------
# REMOVE TENANT
# --------------------------------------------------

def remove_tenant(floor, room, bed):

    return move_to_former_tenants(floor, room, bed)

def delete_room(floor, room):

    conn = connect()
    cur = conn.cursor()

    try:

        cur.execute(
            "DELETE FROM rooms WHERE floor=%s AND room=%s",
            (floor, room)
        )

        conn.commit()

        logger.info(f"Room deleted {floor}-{room}")

        return True

    except Exception as e:

        conn.rollback()
        logger.error(f"delete_room error: {e}")

        return False

    finally:

        cur.close()
        release(conn)

def delete_bed(floor, room, bed):

    conn = connect()
    cur = conn.cursor()

    try:

        cur.execute(
            "DELETE FROM rooms WHERE floor=%s AND room=%s AND bed=%s",
            (floor, room, bed)
        )

        conn.commit()

        logger.info(f"Bed deleted {floor}-{room}-{bed}")

        return True

    except Exception as e:

        conn.rollback()
        logger.error(f"delete_bed error: {e}")

        return False

    finally:

        cur.close()
        release(conn)

def delete_floor(floor):

    conn = connect()
    cur = conn.cursor()

    try:

        cur.execute(
            "DELETE FROM rooms WHERE floor=%s",
            (floor,)
        )

        conn.commit()

        logger.info(f"Floor deleted {floor}")

        return True

    except Exception as e:

        conn.rollback()
        logger.error(f"delete_floor error: {e}")

        return False

    finally:

        cur.close()
        release(conn)