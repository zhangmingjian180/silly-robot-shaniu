from kivy.storage.jsonstore import JsonStore

store = JsonStore('auth.json')

def save_token(token):
    store.put('auth', token=token)

def get_token():
    if store.exists('auth'):
        return store.get('auth')['token']
    return None

def clear_token():
    if store.exists('auth'):
        store.delete('auth')

def exists_token():
    if store.exists('auth'):
        if "token" in store.get('auth'):
            return True
    return False

def save_info(info):
    store.put("info", **info)

def get_info():
    if store.exists('info'):
        return store.get('info')
    return None

def clear_info():
    if store.exists('info'):
        store.delete('info')
