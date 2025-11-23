# Data Folder — README

Este directorio concentra los datasets usados para entrenar, validar, probar y evaluar modelos de Plain Language Summarization (PLS) aplicados a textos biomédicos.

---

## Origen de los Datos

Los archivos `.csv` incluidos en este directorio fueron obtenidos a partir de los datos utilizados en la investigación:

**“Bridging the Gap in Health Literacy: Harnessing the Power of Large Language Models to Generate Plain Language Summaries from Biomedical Texts”**  
Autores: Felipe Arias-Russi, Carolina Salazar-Lara, Rubén Manrique.

Fuentes oficiales:
- GitHub (Data Sources del paper): https://github.com/feliperussi/bridging-the-gap-in-health-literacy/tree/main/data_collection_and_processing/Data%20Sources
- Publicación ACL Anthology: https://aclanthology.org/2025.cl4health-1.23/

---

## Archivos Incluidos

- `df_train.csv` — 3276 filas, columnas: `technical_text`, `plain_summary`, `source`
- `df_validation.csv` — 365 filas, columnas: `technical_text`, `plain_summary`, `source`
- `df_test.csv` — 221 filas, columnas: `technical_text`, `plain_summary`, `source`
- `evaluation_texts.csv` — 100 filas, columnas: `technical_text`, `reference_summary`

Uso en el proyecto:

| Archivo                 | Uso                    |
|-------------------------|------------------------|
| `df_train.csv`          | Entrenamiento          |
| `df_validation.csv`     | Validación             |
| `df_test.csv`           | Evaluación final       |
| `evaluation_texts.csv`  | Evaluación comparativa |

---

## Estadísticas a considerar

- **Longitudes de texto (caracteres, P99 / máximo)**  
  - `df_train.csv`: `technical_text` 7313.75 / 28992; `plain_summary` 5474.0 / 8934  
  - `df_validation.csv`: `technical_text` 8341.16 / 21422; `plain_summary` 5561.52 / 8157  
  - `df_test.csv`: `technical_text` 7056.8 / 17895; `plain_summary` 5507.8 / 6006  
  - `evaluation_texts.csv`: `technical_text` 7044.16 / 7060; `reference_summary` 5588.9 / 5678  
  - **Agregado (train+val+test)**: `technical_text` P99 7326.24 (máx. 28992); `plain_summary` P99 5504.58 (máx. 8934)  
  > Cálculo: longitud de caracteres (incluye espacios y saltos de línea). Útil para fijar `max_seq_length` en fine-tuning.

- **Distribución de `source` (train/val/test)**  
  - `df_train.csv`: 3219 `Cochrane`, 57 `Pfizer/ClinicalTrials`  
  - `df_validation.csv`: 359 `Cochrane`, 6 `Pfizer/ClinicalTrials`  
  - `df_test.csv`: 218 `Cochrane`, 3 `Pfizer/ClinicalTrials`

---

## Métricas evaluadas en los experimentos del proyecto

1) **Relevancia semántica**: BERTScore (F1)  
2) **Factualidad**: AlignScore  
3) **Legibilidad**: Flesch–Kincaid Grade Level, Coleman–Liau Index, Flesch Reading Ease, Gunning Fog Index, SMOG, Dale–Chall.

---

## Ejemplos (3 por archivo)

### `df_train.csv`

| technical_text | plain_summary | source |
|:---------------|:--------------|:-------|
| Background<br>Proliferative diabetic retinopathy (PDR) is a complication of diabetic retinopathy that can cause blindness. Although panretinal photocoagulation (PRP) is the treatment of choice for PDR, it has secondary effects that can affect vision. An alternative treatment such as anti‐vascular endothelial growth factor (anti‐VEGF), which produces an inhibition of vascular proliferation, could improve the vision of people with PDR. | Injections of anti‐vascular endothelial growth factor for advanced diabetic retinopathy<br>Review question  Do injections of anti‐vascular endothelial growth factor (anti‐VEGF) help people with advanced diabetic retinopathy in terms of vision and progression of the disease? Is this treatment safe? | Cochrane |
| Background<br>Pain during dental treatment, which is a common fear of patients, can be controlled successfully by local anaesthetic. Several different local anaesthetic formulations and techniques are available. | Injectable local anaesthetic agents for preventing pain in participants requiring dental treatment<br>Review question  This review assessed the evidence for providing successful local anaesthesia that provides pain control during dental treatment. | Cochrane |
| Background<br>This is an update of a Cochrane Review first published in The Cochrane Library in Issue 12, 2010.  Tinnitus is described as the perception of sound or noise in the absence of real acoustic stimulation. | Sound therapy (masking) in the management of tinnitus in adults<br>Tinnitus can be described as a perception of sound that is not related to an external acoustic source. Subjective tinnitus is not heard by other people and causes significant distress in approximately 1% to 3% of all people. | Cochrane |

