"""
Ban System - Stockage PostgreSQL avec anti-spam
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from memory import memory

logger = logging.getLogger(__name__)

BAN_CONFIG = {
    "STRIKES_TO_BAN": 4,
    "STRIKE_RESET_HOURS": 24,
    "BAN_DURATION_HOURS": 72,
    "MAX_BAN_ATTEMPTS": 5,  # ← NOUVEAU: Max tentatives pendant le ban
    "EXTENDED_BAN_HOURS": 168,  # ← NOUVEAU: 7 jours si spam pendant ban
}

async def initialize_ban_table():
    """Crée la table des bans si elle n'existe pas"""
    with memory.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_bans (
                    user_id VARCHAR(100) PRIMARY KEY,
                    strike_count INT DEFAULT 0,
                    last_strike TIMESTAMP,
                    banned_until TIMESTAMP,
                    ban_attempts INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_banned_until ON user_bans(banned_until);
            """)
            conn.commit()
    logger.info("✅ Ban table initialized")

async def add_strike(user_name: str) -> dict:
    """Ajoute un strike à un utilisateur"""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    
    with memory.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT strike_count, last_strike, banned_until
                FROM user_bans WHERE user_id = %s
            """, (user_name,))
            
            row = cur.fetchone()
            
            if row:
                strike_count, last_strike, banned_until = row
                time_since = now - last_strike
                if time_since > timedelta(hours=BAN_CONFIG["STRIKE_RESET_HOURS"]):
                    strike_count = 0
            else:
                strike_count = 0
            
            strike_count += 1
            
            logger.warning(f"⚠️ STRIKE {strike_count}/{BAN_CONFIG['STRIKES_TO_BAN']} | User: {user_name}")
            
            if strike_count >= BAN_CONFIG["STRIKES_TO_BAN"]:
                banned_until = now + timedelta(hours=BAN_CONFIG["BAN_DURATION_HOURS"])
                
                cur.execute("""
                    INSERT INTO user_bans (user_id, strike_count, last_strike, banned_until, ban_attempts, updated_at)
                    VALUES (%s, 0, %s, %s, 0, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        strike_count = 0,
                        last_strike = EXCLUDED.last_strike,
                        banned_until = EXCLUDED.banned_until,
                        ban_attempts = 0,
                        updated_at = EXCLUDED.updated_at
                """, (user_name, now, banned_until, now))
                conn.commit()
                
                logger.error(f"🚫 USER BANNED | User: {user_name} | Until: {banned_until}")
                
                return {
                    "strikes": strike_count,
                    "is_banned": True,
                    "banned_until": banned_until,
                    "warning_message": f"Banni jusqu'au {banned_until.strftime('%d/%m %H:%M')} pour abus répétés"
                }
            
            cur.execute("""
                INSERT INTO user_bans (user_id, strike_count, last_strike, updated_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    strike_count = EXCLUDED.strike_count,
                    last_strike = EXCLUDED.last_strike,
                    updated_at = EXCLUDED.updated_at
            """, (user_name, strike_count, now, now))
            conn.commit()
            
            remaining = BAN_CONFIG["STRIKES_TO_BAN"] - strike_count
            warnings = {
                3: "Dernier avertissement. Prochain abus = ban de 3 jours",
                2: f"Encore {remaining} abus et tu seras banni",
                1: "Arrête ou tu vas être banni"
            }
            
            return {
                "strikes": strike_count,
                "is_banned": False,
                "banned_until": None,
                "warning_message": warnings.get(strike_count, "Arrête")
            }

async def is_banned(user_name: str) -> tuple[bool, Optional[str]]:
    """Vérifie si un utilisateur est banni et compte les tentatives"""
    with memory.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT banned_until, ban_attempts FROM user_bans
                WHERE user_id = %s AND banned_until IS NOT NULL
            """, (user_name,))
            
            row = cur.fetchone()
            
            if not row or not row[0]:
                return False, None
            
            banned_until, ban_attempts = row
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            
            if now < banned_until:
                # User est toujours banni
                
                # Incrémente le compteur de tentatives
                ban_attempts += 1
                
                # ⚠️ TROP DE TENTATIVES = BAN ÉTENDU
                if ban_attempts >= BAN_CONFIG["MAX_BAN_ATTEMPTS"]:
                    extended_until = now + timedelta(hours=BAN_CONFIG["EXTENDED_BAN_HOURS"])
                    
                    cur.execute("""
                        UPDATE user_bans 
                        SET banned_until = %s, ban_attempts = 0
                        WHERE user_id = %s
                    """, (extended_until, user_name))
                    conn.commit()
                    
                    logger.error(
                        f"🚫 BAN EXTENDED | User: {user_name} | "
                        f"Until: {extended_until.strftime('%d/%m %H:%M')} | "
                        f"Reason: Too many attempts during ban"
                    )
                    
                    return True, f"Ban prolongé de 7 jours pour spam. Fin: {extended_until.strftime('%d/%m %H:%M')}"
                
                # Update le compteur
                cur.execute("""
                    UPDATE user_bans 
                    SET ban_attempts = %s
                    WHERE user_id = %s
                """, (ban_attempts, user_name))
                conn.commit()
                
                # Calcule le temps restant
                remaining = banned_until - now
                hours = int(remaining.total_seconds() / 3600)
                minutes = int((remaining.total_seconds() % 3600) / 60)
                
                time_str = f"{hours}h{minutes:02d}" if hours > 0 else f"{minutes}min"
                
                # Message de plus en plus agressif selon les tentatives
                if ban_attempts == 1:
                    msg = f"Tu es banni encore {time_str}"
                elif ban_attempts == 2:
                    msg = f"Banni {time_str}. Arrête d'essayer"
                elif ban_attempts == 3:
                    msg = f"Banni {time_str}. Stop le spam"
                elif ban_attempts >= 4:
                    msg = f"Banni {time_str}. Encore 1 tentative = ban prolongé de 7 jours"
                
                logger.warning(
                    f"🚫 Banned user attempt {ban_attempts}/{BAN_CONFIG['MAX_BAN_ATTEMPTS']} | "
                    f"User: {user_name}"
                )
                
                return True, msg
            
            # Ban expiré - clean
            cur.execute("""
                UPDATE user_bans 
                SET banned_until = NULL, strike_count = 0, ban_attempts = 0
                WHERE user_id = %s
            """, (user_name,))
            conn.commit()
            
            logger.info(f"✅ Ban expired | User: {user_name}")
            
            return False, None

async def reset_strikes(user_name: str):
    """Reset les strikes (admin)"""
    with memory.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE user_bans
                SET strike_count = 0, banned_until = NULL, ban_attempts = 0
                WHERE user_id = %s
            """, (user_name,))
            conn.commit()
    
    logger.info(f"🔓 User unbanned by admin | User: {user_name}")

async def get_user_status(user_name: str) -> dict:
    """Récupère le statut"""
    with memory.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT strike_count, banned_until, ban_attempts
                FROM user_bans WHERE user_id = %s
            """, (user_name,))
            
            row = cur.fetchone()
            
            if not row:
                return {
                    "strikes": 0,
                    "is_banned": False,
                    "banned_until": None,
                    "ban_attempts": 0
                }
            
            strike_count, banned_until, ban_attempts = row
            is_currently_banned = banned_until and datetime.now(timezone.utc).replace(tzinfo=None) < banned_until
            
            return {
                "strikes": strike_count,
                "is_banned": is_currently_banned,
                "banned_until": banned_until,
                "ban_attempts": ban_attempts
            }