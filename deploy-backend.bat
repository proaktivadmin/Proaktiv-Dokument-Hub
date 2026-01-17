@echo off
echo Deploying backend to Railway...
railway link -s Proaktiv-Dokument-Hub
railway redeploy --yes
echo Backend deployment triggered!
