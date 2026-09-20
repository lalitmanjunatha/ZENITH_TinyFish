"""
ZENITH Memory Brain — The Thinking Layer

An algorithmic system that:
1. Extracts user profile from conversation history (name, preferences, habits, projects)
2. Tracks mood patterns over time
3. Generates time-aware + memory-aware context
4. Provides contextual recall for natural conversation

This is NOT a template system. It's a learning algorithm that builds
a knowledge base about the user over time.
"""

import os
import json
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

TOOL = {
    "name": "memory_brain",
    "description": "Manage the AI's memory system: store facts, recall information, track user preferences, and manage conversation context. Use when the user wants to save or retrieve information from the AI's memory.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {"type": "STRING", "description": "Action: 'store', 'recall', 'get_profile', 'get_mood', 'clear'"},
            "key": {"type": "STRING", "description": "Memory key or topic to store/recall"},
            "value": {"type": "STRING", "description": "Value to store (for store action)"},
            "category": {"type": "STRING", "description": "Memory category (e.g. 'preference', 'fact', 'project')"}
        },
        "required": ["action"]
    },
    "handler": "handle_memory_brain",
}

# =========================
# PATHS
# =========================
_DATA_DIR = Path(os.path.join(os.path.dirname(__file__), '..', 'data'))
_PROFILE_FILE = _DATA_DIR / 'user_profile.json'
_MEMORY_SUMMARY = _DATA_DIR / 'memory_summary.json'
_CONVERSATION_LOG = os.path.join(os.path.dirname(__file__), '..', 'memory.json')
_MOOD_LOG = _DATA_DIR / 'mood_log.json'
_INTERACTION_LOG = _DATA_DIR / 'interaction_log.json'

_DATA_DIR.mkdir(exist_ok=True)


def _load_json(path, default=None):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}


def _save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def _now():
    return datetime.now()


# =========================
# ALGORITHM 1: USER PROFILE EXTRACTION
# =========================
# Pattern-based extraction from conversation history.
# No ML required — uses heuristics and frequency analysis.

