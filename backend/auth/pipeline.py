def create_user(backend, strategy, details, response, user=None, *args,
                **kwargs):
    if user:
        return {'is_new': False}

    fields = None

    if backend.name == 'google-oauth2':
        fields = {
            'email': details.get('email'),
            'first_name': details.get('first_name'),
            'last_name': details.get('last_name'),
        }

    if not fields or not fields.get('email'):
        return

    result = {
        'is_new': True,
        'user': strategy.create_user(**fields)
    }

    return result
