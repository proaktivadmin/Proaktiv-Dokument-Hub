#!/bin/bash
# Fix ALLOWED_ORIGINS in homelab .env.docker
sed -i 's|ALLOWED_ORIGINS=.*|ALLOWED_ORIGINS="[https://proaktiv-dokument-hub.vercel.app,http://192.168.77.127:3000]"|' /root/Proaktiv-Dokument-Hub/backend/.env.docker
