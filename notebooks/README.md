# Notebooks — README

Conjunto de cuadernos que documentan la exploración, prototipado y experimentos previos al producto final de PLS. Incluyen EDA de los datos, un clasificador binario PLS vs no PLS, fine-tuning de modelos livianos para generar resúmenes en lenguaje sencillo y comparativas frente a LLMs comerciales.

---

## Guía rápida

- **Datos**: se leen desde `data/` (`df_train/validation/test.csv` y `evaluation_texts.csv`) para EDA y splits consistentes.
- **EDA**: cada notebook arranca con inspección de columnas, longitudes de texto y limpieza mínima antes de entrenar o evaluar.
- **Clasificador**: flujo TF-IDF + LogisticRegression (baseline y v2) para detectar si un texto ya es PLS.
- **Generadores PLS ligeros**: múltiples rutas de fine-tuning con modelos <=4B parámetros (MedGemma, Qwen, Llama 3.2 1B) y un pipeline <3B.
- **LLMs comerciales**: evaluación comparativa de ChatGPT y Claude sobre el mismo set de evaluación.

---

## Notebooks y propósito

| Notebook | Propósito | Temas clave / Artefactos |
|----------|-----------|--------------------------|
| `pls_classifier_baseline.ipynb` | Primer clasificador binario PLS vs no PLS. | TF-IDF (palabras y caracteres) + LogisticRegression balanceada; curva ROC, top features; exportación `model.joblib` y `meta/metrics`. |
| `pls_classifier_v2.ipynb` | Iteración del clasificador con ajustes de features/umbral. | Repite EDA, ajusta n-gramas y regularización, recalibra probabilidad y umbral de decisión. |
| `pls_generator_pipeline.ipynb` | Pipeline generador <3B. | Prompting y generación con modelo pequeño, limpieza de salida y chequeo rápido de legibilidad. |
| `pls_sft_medgemma.ipynb` | Fine-tuning de `google/medgemma-4b-it` con LoRA. | Carga cuantizada 4bit, SFT sin packing, plantilla de prompt optimizada, métricas automáticas (BERTScore, legibilidad). |
| `pls_sft_qwen.ipynb` | Fine-tuning estable en Colab (GPU L4) con Qwen. | QLoRA, control de LR/batch, guardado de checkpoints y evaluación con set de validación. |
| `pls_stf_llama.ipynb` | Generador PLS con Llama 3.2 1B. | SFT ligero para entornos con poca memoria; comparación de calidad vs modelos más grandes. |
| `pls_laysumm_stepbystep_backup.ipynb` | Respaldo de flujo QLoRA + AWS. | Secuencia paso a paso para montar entorno, cargar datos y entrenar; útil como guía operativa. |
| `pls_commercial_llm_eval.ipynb` | Comparativa de LLMs comerciales. | Evaluación de ChatGPT y Claude sobre textos médicos del repo; análisis de calidad y legibilidad frente a modelos finetuneados. |

---

## Cómo usar estos cuadernos

1. Abrir el EDA inicial de cada notebook para verificar que las rutas a `data/` coinciden con tu entorno.  
2. Ejecutar primero los clasificadores (`pls_classifier_baseline.ipynb`, `pls_classifier_v2.ipynb`) si necesitas el artefacto `model.joblib` para la API.  
3. Probar los generadores ligeros según tu presupuesto de GPU (`pls_generator_pipeline.ipynb` para <3B, `pls_stf_llama.ipynb` para 1B, `pls_sft_qwen.ipynb` o `pls_sft_medgemma.ipynb` para más capacidad y calidad).  
4. Usar `pls_commercial_llm_eval.ipynb` como línea base externa frente a modelos comerciales.  
5. `pls_laysumm_stepbystep_backup.ipynb` sirve de guía operativa si necesitas rehidratar el flujo en Colab/AWS.

---

## Notas de colaboración

Estos cuadernos recogen la fase de experimentación del equipo: limpieza y entendimiento de datos, entrenamiento iterativo del clasificador, afinamiento de generadores compactos y benchmarking contra LLMs comerciales. Son la base de las decisiones que llevaron al despliegue final documentado en `pls_deployment_project/`.