class UserProfileExtractor:
    """
    Extracts user profile from raw conversation history.
    
    Algorithm:
    1. Scan all user messages for name mentions
    2. Extract language preference from message patterns
    3. Detect projects/topics from repeated mentions
    4. Identify communication style (formal/casual/technical)
    5. Build preference map from explicit statements
    """
    
    # Hindi words that indicate Hindi preference
    HINDI_INDICATORS = [
        'hai', 'ho', 'kya', 'kaise', 'karo', 'mat', 'aur', 'yaar',
        'bhai', 'acha', 'theek', 'nahi', 'haan', 'ji', 'sir', 'bolo',
        'kar', 'de', 'le', 'ho', 'raha', 'hai', 'hain', 'tha', 'thi',
        'karna', 'bolna', 'sunna', 'dekhna', 'jaana', 'aana',
        'subah', 'shaam', 'raat', 'din', 'waqt', 'abhi', 'phir',
        'bas', 'chalo', 'arre', 'oye', 'demo', 'project', 'code',
    ]
    
    # Words indicating technical conversation
    TECH_INDICATORS = [
        'code', 'python', 'api', 'function', 'error', 'bug', 'fix',
        'install', 'run', 'test', 'deploy', 'server', 'database',
        'git', 'commit', 'push', 'pull', 'repository', 'npm', 'pip',
        'html', 'css', 'javascript', 'react', 'node', 'flask', 'django',
        'algorithm', 'data', 'structure', 'class', 'object', 'method',
        'file', 'folder', 'directory', 'path', 'command', 'terminal',
    ]
    
    # Words indicating casual conversation
    CASUAL_INDICATORS = [
        'hey', 'yo', 'lol', 'haha', 'nice', 'cool', 'awesome',
        'wtf', 'bruh', 'dude', 'man', 'bro', 'yaar', 'arre',
        'chill', 'mood', 'vibe', 'energy', 'tired', 'sleepy',
        'hungry', 'bored', 'excited', 'fun', 'game', 'music',
    ]
    
    # Mood detection patterns
    MOOD_PATTERNS = {
        'stressed': [
            r'stress', r'too much', r'overwhelm', r'pressure', r'deadline',
            r'panic', r'anxious', r'worried', r'tense', r'cant focus',
            r'sab kuch', r'bahut zyada', r'ruk jao', r'head.*hurt',
        ],
        'excited': [
            r'amazing', r'awesome', r'great', r'nice', r'perfect',
            r'love it', r'wow', r'fantastic', r'brilliant', r'success',
            r'kaam ho gaya', r'ban gaya', r'chal pada', r'it works',
        ],
        'frustrated': [
            r'not working', r'failed', r'error', r'bug', r'broken',
            r'wtf', r'why', r'ugh', r'annoying', r'hate',
            r'ye kya hai', r'band karo', r'galti', r'phir se',
        ],
        'tired': [
            r'tired', r'sleepy', r'exhausted', r'cant think', r'brain',
            r'sleep', r'neend', r'thaak', r'energy nahi', r'rest',
        ],
        'happy': [
            r'happy', r'glad', r'good', r'well', r'fine', r'alright',
            r'theek hai', r'acha hai', r'sahi hai', r'badhiya',
        ],
        'curious': [
            r'what is', r'how does', r'why', r'explain', r'tell me',
            r'kya hai', r'kaise', r'samjhao', r'detail', r'more',
        ],
        'casual': [
            r'hey', r'hi', r'hello', r'whats up', r'kaise ho',
            r'bas', r'chill', r'kuch nahi', r'just checking',
        ],
    }
    
    def extract_from_history(self, messages: List[Dict]) -> Dict:
        """
        Main extraction algorithm.
        Input: Raw conversation messages from memory.json
        Output: Structured user profile
        """
        user_messages = [m for m in messages if m.get('role') == 'user']
        
        if not user_messages:
            return self._empty_profile()
        
        profile = {
            'name': self._extract_name(user_messages),
            'language_preference': self._detect_language(user_messages),
            'communication_style': self._detect_style(user_messages),
            'topics': self._extract_topics(user_messages),
            'habits': self._detect_habits(user_messages, messages),
            'preferences': self._extract_preferences(user_messages),
            'first_seen': messages[0].get('timestamp', ''),
            'last_seen': messages[-1].get('timestamp', ''),
            'total_messages': len(user_messages),
            'profile_confidence': 0.0,  # increases with more data
        }
        
        # Calculate confidence based on data richness
        confidence = 0.0
        if profile['name']: confidence += 0.2
        if profile['language_preference'] != 'mixed': confidence += 0.15
        if len(profile['topics']) > 0: confidence += 0.2
        if len(profile['preferences']) > 0: confidence += 0.2
        if profile['total_messages'] > 50: confidence += 0.15
        if profile['communication_style'] != 'neutral': confidence += 0.1
        profile['profile_confidence'] = min(confidence, 1.0)
        
        return profile
    
    def _extract_name(self, messages: List[Dict]) -> str:
        """
        Extract user name from conversation.
        
        Algorithm:
        1. Look for explicit name statements ("my name is X", "I'm X")
        2. Look for name in greetings ("hi, I'm Lalit")
        3. Check if name appears frequently in user messages
        """
        name_patterns = [
            r'(?:my name is|i am|i\'m|call me|this is)\s+([A-Z][a-z]+)',
            r'(?:naam hai|naam mera)\s+([A-Z][a-z]+)',
            r'(?:main hoon|mai hoon)\s+([A-Z][a-z]+)',
        ]
        
        for msg in messages:
            content = msg.get('content', '')
            # Handle list content
            if isinstance(content, list):
                content = ' '.join(str(item) for item in content)
            for pattern in name_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    if len(name) > 1 and len(name) < 20:
                        return name
        
        # Fallback: check if any proper noun appears frequently
        word_freq = {}
        for msg in messages:
            content = msg.get('content', '')
            if isinstance(content, list):
                content = ' '.join(str(item) for item in content)
            words = re.findall(r'\b[A-Z][a-z]{2,}\b', content)
            for w in words:
                if w not in ('The', 'This', 'That', 'What', 'How', 'When', 'Where', 'Why', 'Can', 'Will', 'Just', 'Now', 'Hey', 'Hello'):
                    word_freq[w] = word_freq.get(w, 0) + 1
        
        if word_freq:
            most_common = max(word_freq, key=word_freq.get)
            if word_freq[most_common] >= 3:
                return most_common
        
        return ""
    
    def _detect_language(self, messages: List[Dict]) -> str:
        """
        Detect user's primary language preference.
        
        Algorithm:
        1. Count Hindi indicators vs English-only patterns
        2. Ratio determines: 'hindi', 'english', or 'mixed'
        """
        hindi_count = 0
        english_count = 0
        
        for msg in messages[-50:]:  # Last 50 messages
            content = msg.get('content', '').lower()
            if isinstance(content, list):
                content = ' '.join(str(item) for item in content).lower()
            
            for indicator in self.HINDI_INDICATORS:
                if indicator in content:
                    hindi_count += 1
            
            # Simple English detection (common English words)
            english_words = len(re.findall(r'\b(?:the|is|are|was|were|have|has|can|will|do|does|did|what|how|when|where|why)\b', content))
            english_count += english_words
        
        total = hindi_count + english_count
        if total == 0:
            return 'mixed'
        
        hindi_ratio = hindi_count / total
        if hindi_ratio > 0.4:
            return 'hindi'
        elif hindi_ratio < 0.15:
            return 'english'
        return 'mixed'
    
    def _detect_style(self, messages: List[Dict]) -> str:
        """
        Detect communication style.
        
        Algorithm:
        1. Check average message length
        2. Check formality indicators
        3. Check technical word density
        """
        lengths = []
        tech_count = 0
        casual_count = 0
        
        for msg in messages[-30:]:
            content = msg.get('content', '')
            if isinstance(content, list):
                content = ' '.join(str(item) for item in content)
            lengths.append(len(content))
            
            content_lower = content.lower()
            for word in self.TECH_INDICATORS:
                if word in content_lower:
                    tech_count += 1
            for word in self.CASUAL_INDICATORS:
                if word in content_lower:
                    casual_count += 1
        
        avg_length = sum(lengths) / len(lengths) if lengths else 0
        
        if tech_count > casual_count and tech_count > 5:
            return 'technical'
        elif casual_count > tech_count and casual_count > 5:
            return 'casual'
        elif avg_length < 30:
            return 'brief'
        elif avg_length > 100:
            return 'detailed'
        return 'neutral'
    
    def _extract_topics(self, messages: List[Dict]) -> List[Dict]:
        """
        Extract recurring topics/projects from conversation.
        
        Algorithm:
        1. Extract noun phrases (capitalized words, tech terms)
        2. Count frequency across all messages
        3. Return topics mentioned 3+ times with context
        """
        topic_counts = {}
        topic_contexts = {}
        
        for msg in messages:
            content = msg.get('content', '')
            if isinstance(content, list):
                content = ' '.join(str(item) for item in content)
            
            # Extract potential topics (capitalized words, tech terms)
            words = re.findall(r'\b[A-Z][a-zA-Z0-9]+\b', content)
            for word in words:
                if len(word) > 2 and word not in ('The', 'This', 'That', 'What', 'How', 'When', 'Where', 'Why', 'Can', 'Will', 'Just', 'Now', 'Hey', 'Hello', 'ZENITH', 'Sir'):
                    topic_counts[word] = topic_counts.get(word, 0) + 1
                    if word not in topic_contexts:
                        topic_contexts[word] = content[:100]
            
            # Also check for quoted terms
            quoted = re.findall(r'"([^"]+)"', content)
            for term in quoted:
                if len(term) > 2:
                    topic_counts[term] = topic_counts.get(term, 0) + 1
                    if term not in topic_contexts:
                        topic_contexts[term] = content[:100]
        
        # Return topics mentioned 3+ times
        topics = []
        for topic, count in sorted(topic_counts.items(), key=lambda x: -x[1]):
            if count >= 3:
                topics.append({
                    'name': topic,
                    'mentions': count,
                    'context': topic_contexts.get(topic, ''),
                })
        
        return topics[:10]  # Top 10 topics
    
    def _detect_habits(self, user_msgs: List[Dict], all_msgs: List[Dict]) -> Dict:
        """
        Detect user habits from message timestamps.
        
        Algorithm:
        1. Parse timestamps from messages
        2. Calculate average active hours
        3. Detect peak usage times
        4. Detect session patterns
        """
        hours = []
        days = []
        
        for msg in all_msgs:
            ts = msg.get('timestamp', '')
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    hours.append(dt.hour)
                    days.append(dt.strftime('%A'))
                except (ValueError, TypeError):
                    pass
        
        if not hours:
            return {'peak_hours': [], 'active_days': [], 'session_pattern': 'unknown'}
        
        # Find peak hours
        hour_counts = {}
        for h in hours:
            hour_counts[h] = hour_counts.get(h, 0) + 1
        peak_hours = sorted(hour_counts.keys(), key=lambda x: -hour_counts[x])[:3]
        
        # Find active days
        day_counts = {}
        for d in days:
            day_counts[d] = day_counts.get(d, 0) + 1
        active_days = sorted(day_counts.keys(), key=lambda x: -day_counts[x])[:3]
        
        # Detect pattern
        if peak_hours:
            avg_hour = sum(peak_hours) / len(peak_hours)
            if 6 <= avg_hour < 12:
                pattern = 'morning_person'
            elif 12 <= avg_hour < 17:
                pattern = 'afternoon_person'
            elif 17 <= avg_hour < 22:
                pattern = 'evening_person'
            else:
                pattern = 'night_owl'
        else:
            pattern = 'unknown'
        
        return {
            'peak_hours': peak_hours,
            'active_days': active_days,
            'session_pattern': pattern,
        }
    
    def _extract_preferences(self, messages: List[Dict]) -> Dict:
        """
        Extract explicit preferences from conversation.
        
        Algorithm:
        1. Look for preference statements ("I like X", "I prefer Y", "I use Z")
        2. Look for tool usage patterns (which tools are used most)
        3. Build preference map
        """
        preferences = {
            'likes': [],
            'dislikes': [],
            'tools_used': {},
            'response_length': 'medium',
        }
        
        like_patterns = [
            r'i (?:like|love|prefer|enjoy|use)\s+(.+?)(?:\.|,|$)',
            r'(?:accha|badhiya|sahi|achha)\s+(.+?)(?:\s+hai|\s+lagta)',
        ]
        dislike_patterns = [
            r'i (?:hate|dislike|dont like|don\'t like)\s+(.+?)(?:\.|,|$)',
            r'(?:bura|ganda|kharab)\s+(.+?)(?:\s+hai)',
        ]
        
        for msg in messages:
            content = msg.get('content', '')
            if isinstance(content, list):
                content = ' '.join(str(item) for item in content)
            content_lower = content.lower()
            
            for pattern in like_patterns:
                matches = re.findall(pattern, content_lower)
                for match in matches:
                    clean = match.strip()[:50]
                    if clean and clean not in preferences['likes']:
                        preferences['likes'].append(clean)
            
            for pattern in dislike_patterns:
                matches = re.findall(pattern, content_lower)
                for match in matches:
                    clean = match.strip()[:50]
                    if clean and clean not in preferences['dislikes']:
                        preferences['dislikes'].append(clean)
        
        return preferences
    
    def _empty_profile(self) -> Dict:
        return {
            'name': '',
            'language_preference': 'mixed',
            'communication_style': 'neutral',
            'topics': [],
            'habits': {'peak_hours': [], 'active_days': [], 'session_pattern': 'unknown'},
            'preferences': {'likes': [], 'dislikes': [], 'tools_used': {}, 'response_length': 'medium'},
            'first_seen': '',
            'last_seen': '',
            'total_messages': 0,
            'profile_confidence': 0.0,
        }


