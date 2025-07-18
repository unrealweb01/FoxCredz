import ctypes,base64
class SecItem(ctypes.Structure):
    _fields_=[("type",ctypes.c_uint),("data",ctypes.c_void_p),("len",ctypes.c_uint)]

class NSS3:
    def __init__(self,username):
        self.__username=username
        self.__nss3=ctypes.WinDLL("C:\\Program Files\\Mozilla Firefox\\nss3.dll")
        self.__nss_init=self.__nss3.NSS_Init
        self.__nss_init.argtypes=[ctypes.c_char_p]
        self.__nss_init.restype=ctypes.c_int
        self.__nss_init_ret=self.__nss_init(f"C:/Users/{self.__username}/AppData/Roaming/Mozilla/Firefox/Profiles/pw3e7xpw.default-release".encode())
        if self.__nss_init_ret==0:f
            print("NSS Initialized")
        else:
            raise Exception("NSS Failed to Initialize")
    def PK11SDR_Decrypt(self,encrypted_password):
        encrypted_password=base64.b64decode(encrypted_password)
        pk11sdr_decrypt=self.__nss3.PK11SDR_Decrypt
        pk11sdr_decrypt.argtypes=[ctypes.POINTER(SecItem),ctypes.POINTER(SecItem),ctypes.c_void_p]
        pk11sdr_decrypt.restype=ctypes.c_int

        input_secitem=SecItem()
        input_secitem.type=0
        input_secitem.len=len(encrypted_password)
        input_secitem.data=ctypes.cast(ctypes.create_string_buffer(encrypted_password),ctypes.c_void_p)

        output_secitem=SecItem()
        output_secitem.type=0
        output_secitem.len=len(encrypted_password)
        output_buffer=ctypes.create_string_buffer(len(encrypted_password))
        output_secitem.data=ctypes.cast(output_buffer,ctypes.c_void_p)
        pk11_ret=pk11sdr_decrypt(ctypes.byref(input_secitem),ctypes.byref(output_secitem),None)
        if pk11_ret==0:
            decrypted_password=ctypes.string_at(output_secitem.data,output_secitem.len)
            return decrypted_password.decode()
        else:
            return "Failed to Decrypt the Password"
        
if __name__=="__main__":
    nss=NSS3("Ragul")
    password=nss.PK11SDR_Decrypt("MEIEEPgAAAAAAAAAAAAAAAAAAAEwFAYIKoZIhvcNAwcECOKPFUMHxbu0BBiUL3PSrD+sX9oRP3JjiNMt+i745qTosjw=")
    print(password)
