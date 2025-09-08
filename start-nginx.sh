#!/bin/bash

echo "Starting TherapyBot with Nginx Reverse Proxy..."

# Check if SSL certificates exist
if [ ! -f "./nginx/ssl/cert.pem" ] || [ ! -f "./nginx/ssl/key.pem" ]; then
    echo "SSL certificates not found. Setting up development certificates..."
    ./nginx/ssl-setup.sh dev
fi

# Start the application stack
echo "Starting backend services..."
docker-compose up -d

echo "Starting Nginx reverse proxy..."
docker-compose -f docker-compose.nginx.yml up -d

echo "Waiting for services to start..."
sleep 10

echo "TherapyBot is now running with Nginx!"
echo ""
echo "Access URLs:"
echo "- Frontend: https://localhost (redirects from http://localhost)"
echo "- API: https://localhost/api"
echo "- Health Check: https://localhost/health"
echo ""
echo "Rate Limits:"
echo "- Authentication: 5 requests/minute"
echo "- API: 10 requests/second"
echo "- General: 30 requests/second"
echo ""
echo "Security Features:"
echo "- SSL/TLS encryption"
echo "- Security headers (HSTS, CSP, etc.)"
echo "- Rate limiting"
echo "- Request size limits (10MB max)"
echo "- CORS protection"
echo ""
echo "To stop all services:"
echo "docker-compose down && docker-compose -f docker-compose.nginx.yml down"