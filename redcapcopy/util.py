def is_super_token(token):
    return len(token) == 64

def change_project_title(data, project_title):
    data['project_title'] = project_title
    return data
