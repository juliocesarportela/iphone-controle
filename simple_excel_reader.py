import pandas as pd

def simple_excel_analysis():
    """Análise simples e robusta da planilha Excel"""
    
    try:
        # Lê a planilha
        df = pd.read_excel("Modelo_Custos_EUA_PY_GSheets.xlsx", sheet_name='CUSTOS')
        
        print("ANÁLISE DA PLANILHA EXCEL")
        print("=" * 50)
        
        print(f"\nDimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
        
        print(f"\nColunas encontradas:")
        for i, col in enumerate(df.columns):
            print(f"{i+1:2d}. {col}")
        
        print(f"\nPrimeiras 3 linhas:")
        print(df.head(3).to_string())
        
        print(f"\nTipos de dados:")
        for col in df.columns:
            print(f"{col}: {df[col].dtype}")
        
        print(f"\nValores únicos em campos categóricos:")
        
        # Modelos
        if 'MODELO' in df.columns:
            print(f"\nModelos: {df['MODELO'].unique()}")
        
        # Capacidades
        if 'GB' in df.columns:
            print(f"Capacidades: {df['GB'].unique()}")
        
        # Grades
        if 'GRADE' in df.columns:
            print(f"Grades: {df['GRADE'].unique()}")
        
        # Valores fixos
        campos_fixos = ['TAXA ADM $', 'FRETE EUA $', 'POL EUA $', 'Câmbio USDT']
        for campo in campos_fixos:
            if campo in df.columns:
                valores = df[campo].unique()
                print(f"{campo}: {valores}")
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    simple_excel_analysis()
