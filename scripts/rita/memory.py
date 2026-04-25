import asyncio
from contextlib import contextmanager
from typing import Optional, List, Tuple
import re
import psycopg2
from psycopg2 import pool
import logging
import google.generativeai as genai
from config import config

logger = logging.getLogger(__name__)

class MemorySystem:
    """Système de mémoire multi-niveau"""

    def __init__(self):
        self.pool: Optional[pool.ThreadedConnectionPool] = None
        self.model = genai.GenerativeModel(
            model_name=config.MODEL_NAME,
            generation_config={"temperature": 0.5}
        )

    async def initialize(self):
        db_url = config.DATABASE_URL.replace("postgres://", "postgresql://", 1)

        try:
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                config.DB_POOL_MIN,
                config.DB_POOL_MAX,
                db_url,
                sslmode='require'
            )
            await asyncio.to_thread(self._init_schema)
            logger.info("✅ Database initialized")

        except Exception as e:
            logger.error(f"❌ Database init failed: {e}")
            raise

    def _init_schema(self):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_memory (
                        user_id VARCHAR(100) PRIMARY KEY,
                        immediate_context TEXT,
                        profile_summary TEXT,
                        affinity SMALLINT DEFAULT 0,
                        total_interactions INT DEFAULT 0,
                        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE INDEX IF NOT EXISTS idx_last_seen ON user_memory(last_seen);
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS events (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        summary TEXT NOT NULL,
                        participants TEXT[]
                    );
                    CREATE INDEX IF NOT EXISTS idx_event_time ON events(timestamp DESC);
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id SERIAL PRIMARY KEY,
                        sender VARCHAR(100) NOT NULL,
                        recipient VARCHAR(100) NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_read BOOLEAN DEFAULT FALSE
                    );
                    CREATE INDEX IF NOT EXISTS idx_recipient ON messages(recipient, is_read);
                """)
                conn.commit()

    @contextmanager
    def get_connection(self):
        conn = self.pool.getconn()
        try:
            yield conn
        finally:
            self.pool.putconn(conn)

    async def analyze_and_save_background(self, user_name: str, profile: str, conversation: str, current_affinity: int):
        """Analyse la conversation et sauvegarde profil + affinité en arrière-plan"""
        try:
            new_affinity, new_profile = await self.analyze_conversation(
                profile, conversation, current_affinity
            )
            await asyncio.to_thread(self._update_profile_sync, user_name, new_profile, new_affinity)

            event = await self.create_event_summary(conversation)
            if event:
                await self.save_event(event, [user_name])

        except Exception as e:
            logger.error(f"Background save error: {e}")

    # ========================================================================
    # SYNC DB HELPERS (exécutés dans un thread via asyncio.to_thread)
    # ========================================================================

    def _load_user_data_sync(self, user_name: str) -> dict:
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT immediate_context, profile_summary, affinity, total_interactions
                    FROM user_memory WHERE user_id = %s
                """, (user_name,))
                user_data = cur.fetchone()

                cur.execute("""
                    SELECT summary FROM events
                    ORDER BY timestamp DESC
                    LIMIT %s
                """, (config.EPISODIC_MEMORY,))
                events = [row[0] for row in cur.fetchall()]

                cur.execute("""
                    SELECT summary FROM events
                    WHERE %s = ANY(participants)
                    ORDER BY timestamp DESC
                    LIMIT %s
                """, (user_name, config.SEMANTIC_MEMORY))
                user_events = [row[0] for row in cur.fetchall()]

                cur.execute("""
                    SELECT sender, content FROM messages
                    WHERE recipient = %s AND is_read = FALSE
                    ORDER BY created_at ASC
                """, (user_name,))
                messages = [(row[0], row[1]) for row in cur.fetchall()]

        if user_data:
            context, profile, affinity, interactions = user_data
            return {
                'context': context or '',
                'profile': profile or 'Nouvelle rencontre',
                'affinity': affinity,
                'interactions': interactions,
                'events': events + user_events,
                'messages': messages
            }
        return {
            'context': '',
            'profile': 'Nouvelle rencontre',
            'affinity': 0,
            'interactions': 0,
            'events': events,
            'messages': []
        }

    def _save_interaction_sync(self, user_name: str, new_context: str, new_profile: str, new_affinity: int):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO user_memory
                        (user_id, immediate_context, profile_summary, affinity, total_interactions, last_seen)
                    VALUES (%s, %s, %s, %s, 1, CURRENT_TIMESTAMP)
                    ON CONFLICT (user_id) DO UPDATE SET
                        immediate_context = EXCLUDED.immediate_context,
                        profile_summary = EXCLUDED.profile_summary,
                        affinity = EXCLUDED.affinity,
                        total_interactions = user_memory.total_interactions + 1,
                        last_seen = CURRENT_TIMESTAMP
                """, (user_name, new_context, new_profile, new_affinity))
                conn.commit()

    def _update_profile_sync(self, user_name: str, new_profile: str, new_affinity: int):
        """Met à jour uniquement le profil et l'affinité (sans toucher au contexte ni au compteur)"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE user_memory
                    SET profile_summary = %s, affinity = %s
                    WHERE user_id = %s
                """, (new_profile, new_affinity, user_name))
                conn.commit()

    def _save_event_sync(self, summary: str, participants: List[str]):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO events (summary, participants)
                    VALUES (%s, %s)
                """, (summary, participants))
                conn.commit()

    def _send_message_sync(self, sender: str, recipient: str, content: str):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO messages (sender, recipient, content)
                    VALUES (%s, %s, %s)
                """, (sender, recipient, content))
                conn.commit()

    def _mark_messages_read_sync(self, recipient: str):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE messages
                    SET is_read = TRUE
                    WHERE recipient = %s AND is_read = FALSE
                """, (recipient,))
                conn.commit()

    def _cleanup_old_data_sync(self):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM events
                    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '30 days'
                """)
                cur.execute("""
                    DELETE FROM messages
                    WHERE is_read = TRUE
                    AND created_at < CURRENT_TIMESTAMP - INTERVAL '7 days'
                """)
                conn.commit()
        logger.info("🧹 Cleanup done")

    # ========================================================================
    # ASYNC PUBLIC API
    # ========================================================================

    async def load_user_data(self, user_name: str) -> dict:
        return await asyncio.to_thread(self._load_user_data_sync, user_name)

    async def analyze_conversation(self, profile: str, recent_conv: str, current_affinity: int) -> Tuple[int, str]:
        prompt = f"""Analyse cette conversation.

