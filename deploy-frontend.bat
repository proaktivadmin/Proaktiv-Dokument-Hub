@echo off
echo Deploying frontend to Railway...
railway link -s blissful-quietude
railway redeploy --yes
echo Frontend deployment triggered!
