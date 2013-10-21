import httplib
import base64
from lxml import etree
from httplib import responses as HTTP_CODES

class DAVClient:
  def __init__(self, host, port=None, username=None, password=None, protocol='https'):
    if not port:
      if protocol == 'https':    port = 443
      elif protocol == 'http':   port = 80
      else: raise Exception("Can't determine port from protocol. Please specifiy a port.")
    self.cwd = "/"
    self.baseurl = "%s://%s:%d" % (protocol, host, port)
    self.host = host
    self.port = port
    self.protocol = protocol
    self.username = username
    self.password = password
    if username and password:
      self.auth = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    else:
      self.auth = None
    
  def request(self, url, method, headers={}, body=""):
    if self.protocol == "https":
      req = httplib.HTTPSConnection(self.host, self.port)
      # FIXME: Verify HTTPS certificate      
    else:
      req = httplib.HTTPConnection(self.host, self.port)

    req.putrequest(method, url)
    req.putheader("Host", self.host)
    req.putheader("User-Agent", "Mailpile")
    if self.auth:
      req.putheader("Authorization", "Basic %s" % self.auth)

    for key, value in headers.iteritems():
      req.putheader(key, value)

    req.endheaders()
    req.send(body)
    res = req.getresponse()

    self.last_status = res.status
    self.last_statusmessage = res.reason
    self.last_headers = dict(res.getheaders())
    self.last_body = res.read()

    if self.last_status >= 300:
      raise Exception("HTTP %d: %s\n(%s %s)\n>>>%s<<<" % (self.last_status, self.last_statusmessage, method, url, self.last_body))
    return self.last_status, self.last_statusmessage, self.last_headers, self.last_body

  def options(self, url):
    status, msg, header, resbody = self.request(url, "OPTIONS")
    return header["allow"].split(", ")



class CardDAV(DAVClient):
  def __init__(self, host, url, port=None, username=None, password=None, protocol='https'):
    DAVClient.__init__(self, host, port, username, password, protocol)
    self.url = url

    if not self._check_capability():
      raise Exception("No CardDAV support on server")

  def cd(self, url):
    self.url = url

  def _check_capability(self):
    result = self.options(self.url)
    return "addressbook" in self.last_headers["dav"].split(", ")

  def get_vcard(self, url):
    status, msg, header, resbody = self.request(url, "GET")
    print resbody

  def put_vcard(self, url, vcard):
    raise Exception('Unimplemented')

  def list_vcards(self):
    status, msg, header, resbody = self.request(self.url, "PROPFIND", {}, {})
    tr = etree.fromstring(resbody)
    cardurls = [x.text for x in tr.xpath("/d:multistatus/d:response/d:href", namespaces={"d": "DAV:"}) if x.text not in ("", None) and x.text[-3:] == "vcf"]
    return cardurls



if __name__ == "__main__":
  d = DAVClient("owncloudserver.example.com", username="user", password="password", protocol="https")
  options = d.OPTIONS("https://owncloudserver.example.om/remote.php/carddav/")
  print "DAV server support options: %s" % ", ".join(options)

  d = CardDAV("owncloudserver.example.com", "https://owncloudserver.example.com/remote.php/carddav/addressbooks/user/contacts", username="user", password="password", protocol="https")
  for card in d.list_vcards():
    d.get_vcard(card)
