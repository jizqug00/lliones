# 📄 README — Resultados con `lliones-corpus` (comparativa breve con `lliones-dict-tr`)

> **Ubicación:** `Resultados/` (experimentos con **lliones-corpus**).

## 🧠 Descripción breve
- **`lliones-corpus`**: texto **no estructurado** en llionés, preparado como **texto plano** y **dividido en *chunks*** para preentrenamiento/continual pretraining.
- **`lliones-dict-tr`**: texto **estructurado** con **pares entrada–salida** (formato *input–output* para chatbots), adecuado para **entrenamiento supervisado** y **evaluación**.

## 🧪 Resultado de los experimentos con `lliones-corpus`
**No se ha podido entrenar ningún modelo** a partir de `lliones-corpus`.

**Motivos principales:**
- **Escasez de datos no estructurados**: para aprender relaciones desde texto crudo se requiere **muchísimo más volumen** que en datasets con señal supervisada.
- **Señal de entrenamiento débil**: al no haber pares (instrucciones/respuestas), el aprendizaje es menos eficiente y **no se observaron mejoras estables**.
- **Sin *benchmark* específico** en llionés: no hay forma rigurosa de **medir** avances sobre este corpus en el marco del TFM.

## 🔁 Comparativa (texto estructurado vs. no estructurado)

| Aspecto | `lliones-dict-tr` (estructurado) | `lliones-corpus` (no estructurado) |
|---|---|---|
| Tipo de datos | Pares **entrada–salida** (supervisado) | **Texto plano** sin anotaciones |
| Señal de aprendizaje | **Fuerte** (objetivos claros) | **Débil** (descubrimiento de patrones) |
| Volumen necesario | **Moderado** | **Alto** (órdenes de magnitud mayor) |
| Evaluación | **Sí** (*benchmark* con Q–A) | **No** (*benchmark* inexistente) |
| Resultados en este TFM | **Buenos y medibles** | **Sin modelos entrenados** |

## ✅ Notas sobre `lliones-dict-tr`
Con `lliones-dict-tr` **sí se han obtenido buenos resultados**: el entrenamiento **supervisado** con pares pregunta–respuesta y la existencia de un **benchmark** permitieron **entrenar y evaluar** modelos de forma objetiva (métricas disponibles en los correspondientes `.csv`/`.json`).

## 📈 Métricas para `lliones-corpus`
No se alcanzó una fase de entrenamiento evaluable → **no hay resultados cuantitativos** ni informes de validación para este dataset.

## 🧾 Conclusión
En este TFM, **`lliones-corpus`** no ha producido modelos entrenados debido al **bajo volumen** y la **naturaleza no estructurada** del texto, junto con la **ausencia de un *benchmark***. En contraste, **`lliones-dict-tr`** sí ha dado **buenos resultados** gracias a su **formato supervisado** y a la **evaluación** disponible.
