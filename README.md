# Proyecto PLS — Visión General

Sistema completo para generar y clasificar resúmenes en lenguaje sencillo (Plain Language Summaries, PLS) de textos biomédicos. Incluye datos usados, notebooks de experimentación, artefactos de modelos (clasificador y generadores afinados), y una arquitectura de despliegue con API FastAPI, microservicio de AlignScore y front Angular servido con nginx.

---

## Mapa de carpetas y documentación

- `data/` — splits de entrenamiento/validación/prueba y textos de evaluación. Métricas de longitud y ejemplos en [`data/README.md`](data/README.md).
- `notebooks/` — EDA, clasificador PLS vs no PLS, fine-tuning de generadores (MedGemma, Qwen, Llama) y comparativa de LLMs comerciales. Resumen en [`notebooks/README.md`](notebooks/README.md).
- `models/` — artefactos finales y evidencia visual (clasificador TF-IDF+LogReg y generadores afinados). Detalle en [`models/README.md`](models/README.md).
- `pls_deployment_project/` — stack tecnológico usado en el despliegue: FastAPI + AlignScore + front Angular/nginx, Docker Compose, Terraform y scripts. Guía en [`pls_deployment_project/README.md`](pls_deployment_project/README.md).
- `outputs/` — resultados de entrenamiento y snapshots de experimentos.

---

## Componentes de ML

- **Clasificador PLS vs no PLS**: TF-IDF (palabras y caracteres) + LogisticRegression balanceada, umbral configurable. Entrenamiento en `notebooks/pls_classifier_baseline.ipynb`
- **Generador PLS (MedGemma afinado)**: `google/medgemma-4b-it` con LoRA 4bit, mejor calidad cualitativa y cuantitativa. Publicado en Hugging Face como `deayala/med-gemma-finetuned` y servido vía endpoint HF Inference.
- **Experimentos adicionales**: pipeline <3B, Llama 3.2 1B y comparativa de LLMs comerciales (ChatGPT, Claude, Gemini y Llama).

---

## Arquitectura de despliegue

![Arquitectura PLS](pls_deployment_project/assets/pls_architecture.drawio.png)

- **Front-end (Angular + nginx)**: sirve la UI y proxy a `/api/` al servicio FastAPI.
- **API FastAPI (contenedor `api`)**: expone `/summarize` y `/classify`, delega generación al endpoint HF (MedGemma) o entra en `DRY_RUN` para casos de pruebas de integración sin el endpoint en HF, carga el clasificador TF-IDF+LogReg desde S3.
- **AlignScore service**: microservicio dedicado al cálculo de similitud factual (`/services/alignscore`), descarga su checkpoint desde S3.
- **Infraestructura**: imágenes `api/front/alignscore` se publican en ECR, Terraform + Makefile provisionan EC2 (t3.large) y despliegan el stack con Docker Compose.

---

## Uso del front-end (paso a paso)

UI Angular sencilla e intuitiva: todo se concentra en una única vista con formularios claros, resultados visibles sin recargar y paneles laterales para métricas e historial.

1) Pantalla inicial: vista limpia con navegación mínima y acceso directo para ingresar el texto que se desea generar PLS.
   ![Pantalla inicial](assets/front_start.png)

2) Ingreso de texto: área amplia para pegar el artículo técnico. Validaciones básicas evitan peticiones vacías o texto que ya son PLS.  
   ![Ingreso de texto](assets/user_input_text_section.png)

3) Resultado PLS: la salida aparece alineada con el texto de entrada para lectura rápida, botones permiten copiar o lanzar una nueva iteración.  
   ![Resultado PLS](assets/pls_result_section.png)

4) Métricas: panel compacto con legibilidad y AlignScore para validar la factualidad del nuevo texto generado con respecto al original, se muestran etiquetas y valores legibles para que un usuario no técnico interprete la calidad.  
   ![Métricas](assets/metrics_section.png)

5) Historial: lista cronológica de generaciones previas con fragmentos del input y output para auditoría y reutilización, se accede sin perder el estado actual.  
   ![Historial de PLS](assets/history_pls_generate_section.png)

---

## Equipo

- Monica Alejandra Alvarez Carrillo.
- Daniel Eduardo Ayala Ramírez.
- Manuela Alejandra Hernandez Otalora.
- Richard Stiv Murcia Huerfano.

---

## Referencias rápidas

- Clasificador: `notebooks/pls_classifier_baseline.ipynb`
- Generador (MedGemma): `notebooks/pls_sft_medgemma.ipynb`
- Generador (Qwen): `notebooks/pls_sft_qwen.ipynb`
- Despliegue: `pls_deployment_project/README.md`
