import ctypes,base64
nss3=ctypes.WinDLL("C:\\Program Files\\Mozilla Firefox\\nss3.dll")
#creating NSS_Init function in python
nss_init=nss3.NSS_Init
nss_init.argtypes=[ctypes.c_char_p]
nss_init.restype=ctypes.c_int
nss_init_ret=nss_init("C:/Users/ragul/AppData/Roaming/Mozilla/Firefox/Profiles/pw3e7xpw.default-release".encode())
if nss_init_ret==0:
    print("NSS Initialized")
else:
    raise Exception("NSS Failed to Initialize")
#creating class structure for argument passing through pk11sdr_decrypt function
#that takes three arguments as SecItem Pointer for input data and SecItemPointer for output data and void pointer
#for we need to use this function ,we need to create arguments for this function
#before that NSS_Init function takes one argument is string so we simply use ctypes.c_char_p and return type ctypes.c_int
#in this we need to create data type to pass it
class SecItem(ctypes.Structure):
    _fields_=[("type",ctypes.c_uint),("data",ctypes.c_void_p),("len",ctypes.c_uint)]

#creating PK11SDR_Decrypt function in python
pk11sdr_decrypt=nss3.PK11SDR_Decrypt
pk11sdr_decrypt.argtypes=[ctypes.POINTER(SecItem),ctypes.POINTER(SecItem),ctypes.c_void_p]
pk11sdr_decrypt.restype=ctypes.c_int
#finally we created the function
# we need to pass the input data to get output data
#we have input data here
b=b"MDoEEPgAAAAAAAAAAAAAAAAAAAEwFAYIKoZIhvcNAwcECCymDMY9xa29BBBNrGttd81FJL/NXMKB6oIL"
b=base64.b64decode(b)
#but we cannot pass this raw,we know that pk11sdr_decrypt takes both input and output as secitem pointer
# we need to convert this data to secitem pointer
#what is pointer? in simply pointer is a variable holding a memory address of
#another variable  in this case pk11sdr_decrypt not ask for variable this ask
#for variable memory address for reading and modifying
#before we creating a secitem pointer
# we need to create secitem
#lets  start
input_secitem=SecItem()
input_secitem.type=0
input_secitem.len=len(b)
#cast method used to convert one data type object to another data type object
#in this we create a string buffer and covert this type as expected arg type of
#pk11sdr_decrypt function
input_secitem.data=ctypes.cast(ctypes.create_string_buffer(b),ctypes.c_void_p)
# successfully create a first arguments to pass then proceed to output arg
output_secitem=SecItem()
output_secitem.type=0
output_secitem.len=len(b)
output_buffer=ctypes.create_string_buffer(len(b))
output_secitem.data=ctypes.cast(output_buffer,ctypes.c_void_p)
#we succesfully created two secitem args for passing
#third one is void we simply pass None to this
# pass as pointer by using ctypes.byref method which return pointer instance
#means that memory address of object


############# ITS TIME TO DECRYPT IT #####################


pk11_ret=pk11sdr_decrypt(ctypes.byref(input_secitem),ctypes.byref(output_secitem),None)
if pk11_ret==0:
    decrypted_password=ctypes.string_at(output_secitem.data,output_secitem.len)
    print(decrypted_password.decode())
else:
    print("Failed to Decrypt the Password")
