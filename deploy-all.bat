@echo off
echo Deploying both services to Railway...

echo.
echo [1/2] Deploying backend...
railway link -s Proaktiv-Dokument-Hub
railway redeploy --yes

echo.
echo [2/2] Deploying frontend...
railway link -s blissful-quietude
railway redeploy --yes

echo.
echo Both deployments triggered!