### `df_validation.csv`

| technical_text | plain_summary | source |
|:---------------|:--------------|:-------|
| Background<br>After a 1999 National Cancer Institute (NCI) clinical alert was issued, chemoradiotherapy has become widely used in treating women with cervical cancer. Two subsequent systematic reviews found consistent, significant survival benefits for chemoradiotherapy compared to conventional radiotherapy. | Chemoradiotherapy for cervical cancer:  results of a meta‐analysis<br>Women with cervical cancer that is too big to be removed by surgery, or has spread to the tissues around the cervix (often called locally advanced cervical cancer) may be treated with radiation (radiotherapy). | Cochrane |
| Background<br>Both peripheral arterial thrombolysis and surgery can be used in the management of peripheral arterial ischaemia. Much is known about the indications, risks, and benefits of thrombolysis. However, there is less agreement about the relative benefits of thrombolysis and surgery. | Surgery versus thrombolysis for the initial management of acute limb ischaemia<br>Background  Thrombolysis involves dissolving a blood clot by injecting a chemical agent at the site of the clot. | Cochrane |
| Background<br>Stroke survivors are often physically inactive as well as sedentary,and may sit for long periods of time each day. This increases cardiometabolic risk and has impacts on physical and other aspects of health. | Interventions to reduce sedentary behaviour after stroke<br>Review questionWe reviewed the evidence that examines the effects of treatments to reduce the amount of sedentary behaviour in people after stroke. | Cochrane |

### `df_test.csv`

| technical_text | plain_summary | source |
|:---------------|:--------------|:-------|
| Background<br>In order to overcome the low effectiveness of assisted reproductive technologies (ART) and the high incidence of multiple births, metabolomics is proposed as a non‐invasive method to assess embryo viability. | Metabolomics for improving pregnancy outcomes<br>Review question  Cochrane researchers reviewed the evidence about the effectiveness of metabolomics as an evaluation tool to improve the rates of ongoing pregnancy and live birth in women undergoing IVF and ICSI, the most widely used ART. | Cochrane |
| Background<br>Onychomycosis refers to fungal infections of the nail apparatus that may cause pain, discomfort, and disfigurement. This is an update of a Cochrane Review published in 2007; a substantial amount of new literature has been published since then. | Are topical and device‐based treatments effective in people with fungal infections of the toenails?<br>Review question  We reviewed evidence about the effect of topical and device‐based treatments for fungal toenail infections. | Cochrane |
| Background<br>Morita therapy was founded in 1919 by Shoma Morita (1874‐1938). The therapy involves a behavioural structured program to encourage an outward perspective on life and increased social functioning, and aims to redirect attention away from symptoms. | Morita therapy for schizophrenia<br>Schizophrenia is a long‐term, chronic illness with a high disability rate and disease burden. Treatment for schizophrenia should focus on the wider social aspects of life. | Cochrane |

### `evaluation_texts.csv`

| technical_text | reference_summary |
|:---------------|:------------------|
| Background<br>Lumbar spinal stenosis with neurogenic claudication is one of the most commonly diagnosed and treated pathological spinal conditions. It frequently afflicts the elderly population.  Objectives  To examine if non‐surgical treatment is effective for neurogenic claudication associated with lumbar spinal stenosis and to evaluate the incidence of adverse events associated with these treatments. | Non‐surgical treatment for spinal stenosis with leg pain<br>Review question  We reviewed the evidence on the effectiveness of non‐surgical treatments for people with leg pain caused by pressure on the nerves in the lower back. |
| Background<br>Older patients with multiple health problems (multi‐morbidity) value being involved in decision‐making about their health care. However, they are less frequently involved than younger patients, although chronic conditions are more common in older people. | Interventions for involving older patients with more than one long‐term health problem in decision‐making during primary care consultations<br>Background  The number of older people with more than one long‐term health problem (multi‐morbid patients) is increasing, and can be expected to continue to increase. |
| Background<br>Beta‐blockers are an essential part of standard therapy in adult congestive heart failure and therefore, are expected to be beneficial in children. However, congestive heart failure in children is not a single condition but rather a collection of different types of heart failure. | Beta‐blockers for children with congestive heart failure<br>Background  The term congestive heart failure describes a disorder in which the heart is unable to sufficiently and efficiently pump blood through the body. |

---

## Licenciamiento y ética

Uso exclusivamente académico, de investigación y desarrollo experimental, siguiendo las licencias del repositorio oficial.
