#!/usr/bin/env python3
"""Update ALLOWED_ORIGINS in .env.docker for homelab."""
import re

path = "/root/Proaktiv-Dokument-Hub/backend/.env.docker"
with open(path) as f:
    c = f.read()
c = re.sub(
    r'ALLOWED_ORIGINS=.*',
    'ALLOWED_ORIGINS="[https://proaktiv-dokument-hub.vercel.app,http://192.168.77.127:3000]"',
    c,
)
with open(path, "w") as f:
    f.write(c)
print("OK")
