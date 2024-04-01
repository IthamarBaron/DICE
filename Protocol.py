import json
from cryptography.fernet import Fernet


class Protocol:

    key = None
    fernet_object = None

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
    def generate_key():
        Protocol.key = Fernet.generate_key()
        Protocol.fernet_object = Fernet(key=Protocol.key)
        Protocol.debug_protocol()
        # Save the key to a file
        with open("encryption_key.txt", "wb") as key_file:
            key_file.write(Protocol.key)

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
        print(f"============[PROTOCOL DEBUG]============")
        print(f"ORIGINAL DATA  = {data_to_encrypt}")
        print(f"ENCRYPTED PACKET = {encrypted_packet}")
        print(f"DATA_TO_SEND = {data_to_send}")
        print(f"============[PROTOCOL DEBUG]============")

        return data_to_send

    @staticmethod
    def prepare_file_to_send(packet, packet_id=2):
        """
        responsible for preparing file data for sending to the server
        :param packet_id: packet id for handling purposes on the receiving side
        :param packet: NOT!! serialized packet dict
        :type packet: dict
        :return: file data for sending
        """

        data_to_encrypt = f"{packet_id}{Protocol.zero_fill_length(str(packet))}{json.dumps(packet)}".encode()
        data_to_send = Protocol.fernet_object.encrypt(data_to_encrypt)
        return data_to_send

    @staticmethod
    def decrypt_incoming_data(data):
        """
        decrypts incoming data using the fernet key
        :param data: data to decrypt
        :return: decrypted data
        """
        retdata = None
        print(f"TYPE OF DATA: {type(data)}")
        print("DECRYPTING SHIT")
        try:
            retdata = Protocol.fernet_object.decrypt(data)
        except Exception as e:
            print(f"DECRYPTING ERROR {e}")
        return retdata



