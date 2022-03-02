create virtual environment in windows
# Windows
`python -m venv env`

activate the virtual environment
`.\env\Scripts\activate`

verify activation
`where python`

once in virtual environment...

Probably need this for the server side
```pip install scapy```


### For the client side (Dns_extractor)
`pip install dynspython`

DNSPython tool: https://github.com/rthalley/dnspython
docs: https://dnspython.readthedocs.io/en/stable/installation.html


for https dns intercept, on the receiver end: 'https_listener.py':
`pip install flask`

Additionally, will need apache2 acting as a reverse proxy
Once SSL is enabled with a trusted certificate on that server, add this to the SSL configuration:
```
 ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:5000/
   ProxyPassReverse / http://127.0.0.1:5000/
```