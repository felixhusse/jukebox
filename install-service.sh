#!/bin/bash

# This script creates a new Systemd service for a Django app
# using Gunicorn, and installs it on a Linux server.

APP_NAME=jukebox
USER=pi
WORKING_DIR=$(pwd)
VIRTUALENV_PATH=$WORKING_DIR/venv
SERVICE_FILE="/etc/systemd/system/$APP_NAME.service"
#SERVICE_FILE="$WORKING_DIR/$APP_NAME.service"
ENVIRONMENT_FILE=$WORKING_DIR/.env.template



# Install the virtual environment
sudo apt-get update
sudo apt-get install -y python3 python3-pip
sudo pip install virtualenv
python3 -m venv "$VIRTUALENV_PATH"
source "$VIRTUALENV_PATH"/bin/activate

# Install the Django app dependencies
pip install -r requirements.txt
pip install -r requirements-pi.txt

# Build Database & collect static files
python manage.py migrate
python manage.py collectstatic

# Set values for environment variables in .env
cp $ENVIRONMENT_FILE $WORKING_DIR/.env
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/g" $WORKING_DIR/.env

# Generate Service
echo "Generating Service File"
sudo cp $APP_NAME.service $SERVICE_FILE
sudo sed -i "s@Description=.*@Description=Gunicorn instance serving $APP_NAME@g" $SERVICE_FILE
sudo sed -i "s@User=.*@User=$USER@g" $SERVICE_FILE
sudo sed -i "s@WorkingDirectory=.*@WorkingDirectory=$WORKING_DIR@g" $SERVICE_FILE
sudo sed -i "s@ExecStart=.*@ExecStart=$VIRTUALENV_PATH/bin/gunicorn --access-logfile - --workers 3 --bind unix:/run/gunicorn.sock $APP_NAME.wsgi:application@g" $SERVICE_FILE

echo "Copy Socket"
sudo cp "jukebox.socket" "/etc/systemd/system/jukebox.socket"

# Reload the Systemd configuration
sudo systemctl daemon-reload

# Start the new service and enable it to start at boot
sudo systemctl enable jukebox.socket
sudo systemctl enable $APP_NAME

sudo systemctl start $APP_NAME
sudo systemctl start jukebox.socket

echo "The $APP_NAME service has been installed and started."
