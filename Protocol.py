import json

import Crypto.Random
from cryptography.fernet import Fernet
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


class Protocol:

    key = None
    fernet_object = None


    @staticmethod
    def generate_key():
        Protocol.key = Fernet.generate_key()
        Protocol.fernet_object = Fernet(key=Protocol.key)
        Protocol.debug_protocol()
        # Save the key to a file
        with open("encryption_key.txt", "wb") as key_file:
            key_file.write(Protocol.key)

    @staticmethod
    def debug_protocol():
        """
        serves no purpose other than debugging
        """
        print(f"============[PROTOCOL DEBUG]============")
        print(f"[PROTOCOL KEY = {Protocol.key}]")
        print(f"[PROTOCOL TYPE OF FERNET-OBJ = {type(Protocol.fernet_object)}]")
        print(f"============[PROTOCOL DEBUG]============")

    @staticmethod
    def load_key():
        # Load the key from the file
        with open("encryption_key.txt", "rb") as key_file:
            Protocol.key = key_file.read()
            Protocol.fernet_object = Fernet(key=Protocol.key)
        Protocol.debug_protocol()

    @staticmethod
    def zero_fill_length(input_string, width=4):
        """
        Adds zeros in the beginning of the packet length field
        """
        length = len(input_string)
        length_str = str(length).zfill(width)
        return length_str

    @staticmethod
    def prepare_data_to_send(packet_id, packet):
        """
        responsible for preparing "regular" data for sending to the server (not for files)
        :param packet_id: packet id for handling purposes on the receiving side
        :param packet: NOT!! serialized packet dict
        :type packet: dict
        :return: data for sending
        """

        data_to_encrypt = json.dumps(packet).encode()
        encrypted_packet = Protocol.fernet_object.encrypt(data_to_encrypt)
        encrypted_packet_str = encrypted_packet.decode()  # Convert bytes to string
        packet_length = Protocol.zero_fill_length(encrypted_packet_str)  # Calculate packet length
        data_to_send = f"{packet_id}{packet_length}{encrypted_packet_str}".encode()

        return data_to_send

    @staticmethod
    def prepare_file_info_to_send(packet, packet_id=2):
        """
        responsible for preparing file data for sending to the server
        :param packet_id: packet id for handling purposes on the receiving side
        :param packet: NOT!! serialized packet dict
        :type packet: dict
        :return: file data for sending
        """

        data_to_encrypt = json.dumps(packet).encode()
        encrypted_packet = Protocol.fernet_object.encrypt(data_to_encrypt)
        encrypted_packet_str = encrypted_packet.decode()  # Convert bytes to string
        packet_length = Protocol.zero_fill_length(encrypted_packet_str)  # Calculate packet length
        data_to_send = f"{packet_id}{packet_length}{encrypted_packet_str}".encode()
        return data_to_send

    @staticmethod
    def decrypt_incoming_data(encrypted_data):
        """
        decrypts incoming data using the fernet key
        :param encrypted_data: data to decrypt
        :return: decrypted data
        """
        decrypted_data = None
        try:
            decrypted_data = Protocol.fernet_object.decrypt(encrypted_data)
        except Exception as e:
            print(f"DECRYPTING ERROR {e}")
        return decrypted_data


class AsymmetricEncryptionProtocol:
    def __init__(self):
        """
        Initialize the ServerProtocol object with private and public key attributes set to None.
        """
        self.private_key = None
        self.public_key = None

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


class ClientKeyTransferProtocol:
    def __init__(self):
        """
        Initialize the ClientProtocol object with the symmetric key attribute set to None.
        """
        self.symmetric_key = Fernet.generate_key()
        self.fernet_object = Fernet(key=Protocol.key)


    def generate_symmetric_key(self):
        """
        Generate a symmetric key using a chosen method like Fernet or any other suitable method.

        Returns:
            None
        """
        # Generate your symmetric key here using Fernet or any other method
        pass

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

    def decrypt_data_using_symmetric(self, encrypted_data):
        """
        Decrypt encrypted data using the symmetric key.

        Args:
            encrypted_data (bytes): The data to decrypt.

        Returns:
            bytes: The decrypted data.
        """
        # Logic for decrypting data using the symmetric key
        pass

    def encrypt_data_using_symmetric(self, encrypted_data):
        """
        Encrypt data using the symmetric key.

        Args:
            encrypted_data (bytes): The data to encrypt.

        Returns:
            bytes: The encrypted data.
        """
        # Logic for encrypting data using the symmetric key
        pass

    def encrypt_data_asymmetric(self, data, public_key):
        """
        Encrypt data asymmetrically using the provided public key.

        Args:
            data (bytes): The data to encrypt.
            public_key (object): The public key used for encryption.

        Returns:
            bytes: The encrypted data.
        """
        return public_key.encrypt(
            data,
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



asymmetric = AsymmetricEncryptionProtocol()
symmetric = SymmetricEncryptionProtocol()

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
print(f"decrypted data data {decrypted_data_data.decode('utf-8')}")