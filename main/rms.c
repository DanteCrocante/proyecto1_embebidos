#include <stdio.h>
#include <math.h>
#include "vars.h"
/* Calcula el RMS de un arreglo de datos (floats). */
float RMS(float *datos, int size) {
    float suma = 0.0;
    for (int i = 0; i < size; i++) {
        suma += datos[i] * datos[i];
    }
    return sqrtf(suma / size);
}