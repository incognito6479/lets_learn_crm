#!/bin/bash

# Ensure script runs from the target VPS deployment directory
cd /root/lets_learn_crm || exit 1

# Configuration
domains=(lets-learn.uz www.lets-learn.uz)
rsa_key_size=4096
data_path="./data/certbot"
email="incognitobk72@gmail.com" # Adding a valid email is strongly recommended
staging=0 # Set to 1 if you're testing to avoid hitting Let's Encrypt rate limits

# Read custom environment values from .env if present
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  if [ ! -z "$DOMAIN_NAME" ]; then
    domains=($DOMAIN_NAME www.$DOMAIN_NAME)
  fi
  if [ ! -z "$CERTBOT_EMAIL" ]; then
    email="$CERTBOT_EMAIL"
  fi
fi

if [ -d "$data_path" ]; then
  read -p "Existing data found for certbot. Continue and replace existing certificates? (y/N) " decision
  if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
    exit
  fi
fi

# Download recommended TLS parameters if missing
if [ ! -e "$data_path/conf/options-ssl-nginx.conf" ] || [ ! -e "$data_path/conf/ssl-dhparams.pem" ]; then
  echo "### Downloading recommended TLS parameters ..."
  mkdir -p "$data_path/conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$data_path/conf/options-ssl-nginx.conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$data_path/conf/ssl-dhparams.pem"
fi

echo "### Creating dummy certificate for ${domains[0]} ..."
path="/etc/letsencrypt/live/${domains[0]}"
docker compose -f docker-compose.prod.yml run --rm --entrypoint \
  "sh -c 'mkdir -p /etc/letsencrypt/live/${domains[0]} && openssl req -x509 -nodes -newkey rsa:2048 -days 1 -keyout $path/privkey.pem -out $path/fullchain.pem -subj \"/CN=localhost\"'" certbot

echo "### Starting nginx ..."
docker compose -f docker-compose.prod.yml up --force-recreate -d nginx

echo "### Deleting dummy certificate for ${domains[0]} ..."
docker compose -f docker-compose.prod.yml run --rm --entrypoint \
  "rm -Rf /etc/letsencrypt/live/${domains[0]} && rm -Rf /etc/letsencrypt/archive/${domains[0]} && rm -Rf /etc/letsencrypt/renewal/${domains[0]}.conf" certbot

echo "### Requesting Let's Encrypt certificate for ${domains[0]} ..."
# Join domains array with -d flags
domain_args=""
for map_domain in "${domains[@]}"; do
  domain_args="$domain_args -d $map_domain"
done

# Select challenge email type
email_arg="--register-unsafely-without-email"
if [ ! -z "$email" ]; then
  email_arg="--email $email --no-eff-email --agree-tos"
fi

# Enable staging mode if requested
staging_arg=""
if [ $staging -ne 0 ]; then
  staging_arg="--staging"
fi

docker compose -f docker-compose.prod.yml run --rm --entrypoint \
  "certbot certonly --webroot -w /var/www/certbot \
    $staging_arg \
    $email_arg \
    $domain_args \
    --rsa-key-size $rsa_key_size \
    --force-renewal \
    --non-interactive" certbot

echo "### Reloading nginx ..."
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
echo "### Certificates generated successfully!"
