import pandas as pd
from datetime import datetime, timedelta
import random
import sqlite3
import argparse
import logging
from typing import List

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Lista de todas as capitais brasileiras
CAPITAIS: List[str] = [
    'Rio Branco', 'Maceió', 'Macapá', 'Manaus', 'Salvador', 'Fortaleza',
    'Brasília', 'Vitória', 'Goiânia', 'São Luís', 'Cuiabá', 'Campo Grande',
    'Belo Horizonte', 'Belém', 'João Pessoa', 'Curitiba', 'Recife', 'Teresina',
    'Rio de Janeiro', 'Natal', 'Porto Alegre', 'Porto Velho', 'Boa Vista',
    'Florianópolis', 'São Paulo', 'Aracaju', 'Palmas'
]


def gerar_dados_horarios(data_inicio: str, data_fim: str) -> pd.DataFrame:
    """
    Gera dados horários simulados para todas as capitais brasileiras.

    Args:
        data_inicio (str): Data inicial no formato 'YYYY-MM-DD'.
        data_fim (str): Data final no formato 'YYYY-MM-DD'.

    Returns:
        pd.DataFrame: Dados com colunas [data_hora_utc, cidade, precipitacao_mm].
    """
    try:
        # Gerar datas horárias em UTC
        datas = pd.date_range(start=data_inicio, end=data_fim, freq='H', tz='UTC')

        # Gerar dados para todas as capitais
        dados = []
        for data_hora in datas:
            for cidade in CAPITAIS:
                precipitacao = round(random.uniform(0, 15), 1)  # Valores entre 0 e 15 mm
                dados.append({
                    'data_hora_utc': data_hora,
                    'cidade': cidade,
                    'precipitacao_mm': precipitacao
                })

        df = pd.DataFrame(dados)
        logging.info(f"Dados gerados: {len(df)} registros.")
        return df

    except Exception as e:
        logging.error(f"Falha na geração de dados: {e}")
        raise


def transformar_diario(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforma dados horários em acumulados diários (regra das 12h UTC).

    Regra:
        - Acumulação diária começa às 12h UTC de um dia e termina às 11:59 UTC do dia seguinte.
        Exemplo: 2023-01-01 12:00 UTC → 2023-01-02 11:59 UTC → Dia 2023-01-02.
    """
    try:
        # Ajustar a data diária conforme a regra das 12h UTC
        df['data_diaria'] = df['data_hora_utc'].apply(
            lambda x: x.date() + timedelta(days=1) if x.hour >= 12 else x.date()
        )

        # Agrupar e somar
        df_diario = df.groupby(['data_diaria', 'cidade'], as_index=False)['precipitacao_mm'].sum()
        logging.info(f"Dados diários processados: {len(df_diario)} registros.")
        return df_diario

    except Exception as e:
        logging.error(f"Falha na transformação: {e}")
        raise


def salvar_dados(df: pd.DataFrame, caminho_saida: str) -> None:
    """
    Salva os dados em CSV e SQLite.

    Args:
        df (pd.DataFrame): Dados processados.
        caminho_saida (str): Pasta de saída.
    """
    try:
        # Salvar CSV
        df.to_csv(f'{caminho_saida}/precipitacao_diaria.csv', index=False, encoding='utf-8-sig')

        # Salvar SQLite
        conn = sqlite3.connect(f'{caminho_saida}/precipitacao.db')
        df.to_sql('precipitacao', conn, if_exists='replace', index=False)
        conn.close()

        logging.info(f"Dados salvos em {caminho_saida}.")

    except Exception as e:
        logging.error(f"Falha ao salvar dados: {e}")
        raise


if __name__ == "__main__":
    # Configurar argumentos
    parser = argparse.ArgumentParser(description='ETL de dados de precipitação')
    parser.add_argument('--start', type=str, required=True, help='Data de início (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, required=True, help='Data de fim (YYYY-MM-DD)')
    args = parser.parse_args()

    # Validar datas
    try:
        start_date = datetime.strptime(args.start, '%Y-%m-%d')
        end_date = datetime.strptime(args.end, '%Y-%m-%d')
        if start_date > end_date:
            raise ValueError("Data de início deve ser anterior à data final.")
    except ValueError as e:
        logging.error(f"Data inválida: {e}")
        exit(1)

    # Executar pipeline
    try:
        dados_horarios = gerar_dados_horarios(args.start, args.end)
        dados_diarios = transformar_diario(dados_horarios)
        salvar_dados(dados_diarios, './saida')
    except Exception as e:
        logging.error(f"Falha no pipeline: {e}")
        exit(1)