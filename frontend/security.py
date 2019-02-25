from database_access_object import Database, connect_to_db

db = connect_to_db("teams")
table = db['registrations']

def authenticate(username, password):
    user = db['registrations'].find_one(username=username, password=password)
    return user
    
    # user = username_mapping.get(username, None)
    # if user and safe_str_cmp(user.password, password):
    #     return user
    # else:
    #     return None
