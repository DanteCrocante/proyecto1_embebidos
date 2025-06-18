import serial
import struct
import time
import traceback


PORT        = 'dev/ttyUSB0'
BAUD_RATE   = 115200
WINDOW_SIZE = 20
N_PEAKS     = 5
BYTE_SIZE   = 4


class Conection:
    def __init__(self):
        self.s = serial.Serial(PORT, BAUD_RATE, timeout=1)

    def read(self, len, size, fmt_char):
        if self.s.in_waiting > 0:
            try:
                stream = self.s.read(len*size)
                data = struct.unpack(f"@{len}{fmt_char}", stream)
            except (struct.error, serial.SerialException) as e:
                print("A ocurrido un error")
                traceback.print_exception(e)
        
        return data
    
    def read_window(self):
        res = [round(f, 3) for f in self.read(WINDOW_SIZE, BYTE_SIZE, "f")]
        time.sleep(2)

        return res
    
    def read_data(self):
        res = round(self.read(1, BYTE_SIZE, "f")[0], 3)
        time.sleep(2)

        return res 
    
    def read_peaks(self):
        res = [round(f, 3) for f in self.read(N_PEAKS, BYTE_SIZE, "f")]
        time.sleep(2)

        return res
    
    def write(self, msg):
        self.s.write(msg)
        time.sleep(2)
    
    def close(self):
        self.s.close()

def print_measures(acc_ms, acc_g, gyr, acc_rms, gyr_rms, 
                   acc_fft, gyr_fft, acc_peaks, gyr_peaks):
    """Imprime en consola todas las mediciones y calculos recibidos desde el sensor"""
    
    print("========== MEDICION ===========")

    msg = "[m/s²]: "
    for i in range(WINDOW_SIZE):
        msg += f"({acc_ms['x'][i]}, {acc_ms['y'][i]}, {acc_ms['z'][i]}) " 
    print(msg)

    msg = "[g]: "
    for i in range(WINDOW_SIZE):
        msg += f"({acc_g['x'][i]}, {acc_g['y'][i]}, {acc_g['z'][i]}) " 
    print(msg)

    msg = "[rad/s]: "
    for i in range(WINDOW_SIZE):
        msg += f"({gyr['x'][i]}, {gyr['y'][i]}, {gyr['z'][i]}) " 
    print(msg)

    print("============= RMS =============")

    msg = "[m/s²]: "
    msg += f"({acc_rms['x']}, {acc_rms['y']}, {acc_rms['z']})" 
    print(msg)

    msg = "[rad/s]: "
    msg += f"({gyr_rms['x']}, {gyr_rms['y']}, {gyr_rms['z']})" 
    print(msg)

    print("============= FFT =============")

    msg = "acc_fft_re: "
    for i in range(WINDOW_SIZE):
        msg += f"({acc_fft['re'][i]}, {acc_fft['re'][i]}, {acc_fft['re'][i]}) " 
    print(msg)

    msg = "acc_fft_im: "
    for i in range(WINDOW_SIZE):
        msg += f"({acc_fft['im'][i]}, {acc_fft['im'][i]}, {acc_fft['im'][i]}) " 
    print(msg)

    msg = "gyr_fft_re: "
    for i in range(WINDOW_SIZE):
        msg += f"({gyr_fft['re'][i]}, {gyr_fft['re'][i]}, {gyr_fft['re'][i]}) " 
    print(msg)

    msg = "gyr_fft_im: "
    for i in range(WINDOW_SIZE):
        msg += f"({gyr_fft['im'][i]}, {gyr_fft['im'][i]}, {gyr_fft['im'][i]}) " 
    print(msg)

    print("============ PEAKS ============")

    msg = "[m/s²]: "
    for i in range(N_PEAKS):
        msg += f"({acc_peaks['x'][i]}, {acc_peaks['y'][i]}, {acc_peaks['z'][i]}) " 
    print(msg)

    msg = "[rad/s]: "
    for i in range(N_PEAKS):
        msg += f"({gyr_peaks['x'][i]}, {gyr_peaks['y'][i]}, {gyr_peaks['z'][i]}) " 
    print(msg)

if __name__ == "__main__":
    # Crear conexión con el sensor
    conn = Conection()

    # Enviar mensaje de inicio
    msg = struct.pack('6s', 'BEGIN\0'.encode())
    conn.write(msg)
    
    # Recibir mensaje de confirmación
    time.sleep(2)
    res = str(conn.read(3, 1, 's'))

    if res[:3] == "OK":
        print("-- Empieza Correctamente --")
    else:
        print("--¡ ERROR DE COMUNICACIÓN !--")
        exit(1)

    # Recibir mediciones
    axis = ['x', 'y', 'z']

    acc_ms, acc_g, gyr = {}, {}, {}

    acc_rms, gyr_rms = {}, {}

    acc_fft, gyr_fft = {'re': {}, 'im': {}}

    acc_peaks, gyr_peaks = {}, {}

    while True:
        try:
            for ax in axis:
                acc_ms[ax]   = conn.read_window()
                acc_g[ax]    = conn.read_window()
                gyr[ax]      = conn.read_window()

            for ax in axis:
                acc_rms[ax] = conn.read_data()
                gyr_rms[ax] = conn.read_data()
            
            for ax in axis:
                acc_fft['re'][ax] = conn.read_window()
                acc_fft['im'][ax] = conn.read_window()
                gyr_fft['re'][ax] = conn.read_window()
                gyr_fft['im'][ax] = conn.read_window()
            
            for ax in axis:
                acc_peaks[ax] = conn.read_peaks()
                gyr_peaks[ax] = conn.read_peaks()

            print_measures(acc_ms, acc_g, gyr, acc_rms, gyr_rms,
                           acc_fft, gyr_fft, acc_peaks, gyr_peaks)
            time.sleep(2)

            # Enviar mensaje de continuación
            msg = struct.pack('4s', 'NXT\0'.encode())
            conn.write(msg)

        except Exception as e:
            print("--¡ ERROR EN LA LECTURA !--")
            traceback.print_exception(e)

            # Enviar mensaje de termino
            msg = struct.pack('4s', 'END\0'.encode())
            conn.write(msg)

            # Cerrar conexión
            conn.close()
            break
