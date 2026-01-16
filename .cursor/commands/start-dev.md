# Start Development Environment

Run the development environment and verify all services are healthy:

1. Start Docker containers: `docker compose up -d`
2. Wait for containers to be ready (check with `docker compose ps`)
3. Test backend health: `curl http://localhost:8000/api/health`
4. Verify frontend is accessible at `http://localhost:3000`
5. Report status of all services

If any service fails, show the logs with `docker compose logs [service]`
