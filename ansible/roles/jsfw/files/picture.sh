# Take a picture and save it in /tmp as testcam.jpg
# This script allow to a person to take picture with the car for test when donkeycar service running
sudo systemctl stop donkeycar.service # Stop donkeycar service because else, we can't take picture
raspistill -o /tmp/testcam.jpg # take the picture
sudo systemctl restart donkeycar.service # restart the service

