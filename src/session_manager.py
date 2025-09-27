"""Session Manager Module for Google Maps Mall Scraping.

Manages authentication context, cookies, and session state for Google Maps interactions.
Handles session persistence, token management, and authentication state.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

# Configure logging
logger = logging.getLogger(__name__)


class GoogleMapsSession:
    """Represents a Google Maps browsing session with authentication context."""

    def __init__(self, session_id: Optional[str] = None) -> None:
        """Initialize a new Google Maps session.

        Args:
            session_id: Optional custom session identifier. Auto-generated if not provided.
        """
        self.session_id = session_id or f"session_{int(time.time())}"
        self.created_at = time.time()
        self.last_activity = time.time()
        self.cookies: Dict[str, Any] = {}
        self.headers: Dict[str, str] = {}
        self.auth_tokens: Dict[str, Any] = {}
        self.user_agent = self._get_default_user_agent()
        self.viewport = {"width": 1920, "height": 1080}
        self.timezone = "Europe/London"
        self.language = "en-GB"
        self.location_granted = False
        self.session_metadata: Dict[str, Any] = {}

        logger.info(f"Initialized Google Maps session: {self.session_id}")

    def _get_default_user_agent(self) -> str:
        """Get a realistic user agent string."""
        return (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/119.0.0.0 Safari/537.36"
        )

    def update_activity(self) -> None:
        """Update the last activity timestamp."""
        self.last_activity = time.time()

    def set_cookie(
        self,
        name: str,
        value: str,
        domain: str = ".google.com",
        path: str = "/",
        secure: bool = True,
        http_only: bool = False,
    ) -> None:
        """Set a cookie in the session.

        Args:
            name: Cookie name
            value: Cookie value
            domain: Cookie domain
            path: Cookie path
            secure: Whether cookie requires HTTPS
            http_only: Whether cookie is HTTP-only
        """
        self.cookies[name] = {
            "value": value,
            "domain": domain,
            "path": path,
            "secure": secure,
            "http_only": http_only,
            "created": time.time(),
        }
        self.update_activity()
        logger.debug(f"Set cookie: {name} for domain {domain}")

    def get_cookie(self, name: str) -> Optional[str]:
        """Get a cookie value by name.

        Args:
            name: Cookie name

        Returns:
            Cookie value if found, None otherwise
        """
        cookie = self.cookies.get(name)
        if cookie and isinstance(cookie, dict):
            return cookie.get("value")
        return None

    def set_auth_token(
        self, token_type: str, token_value: str, expires_at: Optional[float] = None
    ) -> None:
        """Set an authentication token.

        Args:
            token_type: Type of authentication token (e.g., 'bearer', 'google_auth')
            token_value: The token value
            expires_at: Optional expiration timestamp
        """
        self.auth_tokens[token_type] = {
            "value": token_value,
            "expires_at": expires_at,
            "created_at": time.time(),
        }
        self.update_activity()
        logger.info(f"Set auth token: {token_type}")

    def get_auth_token(self, token_type: str) -> Optional[str]:
        """Get an authentication token by type.

        Args:
            token_type: Type of authentication token

        Returns:
            Token value if found and not expired, None otherwise
        """
        token_info = self.auth_tokens.get(token_type)
        if token_info:
            # Check if token is expired
            if token_info.get("expires_at") and time.time() > token_info["expires_at"]:
                logger.warning(f"Auth token {token_type} has expired")
                return None
            return token_info.get("value")
        return None

    def set_location_context(
        self,
        latitude: float,
        longitude: float,
        accuracy: int = 100,
        granted: bool = True,
    ) -> None:
        """Set geolocation context for the session.

        Args:
            latitude: Geographic latitude
            longitude: Geographic longitude
            accuracy: Location accuracy in meters
            granted: Whether location permission is granted
        """
        self.session_metadata["location"] = {
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": accuracy,
            "granted": granted,
        }
        self.location_granted = granted
        self.update_activity()
        logger.info(f"Set location context: {latitude}, {longitude}")

    def get_request_headers(self, url: str) -> Dict[str, str]:
        """Get appropriate headers for a request to the given URL."""
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": f"{self.language};q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        # Add referer if we have session metadata
        parsed_url = urlparse(url)
        if parsed_url.netloc == "www.google.com":
            headers["Referer"] = "https://www.google.com/"

        # Add authorization headers if available
        if self.auth_tokens:
            for token_type, token_info in self.auth_tokens.items():
                if token_type.lower() == "bearer":
                    headers["Authorization"] = f"Bearer {token_info['value']}"
                elif token_type.lower() == "google_auth":
                    headers["Google-Auth"] = token_info["value"]

        self.update_activity()
        return headers

    def get_cookie_header(self, domain: str) -> str:
        """Get cookie header string for the specified domain."""
        relevant_cookies = []
        for name, cookie_data in self.cookies.items():
            if isinstance(cookie_data, dict):
                cookie_domain = cookie_data.get("domain", "")
                if domain.endswith(cookie_domain) or cookie_domain.endswith(domain):
                    relevant_cookies.append(f"{name}={cookie_data['value']}")

        return "; ".join(relevant_cookies)

    def is_expired(self, max_age_hours: int = 24) -> bool:
        """Check if the session is expired based on inactivity."""
        hours_since_activity = (time.time() - self.last_activity) / 3600
        return hours_since_activity > max_age_hours

    def to_dict(self) -> Dict[str, Any]:
        """Serialize session to dictionary."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "cookies": self.cookies,
            "headers": self.headers,
            "auth_tokens": self.auth_tokens,
            "user_agent": self.user_agent,
            "viewport": self.viewport,
            "timezone": self.timezone,
            "language": self.language,
            "location_granted": self.location_granted,
            "session_metadata": self.session_metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GoogleMapsSession":
        """Deserialize session from dictionary.

        Args:
            data: Dictionary containing session data

        Returns:
            Deserialized GoogleMapsSession instance
        """
        session = cls(session_id=data.get("session_id"))
        session.created_at = data.get("created_at", time.time())
        session.last_activity = data.get("last_activity", time.time())
        session.cookies = data.get("cookies", {})
        session.headers = data.get("headers", {})
        session.auth_tokens = data.get("auth_tokens", {})
        session.user_agent = data.get("user_agent", session._get_default_user_agent())
        session.viewport = data.get("viewport", {"width": 1920, "height": 1080})
        session.timezone = data.get("timezone", "Europe/London")
        session.language = data.get("language", "en-GB")
        session.location_granted = data.get("location_granted", False)
        session.session_metadata = data.get("session_metadata", {})
        return session


