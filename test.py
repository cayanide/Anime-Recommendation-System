async def test_create_user(db):
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "securepassword123"
    }
    user = await create_user(user_data, db)
    print(f"Created user: {user.username}, {user.email}")
