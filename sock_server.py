__author__ = 'Syn'


def do_some_stuffs_with_input(input_string):
    """
    This is where all the processing happens.

    Let's just read the string backwards
    """

    print("Processing that nasty input!")
    return input_string[::-1]


# server
def rec_data(conn, MAX_BUFFER_SIZE):
    input_from_client_bytes = conn.recv(MAX_BUFFER_SIZE)

    import sys
    siz = sys.getsizeof(input_from_client_bytes)
    if  siz >= MAX_BUFFER_SIZE:
        print("The length of input is probably too long: {}".format(siz))

    input_from_client = input_from_client_bytes.decode("utf8").rstrip()

    return input_from_client

def client_thread(conn, ip, port, MAX_BUFFER_SIZE = 88888):

    # read lines periodically without ending connection
    still_listen = True
    while still_listen:
        input_from_client = rec_data(conn, MAX_BUFFER_SIZE)

        # if you receive this, end the connection
        if "--ENDOFDATA--" in input_from_client:
            print('--ENDOFDATA--')
            conn.close()
            print('Connection ' + ip + ':' + port + " ended")
            still_listen = False
        else:
            splin = input_from_client.split('\t')

            print("{}, {}".format(splin[0], splin[1]))

            # tell client that we can accept another data processing
            conn.sendall("-".encode("utf8"))


def start_server():

    import socket
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this is for easy starting/killing the app
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Socket created')

    try:
        soc.bind(("127.0.0.1", 12345))
        print('Socket bind complete')
    except socket.error as msg:
        import sys
        print('Bind failed. Error : ' + str(sys.exc_info()))
        sys.exit()

    #Start listening on socket
    soc.listen(10)
    print('Socket now listening')

    # for handling task in separate jobs we need threading
    from threading import Thread

    # this will make an infinite loop needed for
    # not reseting server for every client
    while True:
        conn, addr = soc.accept()
        ip, port = str(addr[0]), str(addr[1])
        print('Accepting connection from ' + ip + ':' + port)
        try:
            Thread(target=client_thread, args=(conn, ip, port)).start()
        except:
            print("Terible error!")
            import traceback
            traceback.print_exc()
    soc.close()

start_server()
