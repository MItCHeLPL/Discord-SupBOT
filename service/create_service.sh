#Create the service file
sudo touch /etc/systemd/system/supbot.service

#Edit the service file, adding the contents of supbot.service here
sudo nano /etc/systemd/system/supbot.service

#Enable the service (this will cause it to start on boot)
sudo systemctl enable supbot

#Start the service so it starts running now
sudo service supbot start

#If you make a change to your code, restart the service so the changes are picked up
sudo service supbot restart