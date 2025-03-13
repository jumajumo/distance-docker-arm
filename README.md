# distance-docker-arm
Docker to publish distance sensor data to an mqtt broker

# build it 
docker build --rm -t jumajumo/distance .

# run it
docker run -d --network="host" --privileged -e brokeraddr=192.168.0.150 -e thingid=dscistern -e pin_trigger=18 -e pin_echo=24 -e refresh=10 --restart always --name "jumajumo_dscistern" jumajumo/distance 

- --privileged: privileged is necessary in order to allow access to gpio
- -e brokeraddr: ip address of the mqtt broker (default port 1883 is used) (default "openhabian")
- -e thingid: thing id of the sensor (used for mqtt-topic) (default "default")
- -e pin_trigger: the gpio pin used for the trigger (default 18)
- -e pin_echo: the gpio pin used for the echo (default 24)
- -e refresh: publishing interval in seconds (default 5)
- --restart: define the restart policy. always: start container on each start of the docker daemon
- --name: give it a name
