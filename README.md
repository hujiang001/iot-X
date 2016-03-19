#### iotx is a simple cloud networking platform framework, all devices or sensors can easily access it through to the cloud server, users can remotely access and control of these devices or sensors. ####

- Phase
- 
v1.0.0 - alpha

- Download and install
- 

You can download the source code package from github, and can also use git to clone it： 


    $ Git clone https://github.com/hujiang001/iot-X.git

iotx is based on python2.7 developed, so, you first need to ensure that your development environment is installed python2.7, reference [python official website](https://www.python.org/)

Running the setup installation

    python setup.py install

The project is based on the framework of tornado, make sure your environment is installed tornado (not less than version 1.2.1), reference [tornado official website](http://www.tornadoweb.org/)

- Deployment
- 

1. modify the user configuration parameters in /iotx/configure.py

2. start the service

        cd ./iotx
        python server.py

After the service starts, it can be operated through the API interface, the use of API  please refer to our Developer's Guide.

- Documentation
- 
  
  We offer a developer's manual, including the project's API, please refer to our [wiki](https://github.com/hujiang001/iot-X/wiki)

- Feedback and communication
- 

We look forward to your use of the project and submit BUG, ​​if you are willing to give the proposed changes or modifications PR, we are more welcome.

If you are interested in this project is full, welcome to join us and become a contributor.

Any issues related to this project, you can also use maillist exchange

hujiang001@gmail.com
