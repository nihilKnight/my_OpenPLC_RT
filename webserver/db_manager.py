import sqlite3
from sqlite3 import Error


DB = 'openplc.db'


def sanitize_input(*args):
    return (escape(a) for a in args)

def escape(s, quote=True):
    """
    Replace special characters "&", "<" and ">" to HTML-safe sequences.
    If the optional flag quote is true (the default), the quotation mark
    characters, both double quote (") and single quote (') characters are also
    translated.
    """
    if s is None: 
        return s
    s = str(s) # force string
    s = s.replace("&", "&amp;") # Must be done first!
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
        s = s.replace('\'', "&#x27;")
    return s

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)


def insert_st_file(prog_name, prog_descr, prog_file, epoch_time):

    (prog_name, prog_descr, prog_file, epoch_time) = sanitize_input(prog_name, prog_descr, prog_file, epoch_time)

    conn = create_connection(DB)
    if (conn is not None):
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO Programs (Name, Description, File, Date_upload) VALUES (?, ?, ?, ?)", (prog_name, prog_descr, prog_file, epoch_time))
            conn.commit()
            cur.close()
            conn.close()
        except Error as e:
            print("Error connecting to the database" + str(e))
    else:
        print('Error connecting to the database. Make sure that your openplc.db file is not corrupt.')
