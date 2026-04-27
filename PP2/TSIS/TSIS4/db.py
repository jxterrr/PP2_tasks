import psycopg2
from psycopg2 import sql

CONN_PARAMS = "host=localhost dbname=postgres user=postgres password=adikadikadik777 port=5432"

def init_db():
    with psycopg2.connect(CONN_PARAMS) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL
                );
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id SERIAL PRIMARY KEY,
                    player_id INTEGER REFERENCES players(id),
                    score INTEGER NOT NULL,
                    level_reached INTEGER NOT NULL
                );
            """)

def get_player_id(username):
    with psycopg2.connect(CONN_PARAMS) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO players (username) VALUES (%s) ON CONFLICT (username) DO NOTHING", (username,))
            cur.execute("SELECT id FROM players WHERE username = %s", (username,))
            return cur.fetchone()[0]

def save_session(player_id, score, level):
    with psycopg2.connect(CONN_PARAMS) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)", (player_id, score, level))

def get_top_10():
    with psycopg2.connect(CONN_PARAMS) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.username, s.score, s.level_reached 
                FROM game_sessions s JOIN players p ON s.player_id = p.id 
                ORDER BY s.score DESC LIMIT 10
            """)
            return cur.fetchall()

def get_personal_best(player_id):
    with psycopg2.connect(CONN_PARAMS) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT MAX(score) FROM game_sessions WHERE player_id = %s", (player_id,))
            res = cur.fetchone()
            return res[0] if res[0] is not None else 0

def clear_leaderboard():
    with psycopg2.connect(CONN_PARAMS) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM game_sessions")
