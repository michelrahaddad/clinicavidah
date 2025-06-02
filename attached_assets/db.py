import sqlite3
from contextlib import contextmanager
import logging

def get_db_connection():
    """Get database connection with row factory"""
    try:
        conn = sqlite3.connect('dados.db')
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        raise

@contextmanager
def get_db():
    """Context manager for database operations"""
    conn = None
    try:
        conn = get_db_connection()
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Database transaction error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def insert_patient_if_not_exists(nome_paciente):
    """Insert patient if not exists and return ID"""
    with get_db() as conn:
        # Check if patient exists
        paciente = conn.execute("SELECT id FROM pacientes WHERE nome = ?", (nome_paciente,)).fetchone()
        
        if paciente:
            return paciente['id']
        else:
            # Insert new patient
            cursor = conn.execute("INSERT INTO pacientes (nome) VALUES (?)", (nome_paciente,))
            return cursor.lastrowid

def get_dashboard_stats():
    """Get dashboard statistics"""
    with get_db() as conn:
        stats = {}
        stats['total_pacientes'] = conn.execute('SELECT COUNT(*) FROM pacientes').fetchone()[0]
        stats['total_receitas'] = conn.execute('SELECT COUNT(*) FROM receitas').fetchone()[0]
        stats['total_exames_lab'] = conn.execute('SELECT COUNT(*) FROM exames_lab').fetchone()[0]
        stats['total_exames_img'] = conn.execute('SELECT COUNT(*) FROM exames_img').fetchone()[0]
        stats['total_agendamentos'] = conn.execute('SELECT COUNT(*) FROM agenda').fetchone()[0]
        return stats
