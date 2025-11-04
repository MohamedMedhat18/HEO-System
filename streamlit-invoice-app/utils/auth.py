def hash_password(plain):
    import bcrypt
    return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain, hashed):
    import bcrypt
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

def create_admin_user(username, password):
    hashed_password = hash_password(password)
    return {"username": username, "password": hashed_password, "role": "admin"}

def create_agent_user(username, password):
    hashed_password = hash_password(password)
    return {"username": username, "password": hashed_password, "role": "agent"}