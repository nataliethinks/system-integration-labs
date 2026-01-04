#!/usr/bin/env python3

"""
Flask + JWT + HTTPS + simple IAM-style role checks
--------------------------------------------------
Run:
  python app.py
Then (in a separate terminal) test using the curl commands shown in the lab guide.

Generate a self-signed cert first (development only):
  openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
"""

import os
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import Flask, request, jsonify, g
import jwt

# ===== Configuration =====
SECRET = os.environ.get("JWT_SECRET", "dev-only-change-me")  # use env var in real deployments
ISSUER = "auth-demo"
AUDIENCE = "api-demo"

# Demo users (replace with DB/IdP in real life)
USERS = {
    "user": {"password": "userpw", "role": "user"},
    "admin": {"password": "adminpw", "role": "admin"},
}

app = Flask(__name__)


# ===== Helpers =====
def generate_token(username: str, role: str, minutes: int = 15) -> str:
    now = datetime.now(tz=timezone.utc)
    payload = {
        "sub": username,
        "role": role,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=minutes)).timestamp()),
        "iss": ISSUER,
        "aud": AUDIENCE,
    }
    token = jwt.encode(payload, SECRET, algorithm="HS256")
    # PyJWT v2+ returns str already; ensure str for safety
    return token if isinstance(token, str) else token.decode("utf-8")


def _bearer_token_from_header() -> str | None:
    auth = request.headers.get("Authorization", "")
    parts = auth.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = _bearer_token_from_header()
        if not token:
            return jsonify({"error": "Missing Bearer token"}), 401
        try:
            claims = jwt.decode(
                token,
                SECRET,
                algorithms=["HS256"],
                audience=AUDIENCE,
                issuer=ISSUER,
                options={"require": ["exp", "iat", "nbf"]},
            )
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"error": "Invalid token", "detail": str(e)}), 401

        # attach to request context
        g.user = claims.get("sub")
        g.role = claims.get("role")
        g.claims = claims
        return fn(*args, **kwargs)

    return wrapper


def require_role(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            role = getattr(g, "role", None)
            if role not in roles:
                return (
                    jsonify(
                        {
                            "error": "Forbidden",
                            "detail": f"Requires role in {roles}, but you have '{role}'",
                        }
                    ),
                    403,
                )
            return fn(*args, **kwargs)

        return wrapper

    return decorator


# ===== Routes =====
@app.get("/")
def index():
    return jsonify({"status": "ok", "message": "Use /login to obtain a JWT."})


@app.post("/login")
def login():
    """
    Body: {"username": "...", "password": "..."}
    Returns: {"access_token": "...", "token_type": "Bearer", "expires_in": 900}
    """
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    user_record = USERS.get(username)
    if not user_record or user_record.get("password") != password:
        return jsonify({"error": "Invalid credentials"}), 401

    token = generate_token(username=username, role=user_record["role"], minutes=15)
    return jsonify({"access_token": token, "token_type": "Bearer", "expires_in": 900})


@app.get("/secure")
@token_required
def secure():
    return jsonify(
        {
            "message": "You have accessed a secure endpoint.",
            "user": getattr(g, "user", None),
            "role": getattr(g, "role", None),
            "claims": getattr(g, "claims", {}),
        }
    )


@app.get("/secure-admin")
@token_required
@require_role("admin")
def secure_admin():
    return jsonify(
        {
            "message": "Admin-only data",
            "user": getattr(g, "user", None),
            "role": getattr(g, "role", None),
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    cert_path = os.environ.get("CERT_PATH", "cert.pem")
    key_path = os.environ.get("KEY_PATH", "key.pem")

    ssl_context = None
    if os.path.exists(cert_path) and os.path.exists(key_path):
        ssl_context = (cert_path, key_path)
        print(f"Starting HTTPS server on https://localhost:{port}")
    else:
        print("cert.pem or key.pem not found — starting HTTP server (dev only).")

    # Debug on so you can see errors quickly during the lab
    app.run(host="0.0.0.0", port=port, debug=True, ssl_context=ssl_context)
