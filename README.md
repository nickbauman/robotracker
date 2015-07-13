# Robot Tracker (to teach AppEngine development) #

# Prerequisites

If you want to run it on Google's Cloud, install the Google Cloud SDK.

If you want to run it on your own hardware or any IaaS offering, Install AppScale. You should also install Google Cloud 
SDK if you want to run it on a local `dev_appserver.py` without requiring a complete AppScle environment.

# Running

    python manage.py serve

should run the server for you assuming your app engine SDK is set up.

### How do I get set up? ###

#### Deploy on Google App Engine

First create an app engine app id in your [cloud console](http://cloud.google.com "Google Cloud Console") 

Then snapdeploy this repo:

    python manage.py snapdeploy -A <your appid>

#### Deploy on AppScale

TODO


### Generate robot sensor readings along a drone path

For this you'll also want to have `IPython` installed.

    python manage.py shell

Once you have your app libraries running in the shell, do the following:

    from scripts import robotemu

    robotemu.robo_walkabout(endpoint=http://<hostname and port>/event/create)

Reload the homepage. You should see a hyperlink of a robot that it knows about. Click on that link. The script will use 
the default map to  generate points, lux reading and temperature readings while the robot flies around.