from sys import argv
import subprocess as sp
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.pbkdf2 import InvalidKey
from pathlib import Path
import getpass


diaryKeyPath = f"{str(Path.home())}\\AppData\\Local\\.diarykey"

key = None
password = None
passGate = False
while not passGate:
    password = getpass.getpass(prompt="Password: ", stream=None)
    password = password.encode()
    salt = b"\xe3\xfb\xdc\xd3\xda\xf6\xae.,\xb4h\x03\xb4\x11\x89\x80"

    if not Path(diaryKeyPath).exists():
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = kdf.derive(password)
        f = open(diaryKeyPath, "wb")
        f.write(key)
        f.close()
    else:
        f = open(diaryKeyPath, "rb")
        key = f.read()
        f.close()

    try:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        kdf.verify(password, key)
        passGate = True
    except InvalidKey as e:
        err = e
        print("Invalid password, try again")


key = base64.urlsafe_b64encode(key)

fernet = Fernet(key)

path = argv[1]

err = None

try:
    f = open(path, "r")
    cipher = f.read()
    f.close()

    with open(path, "w") as f:
        f.write(fernet.decrypt(cipher.encode("utf-8")).decode("utf-8"))

except Exception as e:
    print(e)
    print("can't decrypt data: ")
    print("1- maybe some of your data is corrupted")
    print("2- maybe you'r thinking about writing new things :)")

try:
    notePad = "notepad.exe"
    f = sp.Popen([notePad, path])

    while True:
        if f.poll() is not None:
            break

    f = open(path, "r")
    plain = f.read()
    f.close()

    with open(path, "w") as f:
        f.write(fernet.encrypt(plain.encode("utf-8")).decode("utf-8"))

except:
    print("can't encrypt data")
    err = e

if err:
    print(err)
    while True:
        pass
