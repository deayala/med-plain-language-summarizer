# Directorio de Datos

Este directorio contiene todos los datos utilizados y generados durante el proyecto. Se divide en dos categorías principales: los datos de entrada para el *fine-tuning* de los modelos de lenguaje y los resultados tabulados de los experimentos tanto para el clasificador como para los modelos generativos.

---

## Origen de los Datos de Entrada

Los datasets originales (`df_train.csv`, `df_test.csv`, etc.) fueron obtenidos a partir de los datos públicos de la investigación:

**“Bridging the Gap in Health Literacy: Harnessing the Power of Large Language Models to Generate Plain Language Summaries from Biomedical Texts”**
<br>
*Autores: Felipe Arias-Russi, Carolina Salazar-Lara, Rubén Manrique.*

- **Fuente en GitHub:** [Data Sources](https://github.com/feliperussi/bridging-the-gap-in-health-literacy/tree/main/data_collection_and_processing/Data%20Sources)
- **Publicación ACL Anthology:** [aclanthology.org/2025.cl4health-1.23](https://aclanthology.org/2025.cl4health-1.23/)

---

## Estructura y Contenido

### 📁 `fine_tunning/`
Contiene los datos de entrada para entrenar y evaluar los modelos generativos, así como los resultados consolidados de sus inferencias.

#### Datos de Entrada para el Fine-Tuning
Estos son los corpus principales utilizados para entrenar, validar y probar los modelos de generación de resúmenes.

| Archivo | Filas | Descripción |
| :--- | :--- | :--- |
| `df_train.csv` | 3,276 | Pares de texto técnico y resumen PLS para el entrenamiento. |
| `df_validation.csv` | 365 | Pares de texto técnico y resumen PLS para la validación durante el fine-tuning. |
| `df_test.csv` | 221 | Pares de texto técnico y resumen PLS para la evaluación final del modelo afinado. |
| `evaluation_texts.csv`| 100 | Muestra estratificada para la evaluación cualitativa y comparativa con modelos SOTA. |

#### Estadísticas de los Datos de Entrada
- **Longitudes de texto (caracteres, P99 / máximo)**
  - `technical_text`: 7326 / 28992
  - `plain_summary`: 5504 / 8934
- **Distribución de `source` (agregado)**
  - `Cochrane`: 98.3%
  - `Pfizer/ClinicalTrials`: 1.7%

#### Resultados de los Experimentos de Generación
Estos archivos contienen las salidas y métricas de todos los modelos generativos evaluados.

| Archivo | Descripción |
| :--- | :--- |
| `pls_all_models_finetuned_and_sota.csv` | Consolidado con las generaciones de todos los modelos (afinados y SOTA) sobre el set de `evaluation_texts.csv`. |
| `quantitative_metrics_all_models.csv` | Tabla con los resultados de las métricas cuantitativas (BERTScore, AlignScore, legibilidad) para cada modelo. |
| `qualitative_results_all_models.csv` | Tabla con los resultados de la evaluación cualitativa (factualidad, omisiones, jerga, etc.) para cada modelo. |

---

### 📁 `classifier/`
Contiene los resultados detallados de los experimentos realizados para entrenar y seleccionar el mejor modelo de clasificación PLS vs. no-PLS.

#### Resultados de los Experimentos del Clasificador

| Archivo | Descripción |
| :--- | :--- |
| `classifier_results.csv` | Resumen del rendimiento (F1, Accuracy, etc.) de los modelos de clasificación evaluados (LogReg, SVM). |
| `classifier_dataset_test.csv` | Conjunto de datos de prueba utilizado para la evaluación final del clasificador. |
| `classifier_cm_logreg_tfidf_wordchar.csv` | Datos de la matriz de confusión para el modelo de Regresión Logística. |
| `classifier_cm_svm_linear_tfidf_wordchar.csv`| Datos de la matriz de confusión para el modelo SVM lineal. |
| `classfier_errors_svm_linear_tfidf_wordchar.csv`| Muestras donde el modelo SVM cometió errores de clasificación. |

---

## Licenciamiento y Ética

El uso de estos datos debe ser exclusivamente para fines académicos, de investigación y desarrollo experimental, respetando las licencias del repositorio original de donde fueron obtenidos.
