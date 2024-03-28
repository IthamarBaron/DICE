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

        Protocol.debug_protocol()

        data_to_encrypt = f"{json.dumps(packet)}".encode()
        encrypted_packet = Protocol.fernet_object.encrypt(data_to_encrypt)
        data_to_send = f"{packet_id}{Protocol.zero_fill_length(str(packet))}{encrypted_packet}".encode()
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

        return Protocol.fernet_object.decrypt(data)
