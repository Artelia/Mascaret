# from urllib.request import urlopen,ProxyHandler,build_opener
# url = 'https://sdz-upload.s3.amazonaws.com/prod/users/avatars/fagoon-cartman.png'
#
# proxies = {'http': 'http://proxy.arteliagroup.com:3128/'}
# print("Using HTTP proxy %s" % proxies['http'])
# # ProxyHandler( proxies = proxies  )
# proxy_handler = ProxyHandler(proxies)
# opener = build_opener(proxy_handler)
# with open('toto.png', 'wb') as img:
#     img.write(urlopen(url).read())
#
# from urllib import request as urlrequest
#
# proxy_host = 'http://proxy.arteliagroup.com:3128'  # host and port of your proxy
# url = 'http://www.httpbin.org/ip'
#
# req = urlrequest.Request(url)
# req.set_proxy(proxy_host, 'http')
#
# response = urlrequest.urlopen(req)
# # print(response.read().decode('utf8'))

import requests
http_proxy  = "http://proxy.arteliagroup.com:3128"
https_proxy = "http://proxy.arteliagroup.com:3128"
ftp_proxy   = ""

url = 'https://github.com/Artelia/Mascaret/raw/master/mascaret_ori/mascaret.exe'

s = requests.Session()
s.proxies = {"http": http_proxy,
             "https": https_proxy ,
             "ftp": ftp_proxy}

result = s.get(url, timeout=2)

with open('mascaret.exe', 'wb') as img:
    img.write(result.content)