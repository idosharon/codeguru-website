def get_group(user):
    return getattr(user.profile, "group", None)
