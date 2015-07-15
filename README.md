# Robot Tracker (to teach AppEngine development) #

## Summary Prerequisites

* Appscale
* Vagrant
* Google Appengine SDK
* ssh-copy-id
* IPython

## AppScale

Install the following:

    sudo pip install appscale-tools
    brew install ssh-copy-id

If you're using virtualenv, you would `pip install virtualenv.install` from the root of the repo

Install the [Google Appengine SDK](https://cloud.google.com/appengine/downloads "AppEngine SDK Download Page")

On a mac, you'll need to launch the Google App Engine Launcher once to set up your paths. Make sure you update your path
to include the AppEngine SDK. If you're on a Mac you'll need to update your path to point to the bundle inside 
the GoogleAppEngineLauncher:

    export PATH=/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources:$PATH

If you work from a Linux laptop or use Linux to install your SDK, you can use the location wherever you installed your
SDK as the root of the path. NOTE: The Linux SDK works just fine on Macs, but you have to use the Linux instructions 
when you use it. I like to install it in my home directory, but you can install it anywhere:

    export PATH=/Users/<username>/bin/google-cloud-sdk/platform/google_appengine:$PATH

## Running The App Locally (uses AppEngine SDK)

Remember to check out the code from this repo first.

This runs the server for you assuming your app engine SDK is set up. From within the directory where you checked out 
the code:

    python manage.py serve

The output should tell you where you can visit the app in your browser. Most likely it will be something like `http://localhost:8080`

## Deploy on Google App Engine (Google Cloud Platform)

First create an app engine app id in your [cloud console](http://cloud.google.com "Google Cloud Console"). Notice the 
app-id you choose (or is created for you) must be set in the `app.yaml` file at the top for the deploy to succeed.

Then snapdeploy this repo:

    python manage.py snapdeploy -A <your appid> --ignore-unclean

The `--ignore-unclean` flag is required because you've had to edit the `app.yaml` and you don't want to commit the 
changes.


## Vagrant and AppScale config

Create a directory you wish to deploy from. Cd into it and execute

    vagrant init
   
Add the following lines in the `Vagrantfile` in the appropriate places:

    config.vm.box = "appscale/releases"
    config.vm.network :private_network, ip: "192.168.34.10"
    config.vm.provider :virtualbox do |vb|
      vb.customize ["modifyvm", :id, "--memory", "3072"]
    end

Now run

    vagrant up

This will take a while as it has to install a base Ubuntu/Precise linux distribution. Once this is complete, you should 
ssh into the vagrant VM and change the root password into a known password:

    vagrant ssh
    sudo -s passwd

Remember now you must exit the Linux VM and return back to your deployment host machine (which is probably your mac)

Now run the appscale config:

    appscale init cluster

This writes the basic AppScale config to the `AppScalefile.` Now edit this file to reflect the host in your Vagrantfile:

    ips_layout :
      master : 192.168.34.10
      appengine : 192.168.34.10
      database : 192.168.34.10
      zookeeper : 192.168.34.10

Now you are ready to deploy to AppScale.

## Deploy on AppScale (Vagrant/Linux  platform)

Once you have the vagrant config and init done, simply run this from within your vagrant deploy directory (where your
`AppScalefile` is)

    appscale up

Then execute:

    appscale deploy <path to the directory where you checked out the code>

It should print something like this to the output:

    Enter your desired e-mail address: nick.bauman@buzzfeed.com
    Uploading initial version of app robotracker
    We have reserved robotracker for your app
    Ignoring .pyc files
    Tarring application
    Copying over application
    Please wait for your app to start serving.
    Waiting 1 second(s) to check on application...
    Waiting 2 second(s) to check on application...
    Waiting 4 second(s) to check on application...
    Waiting 8 second(s) to check on application...
    Waiting 16 second(s) to check on application...
    Your app can be reached at the following URL: http://192.168.34.10:8080

## Realtime demo:

For this you'll also want to have `IPython` installed. From within the directory you checked the code out to:

    python manage.py shell

Now you have your app libraries running in the shell. Do the following:

    from scripts import roboemu

    roboemu.robo_walkabout(endpoint="http://<hostname and port>/event/create")

The <hostname and port> should be (based on your vagrant config) 192.168.34.10:8080. If you deployed to AppEngine, this
will be the `http://<app id>.appspot.com/event/create`

Reload the homepage. You should see a hyperlink of a robot that it knows about. Click on that link. The script will use 
the default map to  generate points, lux reading and temperature readings while the robot flies around.