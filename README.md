# Pipeline de Dados de Precipitação

## Funcionalidades
1. Gera dados horários simulados para **todas as capitais brasileiras**.
2. Transforma em acumulados diários seguindo a regra das **12h UTC**.
3. Salva em CSV e banco de dados SQLite (por complementaridade e redundância controlada, escolhi salvar em ambos os formatos).
4. Totalmente conteinerizado com Docker.

## Como Executar
```bash
# Construir a imagem
docker build -t tria-etl .

# Executar com datas personalizadas (exemplo)
docker run -v $(pwd)/saida:/app/saida tria-etl --start 2023-05-01 --end 2023-05-07