class SessionManager:
    """Manages multiple Google Maps sessions with persistence."""

    def __init__(self, storage_path: Optional[str] = None) -> None:
        """Initialize session manager.

        Args:
            storage_path: Optional path for persistent session storage
        """
        self.storage_path = Path(storage_path) if storage_path else None
        self.sessions: Dict[str, GoogleMapsSession] = {}
        self.active_session_id: Optional[str] = None

        # Load existing sessions if storage path provided
        if self.storage_path:
            self._load_sessions()

        logger.info(
            f"SessionManager initialized with {len(self.sessions)} existing sessions"
        )

    def create_session(self, session_id: Optional[str] = None) -> GoogleMapsSession:
        """Create a new session.

        Args:
            session_id: Optional custom session identifier

        Returns:
            Newly created GoogleMapsSession
        """
        session = GoogleMapsSession(session_id)
        self.sessions[session.session_id] = session

        if not self.active_session_id:
            self.active_session_id = session.session_id

        self._save_sessions()
        logger.info(f"Created new session: {session.session_id}")
        return session

    def get_session(
        self, session_id: Optional[str] = None
    ) -> Optional[GoogleMapsSession]:
        """Get a session by ID, or the active session if no ID provided.

        Args:
            session_id: Optional session ID to retrieve

        Returns:
            GoogleMapsSession if found and not expired, None otherwise
        """
        target_id = session_id or self.active_session_id
        if target_id and target_id in self.sessions:
            session = self.sessions[target_id]
            if not session.is_expired():
                session.update_activity()
                return session
            else:
                logger.warning(f"Session {target_id} has expired, removing")
                del self.sessions[target_id]
                self._save_sessions()

        return None

    def get_or_create_session(
        self, session_id: Optional[str] = None
    ) -> GoogleMapsSession:
        """Get existing session or create new one.

        Args:
            session_id: Optional session ID to retrieve or create

        Returns:
            Existing or newly created GoogleMapsSession
        """
        session = self.get_session(session_id)
        if not session:
            session = self.create_session(session_id)
        return session

    def set_active_session(self, session_id: str) -> None:
        """Set the active session.

        Args:
            session_id: Session ID to set as active
        """
        if session_id in self.sessions:
            self.active_session_id = session_id
            logger.info(f"Set active session to: {session_id}")
        else:
            logger.warning(f"Session {session_id} not found")

    def delete_session(self, session_id: str) -> None:
        """Delete a session.

        Args:
            session_id: Session ID to delete
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            if self.active_session_id == session_id:
                self.active_session_id = (
                    next(iter(self.sessions.keys())) if self.sessions else None
                )
            self._save_sessions()
            logger.info(f"Deleted session: {session_id}")
        else:
            logger.warning(f"Session {session_id} not found for deletion")

    def cleanup_expired_sessions(self) -> None:
        """Remove expired sessions from memory and storage."""
        expired_ids = [
            sid for sid, session in self.sessions.items() if session.is_expired()
        ]
        for sid in expired_ids:
            del self.sessions[sid]
            logger.info(f"Cleaned up expired session: {sid}")

        if expired_ids:
            self._save_sessions()

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions with metadata."""
        return [
            {
                "session_id": sid,
                "created_at": session.created_at,
                "last_activity": session.last_activity,
                "is_active": sid == self.active_session_id,
                "is_expired": session.is_expired(),
                "cookies_count": len(session.cookies),
                "auth_tokens_count": len(session.auth_tokens),
            }
            for sid, session in self.sessions.items()
        ]

    def _load_sessions(self):
        """Load sessions from storage."""
        if not self.storage_path or not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for session_data in data.get("sessions", []):
                session = GoogleMapsSession.from_dict(session_data)
                self.sessions[session.session_id] = session

            self.active_session_id = data.get("active_session_id")
            logger.info(
                f"Loaded {len(self.sessions)} sessions from {self.storage_path}"
            )

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to load sessions from {self.storage_path}: {e}")

    def _save_sessions(self):
        """Save sessions to storage."""
        if not self.storage_path:
            return

        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "sessions": [session.to_dict() for session in self.sessions.values()],
                "active_session_id": self.active_session_id,
                "saved_at": time.time(),
            }

            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)

            logger.debug(f"Saved {len(self.sessions)} sessions to {self.storage_path}")

        except Exception as e:
            logger.error(f"Failed to save sessions to {self.storage_path}: {e}")


def create_session_manager(storage_path: Optional[str] = None) -> SessionManager:
    """Factory function to create a session manager."""
    return SessionManager(storage_path)


# Global session manager instance
_default_session_manager: Optional[SessionManager] = None


def get_default_session_manager() -> SessionManager:
    """Get the default global session manager."""
    global _default_session_manager
    if _default_session_manager is None:
        _default_session_manager = SessionManager()
    return _default_session_manager
