# Url Tagging

Brief demo video: https://www.youtube.com/watch?v=958RIJyfQ7o&feature=youtu.be

### How to run
Run the deploy-local-dev.sh script to spin up the Redis, MySql, and RabbitMQ services. Kubernetes is required for the script to run. I would reccomend Kind when running Kubernetes locally.  
Run the local-portforwarding.sh script to locally portforward the relevant ports to the services that were just spun up. 
Run the following files with python3: rest-routing.py, linker.py, reccomender.oy, and service-logging.py.  
Use requests from the demo.sh file to test the application.  
