# TA06-Garcia-Erick-Yabrudy-Richard-Francisco-Diaz-Grupo03
The objective of this task, is to use the power of data and the most advanced AI technologies trained with “our expertise”, to tailor solutions in the green transformation, be it decarbonization, decontamination, resource saving and regeneration, or any other solution.

<div align="center">
  <h1>
    <a href="TA06/E04/index.html">Ir a mi página principal</a>
  </h1>
</div>


# 01 Obtencion de datos
Dentro del la web _AEMET_ debemos de obtener una API Key ingresando nuestro email, el generador de key debera llegar al correro electronico, donde posteriormente llegara un mensaje con la key, esto debera ser realizado por un solo usuario del grupo.
![image](https://github.com/user-attachments/assets/00abf3a8-fd83-4ced-9c85-6648bcbd0514)
![image](https://github.com/user-attachments/assets/e7e5bf6e-7947-4c1b-9dec-34b8f53e8d94)

Una vez obtenidas las credenciales, buscamos el apartado correspondiente a la tarea, dentro de este debemos de filtrar la informacion a lo necesario para la practica, siendo los parametros los siguientes:
 - Método: Regresión Rejilla
 - Modelo: MIROC5
 - Escenarios: RCP6.0
 - Variable: Precipitación
 - Periodo: 2006 - 2100
 
![image](https://github.com/user-attachments/assets/a9bacd1b-be95-4533-af59-ca2b1ca8e412)

El archivo que descaragaremos tendra un tamaño de 360MB el cual es un .tar.gz:

![Captura de pantalla de 2025-01-13 09-21-40](https://github.com/user-attachments/assets/5add685a-939c-4c5d-9d9d-6878307a7b74)

Una vez descargado y extraido, el mismo se debe de subir a uno de los directorios de TA06, en este caso el E01, finalmente mostrandose de la siguiente manera:

![image](https://github.com/user-attachments/assets/00741270-248b-4e58-9a3a-9534732811e1)

Al abrir cada archivo de datos se muestra, lo siguiente:

![image](https://github.com/user-attachments/assets/bc90edf0-06e4-4943-b0dd-100ac5affa88)


# 02 Organización y procesamiento de datos
Para organizar y procesar las datos, seguimos estos pasos:  

## Lectura de archivos:  


- Revisamos las cabeceras, la separación entre datos, comentarios, etc. 

`header = f.readline().strip()`

- Detectamos delimitadores (espacios, comas o tabulaciones).

`delimiter = detect_delimiter(header)`


- Verificamos que todos los archivos tienen el mismo formato, y que no hubieran otros diferentes.

## Verificación del formato:  

- Creamos un script de validación básica para leer las primeras filas de cada archivo y determinar el número de columnas y delimitadores.

`columns = len(header.split(delimiter))`

- Nos aseguramos de que las columnas tenían el tipo de datos esperado (numérico, fecha, etc.).

## Limpieza de datos:  

- Gestionamos los errores de lectura utilizando pandas.

```python
import pandas as pd`
df = pd.read_csv(file_path, delimiter=delimiter, error_bad_lines=False)`
```

- Además verificamos la consistencia de las columnas.
- E identificamos y tratamos datos nulos o valores atípicos.

## 03 Validación y cálculo de estadísticas

Para validar los archivos y calcular estadísticas, actualizamos nuestro script en Python.

![Trabajando coop](TA06/images/trabajando.png)

*El fotógrafo estaba trabajando también dentro del trabajo y fue quien tomó la foto ;)*

Este proceso nos costó mucho esfuerzo y tuvimos que pulirlo varias veces porque no paraba de fallar el script o el Copilot generaba código que requería supervisión. 

![img.png](TA06/images/img.png)

Finalmente, logramos que funcionara correctamente, y actualmente realiza las siguientes tareas:

- Detecta y normaliza delimitadores.

normalize_delimiter(file_path, delimiter)

- Valida encabezados y metadatos.

```python
if not validate_header(lines[0]):
    errors.append(f"Invalid header: {lines[0].strip()}")
```


- Verifica la consistencia de los datos.

`valid, error = validate_data_line(line, expected_columns)`

- Calcula estadísticas anuales de precipitación.

`total_rainfall += rainfall`

- Muestra un resumen de la validación y la tasa de cambio anual de las precipitaciones.

## 04 Resultados

Al finalizar la validación, obtuvimos las siguientes estadísticas:  

- Errores encontrados: Número total de errores en los archivos.
- Líneas procesadas: Número total de líneas procesadas.
- Valores totales procesados: Número total de valores procesados.
- Valores faltantes (-999): Número total de valores faltantes.
- Porcentaje de valores faltantes: Porcentaje de valores faltantes respecto al total.
- Precipitación total: Precipitación total acumulada.
- Precipitación media anual: Precipitación media anual.
- Año más seco: Año con la menor precipitación.
- Año más lluvioso: Año con la mayor precipitación.

Además, mostramos la tasa de cambio anual de las precipitaciones en formato tabular.

## 05 Representación en base a las estadísticas

## Reporte de Cambios en la Generación de Gráficos y Cálculo del Tiempo

### Generación de Gráficos

1. **Inclusión de Timestamps en los Nombres de los Archivos:**
   - Se añadió una marca de tiempo (timestamp) a los nombres de los archivos de los gráficos generados para evitar la sobrescritura cuando el código se ejecuta más de una vez al día.
   - La marca de tiempo se obtiene utilizando `current_time = datetime.now().strftime("%Y%m%d%H%M%S")`.

2. **Generación de Gráficos:**
   - Se crearon dos gráficos:
     - **Promedio Móvil de Precipitación:** Un gráfico de serie temporal que muestra el promedio móvil de la precipitación anual.
     - **Variación Estacional de Precipitación:** Un boxplot que muestra la variación estacional de la precipitación mensual.

3. **Nombres de los Archivos de Gráficos:**
   - Los nombres de los archivos de los gráficos incluyen la marca de tiempo para asegurar que cada archivo generado es único. Los archivos se guardan como `precipitation_trend_{current_time}.png` y `seasonal_variation_{current_time}.png`.

### Cálculo del Tiempo de Generación de Gráficos

1. **Medición del Tiempo de Generación:**
   - Se utilizó el módulo `time` para capturar el tiempo antes y después de la generación de cada gráfico.
   - La diferencia de tiempo se calculó y se imprimió en la consola para mostrar cuánto tiempo tomó generar cada gráfico.

2. **Código para la Medición del Tiempo:**
   - Antes de generar cada gráfico, se captura el tiempo de inicio: `start_time = time.time()`.
   - Después de generar cada gráfico, se captura el tiempo de finalización: `end_time = time.time()`.
   - Se calcula la duración restando `start_time` de `end_time` y se imprime en la consola.

### Ejemplo de Código

```python
# Obtener la marca de tiempo actual para los nombres de archivos
current_time = datetime.now().strftime("%Y%m%d%H%M%S")

# Medir el tiempo para generar el primer gráfico
start_time = time.time()
plt.figure(figsize=(12, 6))
plt.plot(annual_totals['year'], annual_totals['rolling_avg'])
plt.title('Promedio Móvil de Precipitación')
plt.xlabel('Año')
plt.ylabel('Promedio Móvil de Precipitación')
plt.grid(True)
plt.savefig(f'precipitation_trend_{current_time}.png')
plt.close()
end_time = time.time()
print(f"Tiempo para generar el gráfico de Promedio Móvil de Precipitación: {end_time - start_time:.2f} segundos")

# Medir el tiempo para generar el segundo gráfico
start_time = time.time()
plt.figure(figsize=(10, 6))
sns.boxplot(x='month', y='total_rainfall', data=monthly_totals)
plt.title('Variación Estacional de Precipitación')
plt.xlabel('Mes')
plt.ylabel('Precipitación Total')
plt.grid(True)
plt.savefig(f'seasonal_variation_{current_time}.png')
plt.close()
end_time = time.time()
print(f"Tiempo para generar el gráfico de Variación Estacional de Precipitación: {end_time - start_time:.2f} segundos")
```

## Conclusión
Estos cambios aseguran que cada ejecución del código genera gráficos únicos y permite medir y reportar el tiempo de generación de los gráficos de manera precisa. Esto es útil para el monitoreo del rendimiento y para evitar conflictos de nombres de archivos en ejecuciones múltiples en el mismo día.
