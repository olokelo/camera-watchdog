#!/usr/bin/env python3

import bcrypt

user = input('enter user: ')
passwd = input('enter password: ')
salt = bcrypt.gensalt(rounds=12)
hashed = bcrypt.hashpw(passwd.encode('utf8'), salt).decode('ascii')

with open('.htpasswd', 'w') as f:
    f.write(f'{user}:{hashed}')

