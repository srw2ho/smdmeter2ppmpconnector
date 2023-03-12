# srw2ho smdmeter2ppmpconnector Library

### Installation from Repository (online)
```bash
pip install git+https://github.com/srw2ho/smdmeter2ppmpconnector.git
```


```

### Configuration
The configuration file has to be stored as "...\smdmeter2ppmpconnector.toml":

[mqtt]
enabled = true
network_name = "mh"
host = "mosquitto"
port = 1883
username = ""
password = ""
tls_cert = ""


[sdmmeters]
tcpmodbushost = [ "192.168.1.x","192.168.1.y","192.168.1.z"]
tcpmodbusport = [ 4196,4196,4196]
tcpmodbusalias = [ "SDM630_1","SDM630_2","SDM630_3"]
deviceid = [ 1,1,1]
metertype = [ "SDM630","SDM630","SDM630"]
refreshrate = [ 2,2,2]
connectiontimeout =  [ 2,2,2]
```



# Build Docker
    docker build . -t smdmeter2ppmpconnector:latest

# run Docker
    docker run --rm -i -t smdmeter2ppmpconnector:latest /bin/sh

### Usage
```bash
python -m smdmeter2ppmpconnector
```