# =========================
# ALGORITHM 2: MOOD TRACKING
# =========================

class MoodTracker:
    """
    Tracks user mood over time using pattern matching.
    
    Algorithm:
    1. Analyze each user message for mood indicators
    2. Apply weighted scoring (recent messages have more weight)
    3. Calculate rolling mood average
    4. Detect mood shifts and trends
    """
    
    def __init__(self):
        self._mood_log = _load_json(str(_MOOD_LOG), {'entries': [], 'current_mood': 'neutral', 'mood_history': []})
    
    def detect_mood(self, message: str) -> Dict:
        """
        Detect mood from a single message.
        Returns mood type and confidence.
        """
        message_lower = message.lower()
        scores = {}
        
        for mood, patterns in UserProfileExtractor.MOOD_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    score += 1
            if score > 0:
                scores[mood] = score
        
        if not scores:
            return {'mood': 'neutral', 'confidence': 0.5, 'indicators': []}
        
        best_mood = max(scores, key=scores.get)
        total_score = sum(scores.values())
        confidence = min(scores[best_mood] / total_score, 1.0) if total_score > 0 else 0.5
        
        return {
            'mood': best_mood,
            'confidence': round(confidence, 2),
            'indicators': [m for m, s in scores.items() if s > 0],
        }
    
    def log_mood(self, mood: str, confidence: float, message: str = ''):
        """Log a mood entry with timestamp."""
        entry = {
            'mood': mood,
            'confidence': confidence,
            'timestamp': _now().isoformat(),
            'message_preview': message[:50],
        }
        self._mood_log['entries'].append(entry)
        self._mood_log['current_mood'] = mood
        
        # Keep last 100 entries
        if len(self._mood_log['entries']) > 100:
            self._mood_log['entries'] = self._mood_log['entries'][-100:]
        
        # Track mood transitions
        history = self._mood_log.get('mood_history', [])
        if history and history[-1]['mood'] != mood:
            history.append({'from': history[-1]['mood'], 'to': mood, 'at': _now().isoformat()})
            if len(history) > 50:
                history = history[-50:]
        elif not history:
            history.append({'mood': mood, 'at': _now().isoformat()})
        self._mood_log['mood_history'] = history
        
        _save_json(str(_MOOD_LOG), self._mood_log)
    
    def get_current_mood(self) -> str:
        """Get the current detected mood."""
        return self._mood_log.get('current_mood', 'neutral')
    
    def get_mood_trend(self, lookback: int = 10) -> Dict:
        """
        Analyze mood trend over recent messages.
        
        Algorithm:
        1. Take last N mood entries
        2. Calculate dominant mood
        3. Detect if mood is improving, worsening, or stable
        """
        entries = self._mood_log.get('entries', [])[-lookback:]
        
        if not entries:
            return {'trend': 'unknown', 'dominant': 'neutral', 'shifts': 0}
        
        # Count mood frequencies
        mood_counts = {}
        for e in entries:
            m = e.get('mood', 'neutral')
            mood_counts[m] = mood_counts.get(m, 0) + 1
        
        dominant = max(mood_counts, key=mood_counts.get)
        
        # Detect shifts
        shifts = 0
        for i in range(1, len(entries)):
            if entries[i].get('mood') != entries[i-1].get('mood'):
                shifts += 1
        
        # Detect trend direction
        positive_moods = {'excited', 'happy', 'curious', 'casual'}
        negative_moods = {'stressed', 'frustrated', 'tired'}
        
        recent = [e.get('mood', 'neutral') for e in entries[-3:]]
        positive_recent = sum(1 for m in recent if m in positive_moods)
        negative_recent = sum(1 for m in recent if m in negative_moods)
        
        if positive_recent > negative_recent:
            trend = 'improving'
        elif negative_recent > positive_recent:
            trend = 'worsening'
        else:
            trend = 'stable'
        
        return {'trend': trend, 'dominant': dominant, 'shifts': shifts}


