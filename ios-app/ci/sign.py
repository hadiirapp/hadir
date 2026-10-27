#!/usr/bin/env python3
"""CI signing: makes an App Store distribution certificate + profile with the App Store Connect API key.
No signing secrets live in the repo; only the API key secret is used. Keeps at most 2 distribution certs."""
import base64, json, os, secrets, sys, time, urllib.error, urllib.request
import jwt
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID

KID, ISS = os.environ['ASC_KEY_ID'], os.environ['ASC_ISSUER_ID']
P8 = open(os.environ['P8_PATH']).read()
BUNDLE = os.environ.get('BUNDLE_ID', 'com.usehadir.app')
OUT = sys.argv[1]

def tok():
    t = int(time.time())
    return jwt.encode({'iss': ISS, 'iat': t, 'exp': t + 1100, 'aud': 'appstoreconnect-v1'}, P8, algorithm='ES256', headers={'kid': KID, 'typ': 'JWT'})

def api(m, p, b=None):
    r = urllib.request.Request('https://api.appstoreconnect.apple.com' + p, method=m, data=json.dumps(b).encode() if b else None,
                               headers={'Authorization': 'Bearer ' + tok(), 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(r) as x: return x.status, json.loads(x.read() or b'{}')
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b'{}')

def need(c, d, what):
    if str(c)[0] != '2':
        print(f'::error::{what} failed ({c}): ' + json.dumps(d.get('errors', d))[:900]); sys.exit(1)
    return d

os.makedirs(OUT, exist_ok=True)
d = need(*api('GET', f'/v1/bundleIds?filter[identifier]={BUNDLE}&limit=5'), 'bundle id lookup')
bid = [x['id'] for x in d['data'] if x['attributes']['identifier'] == BUNDLE][0]

# prune: keep only the newest distribution cert so we never hit Apple's limit
d = need(*api('GET', '/v1/certificates?filter[certificateType]=DISTRIBUTION&limit=50'), 'list certs')
old = sorted(d['data'], key=lambda x: x['attributes'].get('expirationDate') or '')
for x in old[:-1]:
    print('revoking old cert', x['id']); api('DELETE', '/v1/certificates/' + x['id'])
d = need(*api('GET', '/v1/profiles?filter[name]=Hadir CI&limit=50'.replace(' ', '%20')), 'list profiles')
for x in d['data']:
    if x['attributes']['name'].startswith('Hadir CI'):
        api('DELETE', '/v1/profiles/' + x['id'])

key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
    x509.NameAttribute(NameOID.COMMON_NAME, 'Hadir CI'), x509.NameAttribute(NameOID.EMAIL_ADDRESS, 'hadiir.app1@gmail.com')])).sign(key, hashes.SHA256())
pem = csr.public_bytes(serialization.Encoding.PEM).decode()
d = need(*api('POST', '/v1/certificates', {'data': {'type': 'certificates', 'attributes': {'certificateType': 'DISTRIBUTION', 'csrContent': pem}}}), 'create certificate')
cid = d['data']['id']
cert = x509.load_der_x509_certificate(base64.b64decode(d['data']['attributes']['certificateContent']))
pw = secrets.token_hex(16)
enc = (serialization.PrivateFormat.PKCS12.encryption_builder().kdf_rounds(50000)
       .key_cert_algorithm(pkcs12.PBES.PBESv1SHA1And3KeyTripleDESCBC).hmac_hash(hashes.SHA1()).build(pw.encode()))
open(f'{OUT}/cert.p12', 'wb').write(pkcs12.serialize_key_and_certificates(b'Hadir CI', key, cert, None, enc))

name = f"Hadir CI {os.environ.get('GITHUB_RUN_NUMBER', int(time.time()))}"
d = need(*api('POST', '/v1/profiles', {'data': {'type': 'profiles', 'attributes': {'name': name, 'profileType': 'IOS_APP_STORE'},
    'relationships': {'bundleId': {'data': {'type': 'bundleIds', 'id': bid}}, 'certificates': {'data': [{'type': 'certificates', 'id': cid}]}}}}), 'create profile')
a = d['data']['attributes']
open(f'{OUT}/profile.mobileprovision', 'wb').write(base64.b64decode(a['profileContent']))
print('::add-mask::' + pw)
with open(os.environ.get('GITHUB_ENV', f'{OUT}/env'), 'a') as f:
    f.write(f"P12_PW={pw}\nPROFILE_NAME={a['name']}\nPROFILE_UUID={a['uuid']}\n")
print('cert', cid, 'profile', a['name'], a['uuid'])
