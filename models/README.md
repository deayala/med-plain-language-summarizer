# Directorio de Artefactos de Modelos

Este directorio contiene los artefactos finales y entrenados de los modelos de machine learning desarrollados en el proyecto. Estos archivos son el resultado de los procesos de experimentación y entrenamiento documentados en la carpeta `notebooks/` y están listos para ser utilizados por la aplicación en la carpeta `deployment/`.

---

## Contenido

- **`pls_classifier/`**: Contiene los artefactos del modelo de clasificación de estilo (PLS vs. no-PLS).
- **`pls_generator_medgemma/`**: Contiene el adaptador LoRA resultante del proceso de fine-tuning del modelo MedGemma para la generación de resúmenes.

---

### 📁 `pls_generator_medgemma/`

Este directorio contiene el adaptador **LoRA (Low-Rank Adaptation)** generado tras el ajuste fino del modelo base `google/medgemma-4b-it`. No contiene el modelo completo, sino únicamente los pesos del adaptador que modifican su comportamiento para la tarea de generación de PLS.

- **Modelo Base:** `google/medgemma-4b-it`
- **Técnica de Fine-Tuning:** QLoRA (Quantized Low-Rank Adaptation) con cuantización de 4 bits.
- **Proceso de Entrenamiento:** Documentado en `notebooks/1_pls_generator_finetuning.ipynb`.

#### Contenido Clave del Directorio

| Archivo | Descripción |
| :--- | :--- |
| `adapter_model.safetensors` | Los pesos del adaptador LoRA entrenado. Es el artefacto principal. |
| `adapter_config.json` | Archivo de configuración que define la arquitectura del adaptador (ej. `r`, `lora_alpha`). |
| `tokenizer.json`, `tokenizer.model`| Archivos del tokenizador utilizado durante el entrenamiento. |
| `README.md` | Documentación del modelo publicado en Hugging Face. |

#### Uso y Despliegue

Este adaptador está diseñado para ser cargado junto con el modelo base usando la librería `peft` de Hugging Face. En este proyecto, el modelo completo (base + adaptador) fue publicado en el Hugging Face Hub y es consumido a través de un **Endpoint de Inferencia**, como se detalla en la arquitectura de despliegue.

- **Repositorio en Hugging Face:** [`deayala/med-gemma-finetuned`](https://huggingface.co/deayala/med-gemma-finetuned)

---

### 📁 `pls_classifier/`

Este directorio contiene los artefactos de los modelos de clasificación entrenados. Aunque se experimentó con varios enfoques, el modelo seleccionado para el despliegue final fue el de **TF-IDF + Regresión Logística** por su excelente balance entre rendimiento, eficiencia computacional e interpretabilidad.

- **Modelo Seleccionado (para Despliegue):** TF-IDF + Regresión Logística.
- **Características:** Vectorizador TF-IDF con n-gramas de palabras (1-2) y caracteres (3-5), y un clasificador de Regresión Logística con regularización.
- **Proceso de Entrenamiento:** Documentado en `notebooks/2_pls_classifier.ipynb`.

#### Artefacto de Despliegue

El artefacto final del modelo TF-IDF + Regresión Logística (`model.joblib`, `meta.json`, etc.) se encuentra en `deployment/models/production/`, ya que es cargado directamente por la API durante la ejecución.

#### Nota sobre los Archivos en este Directorio

Los checkpoints de transformador (`best/`, `checkpoint-xxxx/`) presentes en este directorio corresponden a los **experimentos realizados con modelos contextuales** (basados en DistilBERT). Aunque mostraron un rendimiento muy alto, se optó por el modelo clásico para producción debido a su menor costo operacional. Estos archivos se conservan como evidencia del proceso de investigación comparativa.

---

## Integración en la Arquitectura

En la arquitectura final del proyecto, estos modelos se integran de la siguiente manera:

- El **Generador PLS** (`pls_generator_medgemma`) es servido a través de un endpoint remoto de Hugging Face y es llamado por la API en `deployment/`.
- El **Clasificador PLS** (`pls_classifier`) es un archivo local (`.joblib`) que la API en `deployment/` carga al iniciarse para realizar predicciones de estilo de manera eficiente.
