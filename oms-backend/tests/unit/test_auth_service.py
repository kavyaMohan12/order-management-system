from app.services import auth_service


def test_create_user_hashes_password(db_session):
    user = auth_service.create_user(db_session, "alice@example.com", "longpassword1")
    assert user.email == "alice@example.com"
    assert user.hashed_password != "longpassword1"
    assert len(user.hashed_password) > 20


def test_authenticate_user_success(db_session):
    auth_service.create_user(db_session, "bob@example.com", "longpassword1")
    user = auth_service.authenticate_user(
        db_session, "bob@example.com", "longpassword1"
    )
    assert user is not None
    assert user.email == "bob@example.com"


def test_authenticate_user_wrong_password(db_session):
    auth_service.create_user(db_session, "carol@example.com", "longpassword1")
    assert (
        auth_service.authenticate_user(db_session, "carol@example.com", "wrong-pw")
        is None
    )


def test_authenticate_user_unknown_email(db_session):
    assert (
        auth_service.authenticate_user(db_session, "ghost@example.com", "x")
        is None
    )


def test_get_user_by_email(db_session):
    auth_service.create_user(db_session, "dave@example.com", "longpassword1")
    found = auth_service.get_user_by_email(db_session, "dave@example.com")
    assert found is not None
    assert found.email == "dave@example.com"
