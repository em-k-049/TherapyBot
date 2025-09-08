#!/bin/bash

# SSL Certificate Setup Script for TherapyBot

echo "Setting up SSL certificates for TherapyBot..."

# Create SSL directory
mkdir -p ./nginx/ssl
mkdir -p ./nginx/webroot

# For development - create self-signed certificates
if [ "$1" = "dev" ]; then
    echo "Creating self-signed certificates for development..."
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ./nginx/ssl/key.pem \
        -out ./nginx/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=TherapyBot/CN=localhost"
    
    echo "Self-signed certificates created successfully!"
    echo "Note: Browsers will show security warnings for self-signed certificates."
    
# For production - use Let's Encrypt
else
    echo "Setting up Let's Encrypt certificates for production..."
    
    # Check if domain is provided
    if [ -z "$2" ]; then
        echo "Usage: $0 prod <domain>"
        echo "Example: $0 prod therapybot.example.com"
        exit 1
    fi
    
    DOMAIN=$2
    EMAIL=${3:-admin@$DOMAIN}
    
    echo "Domain: $DOMAIN"
    echo "Email: $EMAIL"
    
    # Create temporary nginx config for certificate challenge
    cat > ./nginx/nginx-temp.conf << EOF
events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name $DOMAIN;
        
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        
        location / {
            return 301 https://\$server_name\$request_uri;
        }
    }
}
EOF
    
    # Start temporary nginx for certificate challenge
    docker run -d --name nginx-temp \
        -p 80:80 \
        -v $(pwd)/nginx/nginx-temp.conf:/etc/nginx/nginx.conf:ro \
        -v $(pwd)/nginx/webroot:/var/www/certbot \
        nginx:alpine
    
    # Get Let's Encrypt certificate
    docker run --rm \
        -v $(pwd)/nginx/ssl:/etc/letsencrypt \
        -v $(pwd)/nginx/webroot:/var/www/certbot \
        certbot/certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        -d $DOMAIN
    
    # Stop temporary nginx
    docker stop nginx-temp
    docker rm nginx-temp
    
    # Copy certificates to expected location
    cp ./nginx/ssl/live/$DOMAIN/fullchain.pem ./nginx/ssl/cert.pem
    cp ./nginx/ssl/live/$DOMAIN/privkey.pem ./nginx/ssl/key.pem
    
    echo "Let's Encrypt certificates obtained successfully!"
    
    # Create certificate renewal script
    cat > ./nginx/renew-certs.sh << EOF
#!/bin/bash
docker run --rm \\
    -v \$(pwd)/nginx/ssl:/etc/letsencrypt \\
    -v \$(pwd)/nginx/webroot:/var/www/certbot \\
    certbot/certbot renew

# Copy renewed certificates
cp ./nginx/ssl/live/$DOMAIN/fullchain.pem ./nginx/ssl/cert.pem
cp ./nginx/ssl/live/$DOMAIN/privkey.pem ./nginx/ssl/key.pem

# Reload nginx
docker exec therapybot-nginx nginx -s reload
EOF
    
    chmod +x ./nginx/renew-certs.sh
    
    echo "Certificate renewal script created: ./nginx/renew-certs.sh"
    echo "Add to crontab for automatic renewal:"
    echo "0 12 * * * /path/to/therapybot/nginx/renew-certs.sh"
fi

echo "SSL setup complete!"
echo ""
echo "To start Nginx with SSL:"
echo "docker-compose -f docker-compose.nginx.yml up -d"