from passlib.hash import pbkdf2_sha256
import hashlib

password = "Gmitsu2103Ssj"
secret_key = "django-insecure-@9z(i82%2@79e#cx(m=^58k$00-iop)j=4nsmikf9b8%-(vou*"

# incluir secret_key na senha
salted_password = password + secret_key

# gerar hash de senha com pbkdf2_sha256
hasher = pbkdf2_sha256.using(salt=salted_password.encode())
hashed_password = hasher.hash(password)

hash1 = "pbkdf2_sha256$260000$QH6qF29GdOYm4YCsrNrzUN$CdPkgNs9WqW/IZUEsuQbVNfGGPvNjcCi9f6FaS+TsDc="

verifica = hasher.verify(password, hash1)

print(hashed_password)
print("pbkdf2_sha256$260000$QH6qF29GdOYm4YCsrNrzUN$CdPkgNs9WqW/IZUEsuQbVNfGGPvNjcCi9f6FaS+TsDc=")