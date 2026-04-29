# Classificação do Alfabeto de Libras com CNN

Projeto de reconhecimento de sinais estáticos do alfabeto da Língua Brasileira de Sinais (Libras) utilizando Redes Neurais Convolucionais com o framework Keras.

**Notebook no Google Colab:** [Abrir no Colab](https://colab.research.google.com/drive/1ArGJ1N5HavdpQGHtP8VYkQ66ZdkoekEy#scrollTo=nsAsf1VhJT-4)

---

## 1. Dataset

### Fonte
**Sign Language MNIST**  
Disponível em: [kaggle.com/datasets/datamunge/sign-language-mnist](https://www.kaggle.com/datasets/datamunge/sign-language-mnist)  

### Descrição
O dataset é uma adaptação do MNIST clássico para reconhecimento de linguagem de sinais. Cada amostra representa uma letra estática do alfabeto americano de sinais (ASL), cujas letras estáticas têm representação equivalente ao alfabeto de Libras.

### Classificações
O dataset contém **24 classes** — as letras J e Z são omitidas por exigirem movimento para serem representadas, não podendo ser capturadas em imagens estáticas.

| Índice | Letra | Índice | Letra |
|--------|-------|--------|-------|
| 0 | A | 13 | N |
| 1 | B | 14 | O |
| 2 | C | 15 | P |
| 3 | D | 16 | Q |
| 4 | E | 17 | R |
| 5 | F | 18 | S |
| 6 | G | 19 | T |
| 7 | H | 20 | U |
| 8 | I | 21 | V |
| 10 | K | 22 | W |
| 11 | L | 23 | X |
| 12 | M | 24 | Y |

### Configuração das imagens
- **Tamanho:** 28 × 28 pixels
- **Canais:** 1 (escala de cinza)
- **Formato original:** CSV (cada linha = 1 label + 784 valores de pixel)
- **Fundo:** homogêneo, claro
- **Estilo:** palma da mão voltada para a câmera, centralizada no frame

### Divisão do dataset
| Conjunto | Quantidade |
|----------|-----------|
| Treino   | ~27.455 imagens |
| Validação (10% do treino) | ~2.745 imagens |
| Teste    | ~7.172 imagens |
| **Total** | **~34.627 imagens** |

### Tratamento de dados
- Leitura dos CSVs com `pandas`
- Reshape de vetor `(784,)` para matriz `(28, 28, 1)`
- Normalização dos pixels de `[0, 255]` para `[0.0, 1.0]`
- Conversão dos labels para formato one-hot com `keras.utils.to_categorical`

---

## 2. Treinamento do Modelo

### Arquitetura da rede

Foi utilizada uma CNN construída com Keras Sequential, com 3 blocos convolucionais seguidos de camadas densas:

```
Input (28, 28, 1)
│
├── Conv2D(32, 3x3, relu, padding=same)
├── BatchNormalization
├── MaxPooling2D(2x2)
│
├── Conv2D(64, 3x3, relu, padding=same)
├── BatchNormalization
├── MaxPooling2D(2x2)
│
├── Conv2D(128, 3x3, relu, padding=same)
├── BatchNormalization
├── MaxPooling2D(2x2)
│
├── Flatten
├── Dense(256, relu)
├── Dropout(0.5)
└── Dense(25, softmax)   ← 25 saídas (labels 0–24)
```

### Hiperparâmetros

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| Otimizador | Adam | Adaptativo, converge rápido |
| Loss | categorical_crossentropy | Padrão para classificação multiclasse |
| Batch size | 128 | Equilíbrio entre velocidade e estabilidade |
| Épocas | 20 | Curvas estabilizaram antes da época 5 |
| Dropout | 0.5 | Reduz overfitting desativando 50% dos neurônios |
| Learning rate | automático via ReduceLROnPlateau | Reduz à metade se val_accuracy não melhorar em 3 épocas |

### Data Augmentation

Aplicado via `ImageDataGenerator` no conjunto de treino para aumentar a diversidade dos dados:

```python
ImageDataGenerator(
    rotation_range=10,
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True,
)
```

### Callbacks utilizados

**ModelCheckpoint:** salva automaticamente o modelo com melhor `val_accuracy` durante o treino.

```python
ModelCheckpoint('melhor_modelo.keras', monitor='val_accuracy', save_best_only=True)
```

**ReduceLROnPlateau:** reduz o learning rate pela metade se a `val_accuracy` não melhorar por 3 épocas consecutivas.

```python
ReduceLROnPlateau(monitor='val_accuracy', patience=3, factor=0.5)
```

### Como o modelo é salvo

O melhor modelo é salvo automaticamente no arquivo `melhor_modelo.keras` durante o treino. Ao final, os pesos são recarregados com:

```python
model.load_weights('melhor_modelo.keras')
```

---

## 3. Avaliação do Modelo

### Resultados

| Métrica | Valor |
|---------|-------|
| Test loss | 0.1491 |
| Test accuracy | **95,47%** |

### Análise das curvas de treino

- O modelo convergiu nas primeiras 2–3 épocas, atingindo ~99% de acurácia no treino
- As curvas de treino e validação acompanham de perto durante todo o treinamento, indicando **ausência de overfitting**
- A loss caiu de ~3.5 para próximo de 0 nas primeiras épocas e se manteve estável

### Separação para avaliação

- 10% do conjunto de treino foi separado como validação (`validation_split=0.1`) para monitorar o treinamento em tempo real
- O conjunto de teste (`sign_mnist_test.csv`) foi mantido completamente separado e usado apenas na avaliação final

---

## 4. Uso do Modelo

### Classificação de uma nova imagem

```python
img = cv2.imread('minha_foto.png', cv2.IMREAD_GRAYSCALE)
img = cv2.resize(img, (28, 28))
img_norm = img.astype('float32') / 255.0
img_input = img_norm.reshape(1, 28, 28, 1)

probs = model.predict(img_input)
idx = np.argmax(probs)
```

### Retorno ao usuário

```python
print(f'Letra prevista : {LETRAS[idx]}')
print(f'Confiança      : {probs[0][idx]*100:.1f}%')
```

O modelo retorna a letra com maior probabilidade (`np.argmax`) e o percentual de confiança. A tradução do índice numérico para a letra é feita via dicionário:

```python
LETRAS = {
    0:'A', 1:'B', 2:'C', 3:'D', 4:'E', 5:'F', 6:'G', 7:'H', 8:'I',
    10:'K', 11:'L', 12:'M', 13:'N', 14:'O', 15:'P', 16:'Q', 17:'R',
    18:'S', 19:'T', 20:'U', 21:'V', 22:'W', 23:'X', 24:'Y'
}
```

## 5. Testes do Modelo

### Teste contra o dataset de teste

```python
loss, acc = model.evaluate(x_test, y_test, verbose=0)
print(f'Test loss: {loss:.4f} | Test accuracy: {acc:.4f}')
```

**Resultado:** 95,47% de acurácia em 7.172 imagens nunca vistas pelo modelo.

### Teste unitário com imagem externa

```python
# Upload de imagem própria
uploaded = files.upload()
nome_arquivo = list(uploaded.keys())[0]

img = cv2.imread(nome_arquivo, cv2.IMREAD_GRAYSCALE)
img = cv2.resize(img, (28, 28))
img_input = img.astype('float32') / 255.0
img_input = img_input.reshape(1, 28, 28, 1)

probs = model.predict(img_input)
idx = np.argmax(probs)
print(f'Letra prevista: {LETRAS[idx]} | Confiança: {probs[0][idx]*100:.1f}%')
```

### Observações sobre testes com imagens externas

O modelo apresenta melhor desempenho quando as imagens externas respeitam as mesmas condições do dataset de treino (fundo claro, mão centralizada, vista frontal). Imagens com fundo escuro, mão de perfil ou baixa iluminação reduzem significativamente a confiança da predição, o que é esperado dado que o modelo foi treinado com um dataset de condições controladas.

---

## Configuração da API do Kaggle

Para baixar o dataset automaticamente no Colab é necessário ter uma conta no Kaggle e gerar um token de API. Siga os passos abaixo:

**1. Gerar o token**

1. Acesse [kaggle.com](https://www.kaggle.com) e faça login
2. Clique na sua foto de perfil → **Settings**
3. Role até a seção **API**
4. Clique em **Create new token**
5. Um arquivo `kaggle.json` será baixado — guarde-o

O token gerado tem o formato `KGAT_xxxxxxxxxxxxxxxxxxxx`.

**2. Configurar no Colab via Secrets (recomendado)**

Os Secrets do Colab ficam salvos entre sessões e não aparecem no código.

1. No Colab, clique no ícone de 🔑 chave no menu lateral esquerdo
2. Clique em **Add new secret**
3. Nome: `KAGGLE_TOKEN`
4. Valor: cole o token gerado (ex: `KGAT_xxxxxxxxxxxxxxxxxxxx`)
5. Ative o toggle **Notebook access**

No código, o token é lido assim:

```python
from google.colab import userdata
import os

os.environ["KAGGLE_TOKEN"] = userdata.get("KAGGLE_TOKEN")
```

**3. Baixar e extrair o dataset**

```python
!kaggle datasets download -d datamunge/sign-language-mnist
!unzip -q sign-language-mnist.zip -d sign-language-mnist/
```