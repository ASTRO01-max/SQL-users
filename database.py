import psycopg2

def add_user_to_database(user_data: dict):
    conn = psycopg2.connect("dbname='SQL_DBname' user='SQL password' password='SQL password'") 
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            ism VARCHAR(50),
            fam VARCHAR(50),
            tel_nomer VARCHAR(15)
        );
    """)

    cur.execute(
        "INSERT INTO users (ism, fam, tel_nomer) VALUES (%s, %s, %s);",
        (user_data['ism'], user_data['fam'], user_data['tel_nomer'])
    )

    conn.commit()
    cur.close()
    conn.close()