# =========================
# ALGORITHM 3: CONTEXTUAL GREETING GENERATOR
# =========================

class GreetingGenerator:
    """
    Generates time-aware, context-aware, memory-aware greetings.
    
    Algorithm:
    1. Get current time → determine time-of-day greeting
    2. Check memory for last interaction context
    3. Check mood trend for emotional tone
    4. Combine into natural greeting
    """
    
    TIME_GREETINGS = {
        'early_morning': {  # 4-6
            'phrases': [
                "Early start today?",
                "Up before the sun, Lalit?",
                "Morning! You're up early.",
            ],
            'emoji': '',
        },
        'morning': {  # 6-12
            'phrases': [
                "Good morning, Lalit!",
                "Morning! Hope you slept well.",
                "Subah ho gayi! Ready to go?",
            ],
            'emoji': '',
        },
        'afternoon': {  # 12-17
            'phrases': [
                "Hey Lalit!",
                "Afternoon! What's the plan?",
                "Hey! How's it going?",
            ],
            'emoji': '',
        },
        'evening': {  # 17-21
            'phrases': [
                "Good evening!",
                "Hey! How was your day?",
                "Evening, Lalit!",
            ],
            'emoji': '',
        },
        'night': {  # 21-24
            'phrases': [
                "Working late tonight?",
                "Night owl mode activated.",
                "Hey! Still going strong?",
            ],
            'emoji': '',
        },
        'late_night': {  # 0-4
            'phrases': [
                "Up at this hour?",
                "Can't sleep? I'm here.",
                "Late night session, huh?",
            ],
            'emoji': '',
        },
    }
    
    CONTEXT_FOLLOWUPS = {
        'monday': ["New week, new grind. Let's go!", "Monday vibes. What's first?"],
        'friday': ["Almost weekend! What's the plan?", "Friday! We made it!"],
        'saturday': ["Weekend vibes! Grinding or chilling?", "Saturday! What's happening?"],
        'sunday': ["Sunday! Take it easy or going hard?", "Lazy Sunday or productive Sunday?"],
        'long_gap': [
            "Lalit! It's been a while. How've you been?",
            "Hey stranger! Good to see you again.",
            "Long time no talk! Everything okay?",
        ],
        'same_day': [
            "Welcome back!",
            "What else do you need?",
            "Still going?",
        ],
    }
    
    MOOD_TONE = {
        'stressed': ["I'm here to help lighten the load.", "Let's tackle this together."],
        'excited': ["Love the energy!", "That's the spirit!"],
        'frustrated': ["Let's figure this out.", "I'm with you, let's fix it."],
        'tired': ["Take it easy. I'll keep things brief.", "Want me to keep it short?"],
        'happy': ["Great to see you in good spirits!", "Nice!"],
        'curious': ["Ooh, interesting question!", "Let me think about that..."],
        'casual': ["What's up?", "Hey hey!"],
        'neutral': ["What's the plan?", "How can I help?"],
    }
    
    def generate_greeting(self, profile: Dict, mood_trend: Dict, last_interaction: Optional[str] = None) -> str:
        """
        Generate a contextual greeting.
        
        Algorithm:
        1. Time-based greeting selection
        2. Day-of-week context
        3. Gap since last interaction
        4. Mood-aware tone adjustment
        5. Memory-aware follow-up
        """
        now = _now()
        
        # Step 1: Time-based greeting
        hour = now.hour
        if 4 <= hour < 6:
            time_key = 'early_morning'
        elif 6 <= hour < 12:
            time_key = 'morning'
        elif 12 <= hour < 17:
            time_key = 'afternoon'
        elif 17 <= hour < 21:
            time_key = 'evening'
        elif 21 <= hour <= 23:
            time_key = 'night'
        else:
            time_key = 'late_night'
        
        import random
        base_greeting = random.choice(self.TIME_GREETINGS[time_key]['phrases'])
        
        # Step 2: Day context
        day_name = now.strftime('%A').lower()
        if day_name in self.CONTEXT_FOLLOWUPS:
            day_msg = random.choice(self.CONTEXT_FOLLOWUPS[day_name])
        else:
            day_msg = ""
        
        # Step 3: Gap detection
        gap_msg = ""
        if last_interaction:
            try:
                last_dt = datetime.fromisoformat(last_interaction)
                gap = now - last_dt
                if gap.days >= 3:
                    gap_msg = random.choice(self.CONTEXT_FOLLOWUPS['long_gap'])
                elif gap.days == 0:
                    gap_msg = random.choice(self.CONTEXT_FOLLOWUPS['same_day'])
            except (ValueError, TypeError):
                pass
        
        # Step 4: Mood tone
        current_mood = mood_trend.get('dominant', 'neutral')
        mood_msg = random.choice(self.MOOD_TONE.get(current_mood, self.MOOD_TONE['neutral']))
        
        # Step 5: Combine
        parts = [base_greeting]
        if gap_msg:
            parts.append(gap_msg)
        elif day_msg:
            parts.append(day_msg)
        
        greeting = ' '.join(parts)
        
        # Add name naturally (not every time)
        if profile.get('name') and random.random() > 0.5:
            greeting = greeting.replace('Lalit', profile['name'])
        
        return greeting


