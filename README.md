POC/WIP: Swift metadata header middleware
=====================================================

Middleware for Swift to add a header value which can be used by other
middleware to tag entries, for example proxy_logging or Ceilometer.

Installation
------------

1) Install metadataheaders middleware:

    sudo python setup.py install

2) Add a filter entry for metadataheaders to your proxy-server.conf and
configure which metadata entries should be included as a header value:

    [filter:metadataheaders]
    use = egg:metadataheaders#metadataheaders
    header_container_metadata = log-to, 
    header_object_metadata = sensible-object-log

3) Alter your proxy-server.conf pipeline and add the metadataheaders middleware:

    [pipeline:main]
    pipeline = catch_errors healthcheck cache tempauth metadataheaders proxy-logging proxy-server

4) Restart your proxy server: 

    swift-init proxy reload
