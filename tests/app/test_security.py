from server.app.security import hash_password, sign_session_token, unsign_session_token, verify_password


def test_hash_and_verify_password_round_trip():
    password_hash = hash_password("a-very-good-password")

    assert verify_password("a-very-good-password", password_hash) is True
    assert verify_password("wrong-password", password_hash) is False


def test_signed_session_tokens_round_trip():
    signed = sign_session_token("session-token")

    assert unsign_session_token(signed) == "session-token"
    assert unsign_session_token(f"{signed}tampered") is None

