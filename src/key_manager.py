import keyring

def keep_secret(key_name, value):
    keyring.set_password("Gandalf_Guard", key_name, value)

def get_secret(key_name):
    return keyring.get_password("Gandalf_guard", key_name)

