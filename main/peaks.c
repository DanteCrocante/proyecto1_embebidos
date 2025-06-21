#include <stdio.h>
#include <math.h>
#include "vars.h"
/*Encontrar los 5 peaks maximos*/
void encontrar_peaks(float *datos, float *peaks) {
    int i, j;
    float maximo;

    for (i = 0; i < 5; i++) {
        maximo = -1.0;
        for (j = 0; j < WINDOW_LENGTH; j++) {
            if (datos[j] > maximo) {
                maximo = datos[j];
            }
        }
        peaks[i] = maximo;
        for (j = 0; j < WINDOW_LENGTH; j++) {
            if (datos[j] == maximo) {
                datos[j] = -1.0;
                break;
            }
        }
    }
}