# Resumen del proyecto PLS

Documento en español que resume el estado del proyecto de resúmenes en lenguaje sencillo (Plain Language Summaries, PLS), los modelos entrenados, cómo reproducirlos desde los notebooks y la evidencia visual guardada en `models/assets/`.

## Modelos finales
- **Clasificador PLS vs NO PLS (LogReg + TF‑IDF)**: pipeline con uni/bi-gramas de palabras y 3‑5 gram de caracteres, vectorizado con TF‑IDF y clasificado con `LogisticRegression` balanceada (solver `saga`, `C=2.0`, `max_iter=2000`). El entrenamiento y exportación están en `notebooks/pls_classifier_baseline.ipynb`; el modelo final se publica como `model.joblib` junto con `meta.json` y `metrics.json` (ver imagen `models/assets/classifier_s3_tfidf_logreg.png`).
- **Generador PLS (MedGemma afinado)**: fine-tuning de `google/medgemma-4b-it` con LoRA vía Unsloth en 4 bits (`r=16`, `lora_alpha=32`, `dropout=0.05`, módulos q/k/v/o) y longitud máxima 2048. Toma como prompt un rol de *Health Literacy Expert* y produce PLS en nivel ~8.º grado. El flujo completo está en `notebooks/pls_sft_medgemma.ipynb`; el modelo se publica en Hugging Face como `deayala/med-gemma-finetuned` y se sirvió en un endpoint vLLM de Hugging Face Inference (ver imágenes `models/assets/endpoint_gemma-finetunning.png` y `models/assets/pls_gemma-finetunning.png`).

## Cómo reproducir/obtener los modelos
### 1) Clasificador LogReg PLS/NO PLS (`notebooks/pls_classifier_baseline.ipynb`)
1. Ajusta `BASE_DIR` a la carpeta con las fuentes (`Cochrane`, `Pfizer`, `Trial Summaries`, `ClinicalTrials.gov`). El script deduplica textos y conserva splits existentes; lo que no tiene split se separa estratificado (`DEFAULT_TEST_SIZE=0.2`, `RANDOM_STATE=17`).
2. Ejecuta las celdas de carga y deduplicación para generar `df_train` y `df_test` más los CSV de snapshot en `outputs_pls_classifier/`.
3. Entrena los modelos base; el mejor es `logreg_tfidf_wordchar` (usa TF‑IDF de palabras y caracteres + `LogisticRegression` balanceada). El notebook genera métricas, curva ROC y top features.
4. Exporta el pipeline a `best_model_<nombre>.joblib` y súbelo al bucket S3 si deseas replicar la estructura mostrada en `classifier_s3_tfidf_logreg.png`.

### 2) Generador PLS con MedGemma (`notebooks/pls_sft_medgemma.ipynb`)
1. Instala dependencias (Unsloth, TRL, PEFT, bitsandbytes, `transformers`, `datasets`, `evaluate`, `bert_score`, `textstat`) según la sección de instalación.
2. Define `BASE_PROJECT_DIR`, `MODEL_OUTPUT_DIR` y `MODEL_ID="google/medgemma-4b-it"`.
3. Carga y empareja los datos PLS/NO PLS (Cochrane, Pfizer, Trial Summaries, ClinicalTrials.gov), convierte a `DatasetDict` y formatea el prompt con la plantilla optimizada (rol experto, reglas de claridad y factualidad).
4. Carga el modelo cuantizado en 4 bits con `FastLanguageModel.from_pretrained`, aplica LoRA con los hiperparámetros anteriores y entrena con `SFTTrainer` (batch efectivo 32, 2 épocas, sin packing).
5. Evalúa con métricas automáticas (BERTScore, legibilidad `textstat`, factualidad con NLI y QA) y, en entornos aislados, AlignScore. Guarda resultados y checkpoints en `MODEL_OUTPUT_DIR` y publícalos en Hugging Face (`pls_gemma-finetunning.png` muestra los artefactos subidos).
6. Para inferencia, fusiona adaptadores, carga el tokenizer y usa `generate` con `top_p=0.9`, `temperature=0.3`, `max_new_tokens=800` y limpieza de patrones repetitivos. Opcionalmente despliega un endpoint vLLM en Hugging Face Inference (ver `endpoint_gemma-finetunning.png`).

## Evidencia visual (`models/assets/`)
- `classifier_s3_tfidf_logreg.png`: bucket S3 `tfidf_logreg/` con `meta.json`, `metrics.json` y `model.joblib` (artefacto del clasificador LogReg PLS/NO PLS).
- `endpoint_gemma-finetunning.png`: endpoint Hugging Face Inference `med-gemma-finetuned` en pausa, motor vLLM (`vllm-openai:v0.11.0`), AWS us-east-1 con GPU Nvidia L4 24GB, scale-to-zero y puerto 8000.
- `hugging_face_main.png`: perfil de Hugging Face `deayala` con modelos privados `med-gemma-finetuned`, `qwen-pls-finetuned` y `qwen-pls-fp16-finetuned` (sin datasets).
- `pls_gemma-finetunning.png`: repositorio `deayala/med-gemma-finetuned` mostrando safetensors, configuraciones (`adapter_config.json`, `generation_config.json`, `tokenizer_config`, etc.) y commit verificado.
- `pls_qwen_finetunning.png`: repositorio `deayala/qwen-pls-fp16-finetuned` con archivos de configuración, merges y pesos safetensors en fp16.

## Licenciamiento de MedGemma
Consulta los términos de uso y licenciamiento de MedGemma en la documentación oficial traducida: https://developers-google-com.translate.goog/health-ai-developer-foundations/medgemma?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=tc

## Referencias rápidas
- Clasificador PLS/NO PLS (TF‑IDF + LogReg): `notebooks/pls_classifier_baseline.ipynb`
- Generador PLS (MedGemma + LoRA + Unsloth): `notebooks/pls_sft_medgemma.ipynb`
