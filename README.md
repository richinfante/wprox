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
