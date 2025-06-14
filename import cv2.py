### 1) Importe las librerías necesarias ###
import pydicom
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

### 1) Ubique la carpeta con los archivos DICOM y muestre los nombres de los diferentes archivos ###
# Supongamos que los archivos DICOM están en la carpeta 'dicom_files'
dicom_folder = 'dicom_files'
dicom_files = os.listdir(dicom_folder)
print("Archivos DICOM encontrados:")
for file in dicom_files:
    print(file)

### 2) Lea todos los archivos allí contenidos e ingrese los datasets en una lista ###
datasets = [pydicom.dcmread(os.path.join(dicom_folder, file)) for file in dicom_files]

### 3) Ordene los datasets si es necesario ###
# Verificar si tienen ImagePositionPatient o SliceLocation
if hasattr(datasets[0], 'ImagePositionPatient'):
    # Ordenar por la coordenada Z (tercer elemento de ImagePositionPatient)
    datasets.sort(key=lambda ds: ds.ImagePositionPatient[2])
elif hasattr(datasets[0], 'SliceLocation'):
    datasets.sort(key=lambda ds: ds.SliceLocation)
else:
    print("No se encontraron atributos para ordenar las imágenes")

### 4) Muestre los dataelements de cualquier dataset ###
print("\nElementos de datos de un dataset de ejemplo:")
print(datasets[0])

### 5) Visualice la imagen de cualquiera de los datasets leidos ###
plt.figure(figsize=(10, 6))
plt.imshow(datasets[10].pixel_array, cmap='gray')  # Mostrar el dataset 10
plt.title(f"Imagen DICOM - Profundidad: {datasets[10].pixel_array.dtype}")
plt.colorbar()
plt.show()

### 6) Genere el "sólido" a partir de todas las imágenes superpuestas ###
# Crear un array 3D con todas las imágenes
volume = np.stack([ds.pixel_array for ds in datasets])
print(f"\nDimensiones del volumen 3D: {volume.shape}")

### 7) Muestre en 3 subplots horizontales los cortes coronal, sagital y axial ###
# Obtener índices centrales para cada plano
axial_idx = volume.shape[0] // 2
sagital_idx = volume.shape[1] // 2
coronal_idx = volume.shape[2] // 2

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))

# Corte axial
ax1.imshow(volume[axial_idx, :, :], cmap='gray')
ax1.set_title('Corte Axial')

# Corte sagital
ax2.imshow(volume[:, sagital_idx, :], cmap='gray')
ax2.set_title('Corte Sagital')

# Corte coronal
ax3.imshow(volume[:, :, coronal_idx], cmap='gray')
ax3.set_title('Corte Coronal')

plt.tight_layout()
plt.show()

### 8) Extraiga toda la información del paciente asociado al estudio ###
def get_patient_info(ds):
    info = {
        'PatientName': getattr(ds, 'PatientName', ''),
        'PatientID': getattr(ds, 'PatientID', ''),
        'PatientBirthDate': getattr(ds, 'PatientBirthDate', ''),
        'PatientSex': getattr(ds, 'PatientSex', ''),
        'PatientAge': getattr(ds, 'PatientAge', ''),
        'StudyDate': getattr(ds, 'StudyDate', ''),
        'StudyDescription': getattr(ds, 'StudyDescription', ''),
        'Modality': getattr(ds, 'Modality', ''),
        'InstitutionName': getattr(ds, 'InstitutionName', '')
    }

# (0010,0010) Patient's Name                      PN: 'C3N-00247'
# (0010,0020) Patient ID                          LO: 'C3N-00247'
# (0010,0030) Patient's Birth Date                DA: ''
# (0010,0040) Patient's Sex                       CS: 'F'
# (0010,1010) Patient's Age                       AS: '077Y'
# (0010,2160) Ethnic Group                        SH: '8'
    return info

patient_info = get_patient_info(datasets[0])
print("\nInformación del paciente:")
for key, value in patient_info.items():
    print(f"{key}: {value}")

### 9) Los datos que estén anonimizados modifíquelos por información ficticia ###
# Verificar si los datos están anonimizados (nombres genéricos o vacíos)
if patient_info['PatientName'] == '' or 'Anonymized' in patient_info['PatientName']:
    print("\nDatos anonimizados detectados. Reemplazando con información ficticia...")
    for ds in datasets:
        ds.PatientName = "Paciente Ejemplo"
        ds.PatientID = "123456"
        ds.PatientBirthDate = "19800101"
        ds.PatientSex = "O"
        ds.PatientAge = "042Y"
    
    # Guardar los datasets modificados
    output_folder = 'dicom_files_modified'
    os.makedirs(output_folder, exist_ok=True)
    
    for i, ds in enumerate(datasets):
        ds.save_as(os.path.join(output_folder, f"modified_{i}.dcm"))

### 10) Función que grafique un histograma de la matriz (imagen) ###
def plot_histogram(image, title="Histograma de intensidades"):
    plt.figure(figsize=(8, 5))
    plt.hist(image.flatten(), bins=50, color='blue', alpha=0.7)
    plt.title(title)
    plt.xlabel("Intensidad")
    plt.ylabel("Frecuencia")
    plt.grid(True)
    plt.show()

# Ejemplo de uso
plot_histogram(datasets[0].pixel_array, "Histograma de un corte axial")

### 11) Subplot horizontal de 3 tramas con histogramas de cortes diferentes ###
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))

# Histograma del corte axial
ax1.hist(volume[axial_idx, :, :].flatten(), bins=50, color='blue', alpha=0.7)
ax1.set_title('Histograma - Corte Axial')
ax1.grid(True)

# Histograma del corte sagital
ax2.hist(volume[:, sagital_idx, :].flatten(), bins=50, color='green', alpha=0.7)
ax2.set_title('Histograma - Corte Sagital')
ax2.grid(True)

# Histograma del corte coronal
ax3.hist(volume[:, :, coronal_idx].flatten(), bins=50, color='red', alpha=0.7)
ax3.set_title('Histograma - Corte Coronal')
ax3.grid(True)

plt.tight_layout()
plt.show()