# =========================
# ALGORITHM 4: RESPONSE STYLE ADAPTER
# =========================

class ResponseAdapter:
    """
    Adapts AI response style based on user's current state.
    
    Algorithm:
    1. Analyze user's message length → match response length
    2. Analyze user's mood → adjust tone
    3. Analyze user's style → mirror formality
    4. Provide response guidelines to the LLM
    """
    
    def get_response_guidelines(self, profile: Dict, mood: str, user_message: str) -> str:
        """
        Generate response style guidelines for the current context.
        These get injected into the system prompt dynamically.
        """
        guidelines = []
        
        # Length matching
        msg_len = len(user_message)
        if msg_len < 15:
            guidelines.append("Keep your response SHORT (1-2 sentences). Match their brevity.")
        elif msg_len < 50:
            guidelines.append("Keep your response moderate (2-3 sentences).")
        else:
            guidelines.append("Give a thoughtful, detailed response. They put effort into their message.")
        
        # Mood-based tone
        mood_guidelines = {
            'stressed': "They seem stressed. Be supportive and efficient. Offer to help organize. Don't add more complexity.",
            'excited': "They're excited! Match their energy. Celebrate with them!",
            'frustrated': "They're frustrated. Be patient. Focus on solutions. Acknowledge the difficulty.",
            'tired': "They seem tired. Be concise. Offer encouragement. Suggest breaks if appropriate.",
            'happy': "They're in a good mood! Keep it light and positive.",
            'curious': "They're curious! Be thorough. Explain well. Share interesting details.",
            'casual': "They're being casual. Match their energy. Be relaxed and friendly.",
            'neutral': "Be natural and conversational. Vary your response style.",
        }
        guidelines.append(mood_guidelines.get(mood, mood_guidelines['neutral']))
        
        # Style mirroring
        style = profile.get('communication_style', 'neutral')
        if style == 'technical':
            guidelines.append("They're technical. Use precise terms. Don't over-explain basics.")
        elif style == 'casual':
            guidelines.append("Be casual. Use contractions. Mix Hindi-English if they do.")
        elif style == 'brief':
            guidelines.append("Keep it short. They prefer concise answers.")
        elif style == 'detailed':
            guidelines.append("Give detailed answers. They appreciate thoroughness.")
        
        # Language preference
        lang = profile.get('language_preference', 'mixed')
        if lang == 'hindi':
            guidelines.append("Mix Hindi and English naturally. Use Hinglish.")
        elif lang == 'english':
            guidelines.append("Use English primarily.")
        else:
            guidelines.append("Mirror their language mix. If they use Hinglish, you use Hinglish.")
        
        return '\n'.join(guidelines)


