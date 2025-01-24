## Lyrics Classifier

Este projeto criar e orquestrar um pipeline de Machine Learning Operations (MLOps) para treinar, avaliar e implantar um modelo de classificação de letras de músicas em português por gênero musical. O projeto contém um processo de ETL (Extract, Transform, Load) para coletar, preparar e armazenar dados em uma Feature Store, um script de treinamento de modelo de Machine Learning com avaliação de métricas e um script de implantação de modelo em uma API REST.

## Planejamento

As visões, ideais, propósitos e aspectos gerais de planejamento e desenvolvimento do projeto foram dispostas em modelo de MLOps Infrastructure Stack Canvas para melhor visualização dos requisitos. A versão atual do documento pode ser acessada [aqui](ML-Canva.pdf).

## Workflow

### ETL (Extract, Transform, Load)

O passo inicial do projeto é a coleta, transformação e armazenamento dos dados de treinamento. O pipeline de ETL foi implementado em scripts Python que serão orquestrados e automatizados utilizando Github Actions. As três etapas de ETL serão executadas da seguinte forma:

- [**Extract:**](etl/extract.py) os dados são raspados dos sites de origem (Letras.mus.br e Vagalume.com.br) com auxílio das bibliotecas `requests` e `BeautifulSoup4` e são armazenados de forma desestruturada em arquivos JSON.

- [**Transform:**:](etl/transform.py) os dados de todas as fontes são concatenados em um único DataFrame e categorizados quanto à sua origem. Devido a paralelização da extração de dados, uma mesma música pode ser extraída de ambas as fontes e integrar o dataset de forma duplicada. Por conta disso, um ID é associado à cada ponto de dado para servir como chave primária no Data Lake.

- [**Load:**](etl/load.py) o DataFrame gerado é então enviado para uma Feature Store do HopsWorks em formato de FeatureGroup, e é identificado quanto à data de extração. Por conta disso, o versionamento dos dados servirá como evolução das tendências musicais ao longo do tempo, o que pode ser aproveitado para decisões de negócio futuras.

### Model Training

O [script de treinamento](train.py) contém os passos necessários para obter os dados do Data Lake, criar um modelo de Regressão Logística, treiná-lo e avaliá-lo em um conjunto de testes. As métricas de avaliação são salvas em arquivos e, posteriormente, enviadas por email aos integrantes da equipe. Todo o processo de automação do treinamento é orquestrado com o auxílio do Github Actions.

### Hyperparameter Tuning

O tuning de hiperparâmetros é feito com Sweeps do Weights & Biases. O script de treinamento contém as instruções necessárias para realização da busca e recuperação do melhor modelo encontrado para posterior implantação.

### Model Deploy

O deploy do modelo é feito serializando a Pipeline Scikit-Learn que contém o pré-processamento, extração de características e modelo pré-treinado e posteriormente carregando para uso no servidor. O modelo é implantado em um Space do HuggingFace e uma demo está disponível para acesso público.

### Model Versioning & Monitoring

[WORK IN PROGRESS]
