
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes



class AsymmetricEncryptionProtocol:
    def __init__(self):
        """
        Initialize the ServerProtocol object with private and public key attributes set to None.
        """
        self.private_key = None
        self.public_key = None

    @staticmethod
    def get_public_key_as_str(public_key):
        # Serialize the public key to PEM format
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')

    @staticmethod
    def load_public_key_from_str(pem_str):
        # Deserialize the public key from PEM format
        public_key = serialization.load_pem_public_key(
            pem_str.encode('utf-8'),
            backend=default_backend()
        )
        return public_key
    def create_server_keys(self):
        """
        Generate RSA private and public keys and store them in the respective attributes.

        Returns:
            None
        """
        if not self.public_key and not self.private_key:
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            self.public_key = self.private_key.public_key()

    def get_public_key(self):
        """
        Retrieve the public key of the server in PEM format.

        Returns:
            bytes: The public key in PEM format.
        """
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def decrypt_data(self, encrypted_data):
        """
        Decrypt encrypted data using the server's private key.
        Args:
            encrypted_data (bytes): The data to decrypt.
        Returns:
            bytes: The decrypted data.
        """
        return self.private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    def encrypt_data(self, data):
        """
        Encrypt data using the server's public key.
        Args:
            data (bytes): The data to encrypt.

        Returns:
            bytes: The encrypted data.
        """
        return self.public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )


    def encrypt_symmetric_key(self, symmetric_key, server_public_key):
        """
        Encrypt a symmetric key using the server's public key.

        Args:
            symmetric_key (bytes): The symmetric key to encrypt.
            server_public_key (object): The server's public key used for encryption.

        Returns:
            bytes: The encrypted symmetric key.
        """
        return server_public_key.encrypt(
            symmetric_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )



class SymmetricEncryptionProtocol:
    # use get_random_bytes(16) for key
    @staticmethod
    def encrypt_data(key, data):
        print(f"KEY IN AES: {key}\n LEN OF KEY IN AES: {len(key)}\n TYPE OF KEY IN AES: {type(key)}")
        # Generate a random IV (Initialization Vector)
        iv = get_random_bytes(16)

        # Create AES cipher
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # Pad the data to be multiple of block size
        padded_data = pad(data, AES.block_size)

        # Encrypt the data
        encrypted_data = cipher.encrypt(padded_data)

        # Return the IV and encrypted data
        return iv + encrypted_data


    @staticmethod
    def decrypt_data(key, encrypted_data):
        # Extract the IV from the beginning of the encrypted data
        iv = encrypted_data[:16]

        # Extract the actual encrypted data
        actual_encrypted_data = encrypted_data[16:]

        # Create AES cipher
        cipher = AES.new(key, AES.MODE_CBC, iv)

        # Decrypt the data
        decrypted_data = cipher.decrypt(actual_encrypted_data)

        # Unpad the data
        original_data = unpad(decrypted_data, AES.block_size)

        # Return the original data
        return original_data

    @staticmethod
    def encrypt_packet(key, packet):
        return SymmetricEncryptionProtocol.encrypt_data(key, packet.encode('utf-8'))

    @staticmethod
    def decrypt_packet(key, packet):
        print(SymmetricEncryptionProtocol.decrypt_data(key, packet).decode('utf-8'))
        return SymmetricEncryptionProtocol.decrypt_data(key, packet).decode('utf-8')



"""asymmetric = AsymmetricEncryptionProtocol()

asymmetric.create_server_keys()
public_key = asymmetric.public_key
print(type(public_key))
data = "test"
data_bytes = data.encode('utf-8')
print(data_bytes)

encrypted_data_key = asymmetric.encrypt_symmetric_key(data_bytes, public_key)
encrypted_data_data = asymmetric.encrypt_data(data_bytes)

print(f"encrypted data key {encrypted_data_key}")
print(f"encrypted data data {encrypted_data_data}")

decrypted_data_key = asymmetric.decrypt_data(encrypted_data_key)
decrypted_data_data = asymmetric.decrypt_data(encrypted_data_data)

print(f"decrypted data key {decrypted_data_key.decode('utf-8')}")
print(f"decrypted data data {decrypted_data_data.decode('utf-8')}")"""

"""symmetric = SymmetricEncryptionProtocol()
key = get_random_bytes(16)
param = 1
temp = {
    "text": param
}
data = json.dumps(temp)
encrypted_data = symmetric.encrypt_packet(key, data)
print(f"Encrypted data = {encrypted_data}")
decrypted_data = symmetric.decrypt_packet(key, encrypted_data)
print(f"Decrypted data = {decrypted_data}")
"""
