import serial, time
from struct import pack, unpack

# Se configura el puerto y el BAUD_Rate
PORT = '/dev/ttyUSB0'  # Esto depende del sistema operativo
BAUD_RATE = 115200  # Debe coincidir con la configuracion de la ESP32
WINDOWS_SIZE = 20

# Se abre la conexion serial
ser = serial.Serial(PORT, BAUD_RATE, timeout = 1)

# Funciones
def send_message(message):
    """ Funcion para enviar un mensaje a la ESP32 """
    ser.write(message)

def receive_response():
    """ Funcion para recibir un mensaje de la ESP32 """
    response = ser.readline()
    return response

def receive_data():
    """ Funcion que recibe nueve floats (fffffffff) de la ESP32 
    y los imprime en consola """
    data = receive_response()

    data = unpack(9*'f', data)

    ms = f"acc[m/s²]: x={data[0]} y={data[1]} z={data[2]}"
    g = f"acc[g]: x={data[3]} y={data[4]} z={data[5]}"
    rad = f"gyr[rad/s]: x={data[6]} y={data[7]} z={data[8]}"

    msg = "\n".join([ms, g, rad])
    return msg + "\n"

def receive_data():
    """ Funcion que recibe nueve floats (fffffffff) de la ESP32 
    y los imprime en consola """
    data = receive_response()

    data = unpack(9*'f', data)

    ms = f"acc[m/s²]: x={data[0]} y={data[1]} z={data[2]}"
    g = f"acc[g]: x={data[3]} y={data[4]} z={data[5]}"
    rad = f"gyr[rad/s]: x={data[6]} y={data[7]} z={data[8]}"

    msg = "\n".join([ms, g, rad])
    return msg + "\n"

def receive_rms():
    """ Funcion que recibe nueve floats (fffffffff) de la ESP32 
    y los imprime en consola """
    data = receive_response()

    data = unpack(9*'f', data)

    ms = f"acc[m/s²]: x={data[0]} y={data[1]} z={data[2]}"
    g = f"acc[g]: x={data[3]} y={data[4]} z={data[5]}"
    rad = f"gyr[rad/s]: x={data[6]} y={data[7]} z={data[8]}"

    msg = "\n".join([ms, g, rad])
    return msg + "\n"


def send_end_message():
    """ Funcion para enviar un mensaje de finalizacion a la ESP32 """
    end_message = pack('4s', 'END\0'.encode())
    ser.write(end_message)

# Se envia el mensaje de inicio de comunicacion
message = pack('6s','BEGIN\0'.encode())
send_message(message)
# Espera un tiempo antes de recibir OK
time.sleep(2)
receive_response()
print("empieza correctamente")

# Se lee data por la conexion serial
counter = 0
err_counter = 0
rms_ok = False
while True:
    if ser.in_waiting > 0 and counter < WINDOWS_SIZE:
        try:
            message = receive_data()
        except:
            #print(f'Error en leer mensaje {err_counter}')
            continue
        else: 
            counter += 1
            print(f"Lectura {counter}\n------------")
            print(message)
        finally:
            if counter == WINDOWS_SIZE:
                print('Lecturas listas!\n')
    elif ser.in_waiting > 0 and not rms_ok:
        try:
            message = receive_rms()
        except:
            continue
        else:
            rms_ok = True
            print("RMS\n------------")
            print(message)
        finally:
            if rms_ok:
                print('RMS listas!\n')



# Se envia el mensaje de termino de comunicacion
send_end_message()

ser.close()