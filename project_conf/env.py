import os
import sys
import json
from typing import Iterable

import trafaret as t


__all__ = ('raw_environ', 'environ')


def make_list(val: str) -> Iterable[str]:
    return val.split(',')

def opt(name: str) -> t.Key:
    return t.Key(name, optional=True)


env_t = t.Dict({
    'DJANGO_DEBUG': t.StrBool(),
    'DOMAIN': t.String(),
    'WWW_DOMAIN': t.String(),

    'DATABASE_NAME': t.String(),
    'DATABASE_HOST': t.String(),
    'DATABASE_USER': t.String(),
    'DATABASE_PASSWORD': t.String(),

    'SUPERUSERS': t.String() >> make_list,
    'SUPERUSER_PASSWORD': t.String(),

    'EMAIL_EXCLUDE_LIST': t.String() >> make_list,

    opt('MEDIA_URL'): t.String(),
    opt('STATIC_URL'): t.String(),
    opt('EMAIL_BACKEND'): t.String(),

}).ignore_extra('*')


try:
    environ = env_t.check_and_return(os.environ)
    raw_environ = {}
    for key in env_t.keys_names():
        if key in os.environ:
            environ.setdefault(key, None)
            raw_environ[key] = os.environ.get(key, None)

except t.DataError as err:
    sys.stderr.write('\x1B[31;1mcheck following env errors:\x1B[m\n')
    for key, err in err.as_dict().items():
        sys.stderr.write('{}: {}\n'.format(key, err))
    sys.exit(1)


if __name__ == '__main__':
    target = environ
    if len(sys.argv) > 1 and sys.argv[1] == 'raw':
        target = raw_environ
    if len(sys.argv) > 2 and sys.argv[2] == 'export':
        for key, value in raw_environ.items():
            sys.stdout.write('{}={}\n'.format(key, value))
    else:
        json.dump(target, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write('\n')