# =========================
# MAIN: MEMORY BRAIN
# =========================

class MemoryBrain:
    """
    The central thinking layer that coordinates all algorithms.
    
    Flow:
    1. On session start: Load profile, generate greeting
    2. On each message: Detect mood, update profile, get response guidelines
    3. On session end: Save profile, summarize conversation
    """
    
    def __init__(self):
        self._extractor = UserProfileExtractor()
        self._mood_tracker = MoodTracker()
        self._greeting_gen = GreetingGenerator()
        self._response_adapter = ResponseAdapter()
        self._profile = self._load_profile()
        self._interaction_log = _load_json(str(_INTERACTION_LOG), {'sessions': []})
    
    def _load_profile(self) -> Dict:
        """Load or build user profile."""
        profile = _load_json(str(_PROFILE_FILE))
        if not profile:
            profile = self._extractor._empty_profile()
            _save_json(str(_PROFILE_FILE), profile)
        return profile
    
    def initialize_from_history(self):
        """Build profile from conversation history on first run."""
        try:
            with open(_CONVERSATION_LOG, 'r', encoding='utf-8') as f:
                messages = json.load(f)
            
            if messages:
                new_profile = self._extractor.extract_from_history(messages)
                
                # Merge with existing profile (don't overwrite explicit data)
                for key, value in new_profile.items():
                    if value and value != [] and value != {} and key != 'profile_confidence':
                        if not self._profile.get(key) or key == 'total_messages':
                            self._profile[key] = value
                
                self._profile['last_updated'] = _now().isoformat()
                _save_json(str(_PROFILE_FILE), self._profile)
        except Exception as e:
            print(f"Memory brain init error: {e}")
    
    def process_message(self, message: str) -> Dict:
        """
        Process incoming user message.
        Returns: mood, guidelines, context for the AI.
        """
        # Detect mood
        mood_result = self._mood_tracker.detect_mood(message)
        self._mood_tracker.log_mood(
            mood_result['mood'],
            mood_result['confidence'],
            message
        )
        
        # Get mood trend
        mood_trend = self._mood_tracker.get_mood_trend()
        
        # Get response guidelines
        guidelines = self._response_adapter.get_response_guidelines(
            self._profile, mood_result['mood'], message
        )
        
        return {
            'mood': mood_result['mood'],
            'mood_confidence': mood_result['confidence'],
            'mood_trend': mood_trend,
            'guidelines': guidelines,
            'profile': self._profile,
        }
    
    def get_greeting(self) -> str:
        """Generate a contextual greeting for session start."""
        mood_trend = self._mood_tracker.get_mood_trend()
        last_interaction = self._profile.get('last_seen')
        return self._greeting_gen.generate_greeting(self._profile, mood_trend, last_interaction)
    
    def get_session_context(self) -> str:
        """
        Get full context string to inject into AI system prompt.
        This is the "brain" output that makes the AI think.
        """
        context_parts = []
        
        # User identity
        name = self._profile.get('name', '')
        if name:
            context_parts.append(f"User's name: {name}")
        
        # Language preference
        lang = self._profile.get('language_preference', 'mixed')
        context_parts.append(f"Preferred language: {lang}")
        
        # Style
        style = self._profile.get('communication_style', 'neutral')
        context_parts.append(f"Communication style: {style}")
        
        # Current mood
        mood = self._mood_tracker.get_current_mood()
        mood_trend = self._mood_tracker.get_mood_trend()
        context_parts.append(f"Current mood: {mood} (trend: {mood_trend.get('trend', 'unknown')})")
        
        # Topics
        topics = self._profile.get('topics', [])
        if topics:
            topic_names = [t['name'] for t in topics[:5]]
            context_parts.append(f"Frequent topics: {', '.join(topic_names)}")
        
        # Habits
        habits = self._profile.get('habits', {})
        pattern = habits.get('session_pattern', 'unknown')
        if pattern != 'unknown':
            context_parts.append(f"User's pattern: {pattern.replace('_', ' ')}")
        
        # Preferences
        prefs = self._profile.get('preferences', {})
        if prefs.get('likes'):
            context_parts.append(f"Likes: {', '.join(prefs['likes'][:3])}")
        if prefs.get('dislikes'):
            context_parts.append(f"Dislikes: {', '.join(prefs['dislikes'][:3])}")
        
        # Last interaction
        last_seen = self._profile.get('last_seen', '')
        if last_seen:
            try:
                last_dt = datetime.fromisoformat(last_seen)
                gap = _now() - last_dt
                if gap.days > 0:
                    context_parts.append(f"Last interaction: {gap.days
} days ago")
                else:
                    context_parts.append(f"Last interaction: today")
            except (ValueError, TypeError):
                pass
        
        return '\n'.join(context_parts) if context_parts else "No user context available yet."
    
    def update_last_seen(self):
        """Update the last interaction timestamp."""
        self._profile['last_seen'] = _now().isoformat()
        _save_json(str(_PROFILE_FILE), self._profile)
    
    def get_response_style(self, user_message: str) -> str:
        """Get dynamic response style guidelines for the current message."""
        mood = self._mood_tracker.get_current_mood()
        return self._response_adapter.get_response_guidelines(self._profile, mood, user_message)


