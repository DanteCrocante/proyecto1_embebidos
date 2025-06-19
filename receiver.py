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
    peaks = ser.read(5 * 4)  # 4 bytes por float
    if peaks is None:
        print("No se recibieron datos")
        return []
    print(f"Peaks de datos recibida: {len(peaks)} elementos")
    if len(peaks) != 5 * 4:
        print(f"Error: se esperaban {5} datos, pero se recibieron {len(peaks)}")
        return []
    return unpack(5 * 'f', peaks)


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
ventana_acc_x_ms, ventana_acc_y_ms, ventana_acc_z_ms = [], [], []
ventana_acc_x_g, ventana_acc_y_g, ventana_acc_z_g = [], [], []
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
            ventana_acc_x_ms = receive_ventana()
            time.sleep(2)
            ventana_acc_y_ms = receive_ventana()
            time.sleep(2)
            ventana_acc_z_ms = receive_ventana()
            time.sleep(2)
            ventana_acc_x_g = receive_ventana()
            time.sleep(2)
            ventana_acc_y_g = receive_ventana()
            time.sleep(2)
            ventana_acc_z_g = receive_ventana()
            time.sleep(2)
            print("Ventanas de acelerómetro recibidas correctamente")
            ventana_gyro_x = receive_ventana()
            time.sleep(2)
            ventana_gyro_y = receive_ventana()
            time.sleep(2)
            ventana_gyro_z = receive_ventana()
            print("Ventanas de giroscopio recibidas correctamente")
            print("Ventanas recibidas correctamente")
            print(f"Ventana Acc X  m/s²: {ventana_acc_x_ms}")
            print(f"Ventana Acc Y  m/s²: {ventana_acc_y_ms}")
            print(f"Ventana Acc Z  m/s²: {ventana_acc_z_ms}")
            print(f"Ventana Acc X  G: {ventana_acc_x_g}")
            print(f"Ventana Acc Y  G: {ventana_acc_y_g}")
            print(f"Ventana Acc Z  G: {ventana_acc_z_g}")
            print(f"Ventana Gyro X  rad/s: {ventana_gyro_x}")
            print(f"Ventana Gyro Y  rad/s: {ventana_gyro_y}")
            print(f"Ventana Gyro Z  rad/s: {ventana_gyro_z}")
            time.sleep(3)
            # Recibir RMS
            rms = receive_rms()
            print("RMS recibidas correctamente")
            print(f"RMS (X, Y, Z): {rms[0:3]} m/s², {rms[3:6]} G, {rms[6:9]} rad/s")
            time.sleep(2)
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
            print("FFT recibidas correctamente")
            print(f"FFT Acc X m/s²: {fft_acc_ms_re[0]} (Re), {fft_acc_ms_im[0]} (Im)")
            print(f"FFT Acc Y m/s²: {fft_acc_ms_re[1]} (Re), {fft_acc_ms_im[1]} (Im)")
            print(f"FFT Acc Z m/s²: {fft_acc_ms_re[2]} (Re), {fft_acc_ms_im[2]} (Im)")
            print(f"FFT Acc X G: {fft_acc_g_re[0]} (Re), {fft_acc_g_im[0]} (Im)")
            print(f"FFT Acc Y G: {fft_acc_g_re[1]} (Re), {fft_acc_g_im[1]} (Im)")
            print(f"FFT Acc Z G: {fft_acc_g_re[2]} (Re), {fft_acc_g_im[2]} (Im)")
            print(f"FFT Gyro X rad/s: {fft_gyro_rad_re[0]} (Re), {fft_gyro_rad_im[0]} (Im)")
            print(f"FFT Gyro Y rad/s: {fft_gyro_rad_re[1]} (Re), {fft_gyro_rad_im[1]} (Im)")
            print(f"FFT Gyro Z rad/s: {fft_gyro_rad_re[2]} (Re), {fft_gyro_rad_im[2]} (Im)")
            # Recibir Peaks
            time.sleep(2)
            for i in range(3):
                peaks_acc_ms[i] = receive_peaks()
                time.sleep(2)
            for i in range(3):
                peaks_acc_g[i] = receive_peaks()
                time.sleep(2)
            for i in range(3):
                peaks_gyro_rad[i] = receive_peaks()
                time.sleep(2)
            print("Peaks recibidos correctamente")
            print(f"Peaks Acc X m/s²: {peaks_acc_ms[0]}")
            print(f"Peaks Acc Y m/s²: {peaks_acc_ms[1]}")
            print(f"Peaks Acc Z m/s²: {peaks_acc_ms[2]}")
            print(f"Peaks Acc X G: {peaks_acc_g[0]}")
            print(f"Peaks Acc Y G: {peaks_acc_g[1]}")
            print(f"Peaks Acc Z G: {peaks_acc_g[2]}")
            print(f"Peaks Gyro X rad/s: {peaks_gyro_rad[0]}")
            print(f"Peaks Gyro Y rad/s: {peaks_gyro_rad[1]}")
            print(f"Peaks Gyro Z rad/s: {peaks_gyro_rad[2]}")
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