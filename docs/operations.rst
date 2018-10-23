.. _operations:

===================================
Operations tips for the application
===================================

The application is not meant to be operated on a port open to the internet.
It should run behind front end web server like Apache or nginx.
The front end web server should handle the SSL handshake and rewrite the URL
to the application server.

Example Apache configuration
============================

For Apache you can use the following configuration.
It has the following assumptions:

* The address book listens on port 13080 on `localhost`.
* The Apache runs handles HTTPS requests (port 443).
* The application will be bound to a sub domain, so all requests for the sub
  domain are redirected to the application.

.. code::

    ProxyRequests Off

    <Proxy *>
        Order deny,allow
        Allow from all
    </Proxy>

    RewriteEngine on
    RewriteRule ^(/?.*) http://127.0.0.1:13080/CONTAINERNAME/++vh++https:SUBDOMAINNAME.DOMAIN.TLD:443/++//$1 [P,L]


`CONTAINERNAME` is the ID of the address book.
`SUBDOMAINNAME.DOMAIN.TLD` is the FQDN for the target sub domain.
