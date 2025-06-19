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

def receive_data(size):
    """ Funcion que recibe size floats de la ESP32 
    y los imprime en consola """
    if ser.in_waiting > 0:
        try:
            data = ser.read(size * 4)  # 4 bytes por float

            print("llegó hasta acá")

            data = unpack(size * 'f', data)

            print(f'Received: {data}')
            return data
        except Exception as e:
            print(f'Error en leer mensaje: {e}')
            return None

def receive_ventana():
    """ Funcion que recibe una ventana de datos (WINDOWS_SIZE floats) de la ESP32 
    y los imprime en consola """
    time.sleep(2)
    data = ser.read(WINDOWS_SIZE * 4)  # 4 bytes por float
    if data is None:
        print("No se recibieron datos")
        return []
    print(f"Ventana de datos recibida: {len(data)} elementos")
    if len(data) != WINDOWS_SIZE * 4:
        print(f"Error: se esperaban {WINDOWS_SIZE} datos, pero se recibieron {len(data)}")
        return []
    return unpack(WINDOWS_SIZE * 'f', data)

def receive_rms():
    """ Funcion que recibe nueve floats (fffffffff) de la ESP32 
    (que representan las rms) para tres ejes (x, y, z)
    y en m/s^2, G y Rad/s """
    time.sleep(2)
    rms = ser.read(9 * 4) # 4 bytes por float
    if rms is None:
        print("No se recibieron datos")
        return []
    print(f"rms de datos recibida: {len(rms)} elementos")
    if len(rms) != 9 * 4:
        print(f"Error: se esperaban {9} datos, pero se recibieron {len(rms)}")
        return []
    return unpack(9 * 'f', rms)

def receive_peaks():
    """ Funcion que recibe 5 picos por eje (x, y, z) de la ESP32 
    y los imprime en consola """
    time.sleep(2)
    peaks = [0] * 5
    for i in range(5):
        data = ser.read(4 * 5)  # 4 bytes por float
        if data is None:
            print("No se recibieron datos de Peaks")
            return []
        peaks[i] = unpack(5*'f', data)[0]
    print(f"Picos recibidos: {peaks}")
    return peaks


def send_continue_message():
    """ Funcion para enviar un mensaje de continuacion a la ESP32 """
    end_message = pack('9s', 'CONTINUE\0'.encode())
    ser.write(end_message)

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
# Ventanas de acelerómetro y giroscopio (por eje)
ventana_acc_x, ventana_acc_y, ventana_acc_z = [], [], []
ventana_gyro_x, ventana_gyro_y, ventana_gyro_z = [], [], []

# RMS: lista con 3 primeros para m/s², siguientes 3 G y ultimos 3 Rad/s
rms= []

# FFT: listas de 20 valores por eje 
fft_acc_ms_re = [[], [], []]  # X, Y, Z
fft_acc_ms_im = [[], [], []]
fft_acc_g_re = [[], [], []]
fft_acc_g_im = [[], [], []]
fft_gyro_rad_re = [[], [], []]
fft_gyro_rad_im = [[], [], []]

# Peaks: lista de 5 picos por eje 
peaks_acc_ms = [[], [], []]
peaks_acc_g = [[], [], []]
peaks_gyro_rad = [[], [], []]
while True:
    if ser.in_waiting > 0:
        try:
            # Recibir ventana de datos
            ventana_acc_x = receive_ventana()
            print(ventana_acc_x)
            time.sleep(2)
            ventana_acc_y = receive_ventana()
            time.sleep(2)
            ventana_acc_z = receive_ventana()
            time.sleep(2)
            ventana_gyro_x = receive_ventana()
            time.sleep(2)
            ventana_gyro_y = receive_ventana()
            time.sleep(2)
            ventana_gyro_z = receive_ventana()
            time.sleep(3)
            # Recibir RMS
            rms = receive_rms()
            time.sleep(2)
            print(rms)
            #Recibir FFT
            # parte real
            for i in range(3):
                fft_acc_ms_re[i] = receive_ventana()
                time.sleep(2)

            for i in range(3):
                fft_acc_g_re[i] = receive_ventana()
                time.sleep(2)
            for i in range(3):
                fft_gyro_rad_re[i] = receive_ventana()
                time.sleep(2)

            # parte imaginaria
            for i in range(3):
                fft_acc_ms_im[i] = receive_ventana()
                time.sleep(2)
            for i in range(3):
                fft_acc_g_im[i] = receive_ventana()
                time.sleep(2)
            for i in range(3):
                fft_gyro_rad_im[i] = receive_ventana()
                time.sleep(2)
                
            # Recibir Peaks
            time.sleep(2)
            peaks_acc_ms[0] = receive_peaks()
            time.sleep(2)
            peaks_acc_g[1] = receive_peaks()
            time.sleep(2)
            peaks_gyro_rad[2] = receive_peaks()
            time.sleep(2)
            counter += 1
            print(f'Lectura {counter} completada')

        except Exception as e:
            print(f'Error en leer mensaje: {e}')
            err_counter += 1
            if err_counter > 5:
                print("Demasiados errores, terminando la comunicacion")
                break
        finally:
            receive_response()
            send_end_message()
            ser.close()
            break