Profil actuel: {profile}
Conversation: {recent_conv}

Réponds en 2 lignes EXACTEMENT:
LIGNE 1: Chiffre entre -3 et +3 pour l'ambiance (-3=très hostile, 0=neutre, +3=très positif)
LIGNE 2: Nouveau profil en 1 phrase (traits, passions, humeur)"""

        try:
            response = await self.model.generate_content_async(prompt)
            lines = response.text.strip().split('\n', 1)

            delta = 0
            if lines:
                match = re.search(r'([-+]?\d+)', lines[0])
                if match:
                    delta = max(-3, min(3, int(match.group(1))))

            new_profile = lines[1].strip() if len(lines) > 1 else profile
            new_affinity = max(config.AFFINITY_MIN,
                             min(config.AFFINITY_MAX,
                                 current_affinity + delta))

            return new_affinity, new_profile

        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return current_affinity, profile

    async def create_event_summary(self, conversation: str) -> Optional[str]:
        try:
            response = await self.model.generate_content_async(
                f"Résume en 1 phrase courte à la 3e personne:\n{conversation}"
            )
            return response.text.strip()
        except:
            return None

    async def save_interaction(self, user_name: str, new_context: str, new_profile: str, new_affinity: int):
        await asyncio.to_thread(self._save_interaction_sync, user_name, new_context, new_profile, new_affinity)

    async def save_event(self, summary: str, participants: List[str]):
        await asyncio.to_thread(self._save_event_sync, summary, participants)

    async def send_message(self, sender: str, recipient: str, content: str):
        await asyncio.to_thread(self._send_message_sync, sender, recipient, content)

    async def mark_messages_read(self, recipient: str):
        await asyncio.to_thread(self._mark_messages_read_sync, recipient)

    async def cleanup_old_data(self):
        await asyncio.to_thread(self._cleanup_old_data_sync)

    async def shutdown(self):
        if self.pool:
            self.pool.closeall()
            logger.info("Database pool closed")

memory = MemorySystem()
