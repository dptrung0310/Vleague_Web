# utils/database.py
import sqlite3
import os
from contextlib import contextmanager
from config import Config

def get_db_connection():
    """
    Get database connection with dict factory
    Returns connection that returns rows as dictionaries
    """
    try:
        conn = sqlite3.connect(Config.DATABASE_URL)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        # Enable WAL mode for better concurrent reads
        conn.execute("PRAGMA journal_mode = WAL")
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        raise

@contextmanager
def get_db_cursor():
    """
    Context manager for database operations
    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM table")
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def execute_query(query, params=None):
    """
    Execute a query and return all results
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        return [dict(row) for row in results]
    except sqlite3.Error as e:
        print(f"Query execution error: {e}")
        raise
    finally:
        conn.close()

def execute_single_query(query, params=None):
    """
    Execute a query and return single result
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchone()
        return dict(result) if result else None
    except sqlite3.Error as e:
        print(f"Query execution error: {e}")
        raise
    finally:
        conn.close()

def execute_insert(query, params=None):
    """
    Execute an INSERT query and return the last row ID
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Insert execution error: {e}")
        raise
    finally:
        conn.close()

def execute_update(query, params=None):
    """
    Execute an UPDATE/DELETE query and return number of affected rows
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor.rowcount
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Update execution error: {e}")
        raise
    finally:
        conn.close()

def check_database_health():
    """
    Check if database is accessible and has required tables
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if essential tables exist
        required_tables = ['Matches', 'Teams', 'Seasons', 'Players']
        existing_tables = []
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        existing_tables = [table['name'] for table in tables]
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        conn.close()
        
        return {
            'status': 'healthy' if not missing_tables else 'degraded',
            'database_path': Config.DATABASE_URL,
            'existing_tables': existing_tables,
            'missing_tables': missing_tables,
            'total_tables': len(existing_tables)
        }
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }

def init_database():
    """
    Initialize database with required tables and indexes
    This is a safety function to ensure required tables exist
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Create indexes for better performance if they don't exist
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_matches_season ON Matches(season_id)",
            "CREATE INDEX IF NOT EXISTS idx_matches_status ON Matches(status)",
            "CREATE INDEX IF NOT EXISTS idx_matches_datetime ON Matches(match_datetime)",
            "CREATE INDEX IF NOT EXISTS idx_matches_teams ON Matches(home_team_id, away_team_id)",
            "CREATE INDEX IF NOT EXISTS idx_teams_name ON Teams(name)",
            "CREATE INDEX IF NOT EXISTS idx_players_name ON Players(full_name)",
            "CREATE INDEX IF NOT EXISTS idx_seasons_dates ON Seasons(start_date, end_date)",
            "CREATE INDEX IF NOT EXISTS idx_lineups_match ON MatchLineups(match_id)",
            "CREATE INDEX IF NOT EXISTS idx_events_match ON MatchEvents(match_id)",
            "CREATE INDEX IF NOT EXISTS idx_standings_season_round ON SeasonStandings(season_id, round)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        print("✅ Database initialized successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Database initialization failed: {e}")
        raise
    finally:
        conn.close()