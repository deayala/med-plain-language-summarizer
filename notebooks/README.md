# Directorio de Notebooks de Investigación

Este directorio es el corazón del proceso de investigación y desarrollo del proyecto. Contiene los cuadernos de Jupyter que documentan el viaje desde la preparación de los datos crudos hasta el análisis comparativo final y la generación de los resultados presentados en el trabajo de grado.

Los notebooks están numerados para reflejar el flujo lógico del trabajo. El notebook `1_...` es el principal y más completo, mientras que el `2_...` se enfoca en un componente específico. Los experimentos exploratorios que no formaron parte de la solución final se han movido a la carpeta `archive/`.

---

## Flujo de Trabajo y Notebooks Principales

### 1. Pipeline Completo: Fine-Tuning, Evaluación y Análisis Comparativo
**`1_pls_generator_finetuning.ipynb`**

Este es el **notebook maestro** del proyecto. Implementa el pipeline completo de investigación, inspirado en la metodología CRISP-ML(Q), abarcando desde la configuración del entorno hasta la generación de las tablas de reporte finales. Su objetivo es demostrar de manera reproducible si un modelo compacto (<4B) ajustado eficientemente puede competir con modelos fundacionales de gran escala.

El contenido de este notebook se estructura en las siguientes fases clave:

-   **Fase 0: Configuración del Entorno:** Instalación de librerías especializadas como `unsloth` para un fine-tuning acelerado, el ecosistema de Hugging Face (`transformers`, `peft`, `trl`), y las librerías de evaluación.

-   **Fase 1: Carga y Preprocesamiento de Datos:** Construcción de un dataset unificado a partir de las fuentes de datos originales (Cochrane, Pfizer, etc.), realizando el emparejamiento de textos y la partición estratificada en conjuntos de `train`, `validation` y `test`.

-   **Fase 2: Ingeniería de Prompt y Configuración del Modelo:**
    -   Diseño de una plantilla de prompt avanzada que asigna un rol al LLM ("Health Literacy Expert") y define reglas estrictas de factualidad, legibilidad y formato.
    -   Carga del modelo `google/medgemma-4b-it` con cuantización a 4 bits (`bitsandbytes`) y configuración de adaptadores **QLoRA** para un entrenamiento eficiente en memoria.

-   **Fase 3: Entrenamiento Supervisado (SFT):** Orquestación y ejecución del fine-tuning utilizando el `SFTTrainer` de la librería `trl`, guardando el mejor checkpoint basado en el *validation loss*.

-   **Fase 4: Inferencia en Lote y Comparativa con Modelos SOTA:**
    -   Generación de resúmenes para el conjunto de evaluación (100 textos) con el modelo MedGemma afinado.
    -   Establecimiento de una línea base de rendimiento generando resúmenes con modelos fundacionales *zero-shot* como **Gemini 2.5 Flash** y **Llama 3.1 8B Instruct**.

-   **Fase 5: Evaluación Cuantitativa y Cualitativa:**
    -   **Métricas Estándar:** Cálculo de BERTScore, factualidad (NLI y QA) y un panel de métricas de legibilidad.
    -   **Métrica Avanzada (AlignScore):** Implementación de un flujo MLOps que crea un **entorno virtual aislado de Python 3.10** para ejecutar AlignScore, evitando conflictos de dependencias con el entorno principal de entrenamiento.
    -   **Evaluación Cualitativa (LLM-as-Judge):** Uso de un LLM avanzado (**Gemini 2.5 Flash Lite**) como "juez" para evaluar los resúmenes generados en dimensiones narrativas, con un prompt estructurado que devuelve la salida en formato JSON.

-   **Fase 6: Evaluación Final y Reporte Consolidado:** Unificación de todos los resultados (cuantitativos y cualitativos) de todos los modelos (ajustados y fundacionales) para generar las tablas comparativas finales en formato Markdown, listas para ser incluidas en el documento del trabajo de grado.

### 2. Clasificación de Estilo (PLS vs. no-PLS)
**`2_pls_classifier.ipynb`**

Este notebook se enfoca exclusivamente en el desarrollo del clasificador binario, un componente de apoyo en la arquitectura final.
-   **Análisis y Entrenamiento:** Explora representaciones de texto dispersas (TF-IDF) y entrena modelos clásicos (Regresión Logística, SVM).
-   **Selección de Modelo:** Se selecciona el pipeline **TF-IDF + Regresión Logística** como la solución final por su excelente equilibrio entre rendimiento (F1-score > 0.99), eficiencia e interpretabilidad.
-   **Artefactos Generados:** El modelo final (`model.joblib`) que se utiliza en la API desplegada.

---

## 📁 `archive/` — Experimentos Archivados

Esta carpeta contiene notebooks de experimentos exploratorios y modelos que no fueron seleccionados para la solución final. Sirven como registro del proceso iterativo de investigación. Incluye el fine-tuning de modelos como **Qwen** y **Llama**, así como versiones anteriores de los flujos principales.

---

## Guía para la Reproducibilidad

1.  **Comience con `1_pls_generator_finetuning.ipynb`:** Este notebook es autocontenido y reproduce la mayor parte de la investigación. Es el punto de partida recomendado.
2.  **Ejecute `2_pls_classifier.ipynb` de forma independiente:** Si desea generar o re-entrenar el artefacto del clasificador (`.joblib`), este notebook puede ejecutarse por separado.
3.  **Consulte la carpeta `archive/`** para entender las decisiones de diseño y las alternativas que se exploraron durante el proyecto.