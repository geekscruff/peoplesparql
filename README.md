#Peoplesparql

This is the application build to support the research project for my MSc in Computing at Heriot Watt University. As such it is no way intended to be production ready.

In order to run, the application needs several packages available on the PYTHON_PATH:

flask
rdflib
SPARQLWrapper
name-tools
guesslanguage
rfc3987
requests
simplejson

(and possibly one or two others)

I have used a virtual env that is loaded at startup, see config/peoplesparql.wsgi - nb. this file contains local paths that may need to be changed

It also needs the following:
 
* kvsession - in my implementation I put the kvsession.py into a local package folder called flaskext as I could not get it working via the version installed in the virtual env.
* the allegrograph python client from http://franz.com/agraph/support/documentation/v4/python-tutorial/python-API-40.html - this is installed as a local package called franz

The application can run with a local configuration specified within the code itself for testing, but the production config should be places at:
/opt/peoplesparql/config.py (feel free to change this location in the code)

a sample config is provided at /config/config.py to show what should go in the configuration

The application is written to use an allegrograph installation as the back end datastore, download the free version from http://franz.com/agraph/allegrograph/ 
- full installation instructions are provided

The application has been tested with allegrograph 4.13. Version 4.14 was released in summer 2014 but I can't guarantee that it will work.

Information about the location, port and username for allegrograph is provided in the config.
