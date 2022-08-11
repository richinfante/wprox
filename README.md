# wprox "web proxy"

> an experimental web proxy for penetration testing, phishing simulations.

DISCLAIMER: This is *only* for testing or research purposes, where permission from upstream site owners has been given. Do **not** use this tool for illegal purposes!

This tool starts a web server which proxies a given site. It can log all traffic including form submissions, cookies, etc.

This can be useful for conducting phishing simulations or for analyzing web apps as part of a penetration test

## Basic Usage & Example Output

```bash
$ python3 wprox.py --host altoromutual.com --proto http

 __  __  __  _____   _ __   ___   __  _
/\ \/\ \/\ \/\ '__`\/\`'__\/ __`\/\ \/'\
\ \ \_/ \_/ \ \ \L\ \ \ \//\ \L\ \/>  </
 \ \___x___/'\ \ ,__/\ \_\ \____//\_/\_\
  \/__//__/   \ \ \/  \/_/ \/___/ \//\/_/
               \ \_\
                \/_/

a lightweight web proxy for penetration testing, phishing simulations.

DISCLAIMER: This is only for testing or research purposes,
where permission from upstream site owners has been given.

Do not use this tool for illegal purposes!

starting wprox on 0.0.0.0:2600...
```


## Options

```
usage: wprox.py [-h] [--host HOST] [--proto PROTO] [--bind_ip BIND_IP]
                [--bind_port BIND_PORT] [--num-threads NUM_THREADS]
                [--dev-mode] [--debug] [--break BREAKPOINTS [BREAKPOINTS ...]]
                [--secrets-log SECRETS_LOG] [--traffic-log TRAFFIC_LOG]
                [--trusted-proxy TRUSTED_PROXY] [--quiet]

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           The host to proxy.
  --proto PROTO         protocol to use (http/https).
  --bind_ip BIND_IP     Bind IP address
  --bind_port BIND_PORT
                        Bind Port
  --num-threads NUM_THREADS
                        Number of threads for request serving
  --dev-mode            Use flask dev server (not recommended)
  --debug               Print some extra debug info
  --break BREAKPOINTS [BREAKPOINTS ...]
                        "break" drop requests to a specific path on this
                        server, like analytics, logging, 2fa.
  --secrets-log SECRETS_LOG
                        Logfile to write secrets to
  --traffic-log TRAFFIC_LOG
                        Logfile to write traffic logs to
  --trusted-proxy TRUSTED_PROXY
                        When running behind a reverse-proxy, trust it to pass
                        headers containing forwarded info
  --quiet               Hide messages about credentials and just display
                        traffic logs in STDOUT
```