# =========================
# MODULE-LEVEL ACTION HANDLER
# =========================
_brain_instance = None

def _get_brain():
    global _brain_instance
    if _brain_instance is None:
        try:
            _brain_instance = MemoryBrain()
        except Exception as e:
            return None, str(e)
    return _brain_instance, None


def handle_memory_brain(parameters: dict) -> str:
    """Module-level handler for the action loader."""
    action = parameters.get("action", "")
    brain, err = _get_brain()
    if err:
        return f"❌ Memory brain init failed: {err}"

    try:
        if action == "get_profile":
            return brain.get_session_context()
        elif action == "get_mood":
            mood = brain._mood_tracker.get_current_mood()
            trend = brain._mood_tracker.get_mood_trend()
            return f"Current mood: {mood}, trend: {trend.get('trend', 'unknown')}"
        elif action == "store":
            key = parameters.get("key", "")
            value = parameters.get("value", "")
            category = parameters.get("category", "fact")
            if not key or not value:
                return "❌ 'key' and 'value' are required for store action."
            profile = _load_json(str(_PROFILE_FILE), {})
            facts = profile.setdefault("stored_facts", {})
            facts[key] = {"value": value, "category": category, "timestamp": _now().isoformat()}
            _save_json(str(_PROFILE_FILE), profile)
            return f"✅ Stored '{key}' = '{value}' [{category}]"
        elif action == "recall":
            key = parameters.get("key", "")
            profile = _load_json(str(_PROFILE_FILE), {})
            facts = profile.get("stored_facts", {})
            if key:
                entry = facts.get(key)
                if entry:
                    return f"🔍 '{key}': {entry.get('value')} [{entry.get('category')}]"
                return f"❌ No memory found for key '{key}'."
            if facts:
                lines = [f"• {k}: {v.get('value')} [{v.get('category')}]" for k, v in list(facts.items())[:10]]
                return "📂 Stored memories:\n" + "\n".join(lines)
            return "No memories stored yet."
        elif action == "clear":
            profile = _load_json(str(_PROFILE_FILE), {})
            profile.pop("stored_facts", None)
            _save_json(str(_PROFILE_FILE), profile)
            return "✅ Memory cleared."
        else:
            return f"❌ Unknown action '{action}'. Use: store, recall, get_profile, get_mood, clear."
    except Exception as e:
        return f"❌ Memory brain error: {e}"

