"""
SQLite database for storing conversations and feedback.
Auto-creates tables on first run.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from contextlib import contextmanager
from config import settings

class Database:
    """SQLite database manager for Math Agent."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize database connection."""
        if db_path is None:
            # Store in data/ folder
            self.db_path = settings.DATA_DIR / "conversations.db"
        else:
            self.db_path = db_path
        
        # Ensure data directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize tables
        self._create_tables()
        print(f"✅ Database initialized: {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Return dict-like rows
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Table 1: Conversations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    source TEXT NOT NULL,
                    confidence_score REAL,
                    kb_matches INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table 2: Feedback
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER,
                    query TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                    is_correct BOOLEAN,
                    correction TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            """)
            
            # Table 3: Human Interventions (for significant corrections)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS human_interventions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feedback_id INTEGER NOT NULL,
                    original_answer TEXT NOT NULL,
                    corrected_answer TEXT NOT NULL,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (feedback_id) REFERENCES feedback(id)
                )
            """)
            
            conn.commit()
    
    # ==================== CONVERSATION METHODS ====================
    
    def save_conversation(
        self,
        query: str,
        answer: str,
        source: str,
        confidence_score: float,
        kb_matches: int
    ) -> int:
        """
        Save a conversation to database.
        
        Returns:
            conversation_id (int)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations 
                (query, answer, source, confidence_score, kb_matches)
                VALUES (?, ?, ?, ?, ?)
            """, (query, answer, source, confidence_score, kb_matches))
            return cursor.lastrowid
    
    def get_conversation(self, conversation_id: int) -> Optional[Dict]:
        """Get conversation by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM conversations WHERE id = ?",
                (conversation_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Get recent conversations."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM conversations 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== FEEDBACK METHODS ====================
    
    def save_feedback(
        self,
        query: str,
        answer: str,
        rating: int,
        is_correct: Optional[bool] = None,
        correction: Optional[str] = None,
        notes: Optional[str] = None,
        conversation_id: Optional[int] = None
    ) -> int:
        """
        Save user feedback.
        
        Returns:
            feedback_id (int)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO feedback
                (conversation_id, query, answer, rating, is_correct, correction, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (conversation_id, query, answer, rating, is_correct, correction, notes))
            
            feedback_id = cursor.lastrowid
            
            # If significant correction provided, save as human intervention
            if correction and len(correction) > 50:
                self._save_intervention(cursor, feedback_id, answer, correction)
            
            return feedback_id
    
    def _save_intervention(
        self,
        cursor,
        feedback_id: int,
        original_answer: str,
        corrected_answer: str
    ):
        """Save significant corrections as human interventions."""
        cursor.execute("""
            INSERT INTO human_interventions
            (feedback_id, original_answer, corrected_answer, reason)
            VALUES (?, ?, ?, ?)
        """, (feedback_id, original_answer, corrected_answer, "User provided substantial correction"))
    
    def get_feedback_stats(self) -> Dict:
        """Get aggregate feedback statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_feedback,
                    AVG(rating) as avg_rating,
                    SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct_count,
                    SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) as incorrect_count,
                    SUM(CASE WHEN correction IS NOT NULL THEN 1 ELSE 0 END) as corrections_count
                FROM feedback
            """)
            row = cursor.fetchone()
            return dict(row) if row else {}
    
    def get_recent_feedback(self, limit: int = 10) -> List[Dict]:
        """Get recent feedback entries."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM feedback 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_human_interventions(self, limit: int = 10) -> List[Dict]:
        """Get recent human interventions (significant corrections)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT hi.*, f.query, f.rating
                FROM human_interventions hi
                JOIN feedback f ON hi.feedback_id = f.id
                ORDER BY hi.created_at DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== ANALYTICS METHODS ====================
    
    def get_source_distribution(self) -> Dict[str, int]:
        """Get distribution of answer sources (KB vs web vs LLM)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT source, COUNT(*) as count
                FROM conversations
                GROUP BY source
            """)
            return {row['source']: row['count'] for row in cursor.fetchall()}
    
    def get_average_confidence_by_source(self) -> Dict[str, float]:
        """Get average confidence score by source."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT source, AVG(confidence_score) as avg_confidence
                FROM conversations
                WHERE confidence_score > 0
                GROUP BY source
            """)
            return {row['source']: round(row['avg_confidence'], 3) for row in cursor.fetchall()}

# Global database instance
_db: Optional[Database] = None

def get_db() -> Database:
    """Get global database instance (singleton pattern)."""
    global _db
    if _db is None:
        _db = Database()
    return _db

def init_db():
    """Initialize database (call on app startup)."""
    return get_db()
