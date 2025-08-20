# TFM – Modelos de PLN para el Leonés

Este repositorio contiene el trabajo desarrollado en el marco del **Trabajo de Fin de Máster (TFM)** centrado en la recopilación, procesamiento y modelado de recursos lingüísticos en **llionés (leonés)**.  

El proyecto combina la **creación de datasets propios**, su limpieza y estructuración, junto con la **entrenación y evaluación de modelos de lenguaje** usando frameworks modernos en Google Colab.  

**Máster en Robótica e Inteligencia Artificial**

**Universidad de León**

---

## 📂 Estructura del repositorio

```
    ├── Dataset/ # Recursos creados para el proyecto
    │ ├── corpus/ # Corpus textual en llionés (textos literarios y académicos)
    │ └── dict-tr/ # Dataset de pares Input-Output (traducciones y diccionarios)
    │
    ├── Memoria/ # Proyecto Overleaf en LaTeX (documento principal del TFM)
    │
    ├── Notebooks/ # Google Colab notebooks
    │ ├── Training_Models.ipynb
    │ └── Testing_Models.ipynb
    │
    ├── Resultados/ # Resultados de evaluación de los modelos
    │ ├── Modelos Corpus/
    │ └── Modelos dict-tr/ # Incluye resultados de 9 modelos entrenados
    │
    └── README.md # Este archivo
```


---

## 📊 Datasets

El proyecto ha requerido la **construcción de datasets originales** a partir de múltiples fuentes.  

### 1. 📖 Corpus
Ubicado en `Dataset/corpus/`, incluye:
- Textos literarios, etnográficos y académicos en llionés.
- Procesados a partir de **PDFs**, **OCR** y **web scraping**.
- Organización en **chunks de texto plano** listos para su uso en modelado.

### 2. 🗂️ Dict-TR
Ubicado en `Dataset/dict-tr/`, contiene el dataset [`unileon-robotics/lliones-dict-tr`](https://huggingface.co/unileon-robotics/lliones-dict-tr).  

Este dataset recopila pares *Input-Output* con traducciones, significados y vocabulario leonés-español.  

#### Descripción del dataset
El dataset **Llionés - Base de Datos Lingüística** recopila y organiza información relacionada con el idioma leonés en formato Input-Output, incluyendo:
- Traducciones.
- Vocabulario.
- Significados.
- Diccionarios.

##### Recursos utilizados:
- `lliones-esp-tr`: Traducciones de la página de **L'alderique**.  
- `lliones-semantics-and-meanings`: Vocabulario e información de **L'alderique**.  
- `lliones-dict-cele`: Diccionario del Léxico Leonés Actual (LLA).  
- `lliones-dict-faceira`: Diccionario Llionés de Nicolás Bartolomé Pérez.  

##### Agradecimientos:
- **Grupo de Robótica ULE**  
- **Cátedra de Estudios Leoneses (CELE – Universidad de León)**  
- **Asociación Faceira**  
- **Asociación Furmientu**  
- **Asociación El Fueyu**  
- **Asociación L’alderique**  

---

## 🚀 Entrenamiento de modelos

Los modelos se han entrenado en **Google Colab** utilizando la librería [Unsloth](https://github.com/unslothai/unsloth).  

- **Dataset usado:** `dict-tr` (pares Input-Output).  
- **Modelos base:** Qwen2.5 en distintas configuraciones (0.5B, 1.5B, 3B).  
- **Épocas:** 1, 3 y 5.  
- **Técnicas:** Fine-tuning y evaluación en formato GGUF.  

Los **notebooks principales** se encuentran en la carpeta `Notebooks/`:
- `Training_Models.ipynb`: entrenamiento de los modelos.  
- `Testing_Models.ipynb`: evaluación y análisis.  

---

## 📈 Resultados

Los resultados de evaluación se encuentran en la carpeta `Resultados/`.  

- `Modelos dict-tr/`: incluye los experimentos con 9 modelos (Qwen2.5 en tamaños 0.5B, 1.5B y 3B; entrenados con 1, 3 y 5 épocas).  
- Cada modelo contiene sus métricas en formato `.csv` y `.json` (`lliones_eval_summary`).  
- Se incluyen distintas variantes de cuantización (F16 y Q5_K_M).  

---

## 📑 Memoria

En la carpeta `Memoria/` se encuentra el proyecto de **Overleaf (LaTeX)** para la redacción del documento académico del TFM.  
- Estructurado en capítulos (introducción, estado del arte, metodología, resultados y conclusiones).  
- En desarrollo para la entrega final.  

---

## 🛠️ Tecnologías utilizadas

- **Python** (procesamiento y limpieza de datos).  
- **PyMuPDF, PDFPlumber, Tesseract** (OCR y extracción de textos).  
- **BeautifulSoup / Scrapy** (web scraping).  
- **Unsloth + Google Colab** (entrenamiento de modelos).  
- **Hugging Face** (distribución de datasets y modelos).  
- **LaTeX (Overleaf)** (redacción de la memoria).  

---

## 📌 Autor

Julián Izquierdo García

Este trabajo forma parte del **Trabajo de Fin de Máster** en el área de **Procesamiento de Lenguaje Natural (PLN)** y tiene como objetivo contribuir a la preservación y digitalización del leonés mediante el uso de técnicas modernas de IA.  
