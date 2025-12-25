# Simulador de Subestação

Aplicação Django para receber um diagrama unifilar em PDF de uma subestação de distribuição, interpretar suas chaves e permitir simulações de abertura/fechamento para visualizar barras energizadas.

> Observação: a extração do PDF é um placeholder. O backend gera uma topologia demonstrativa para testes enquanto a lógica de interpretação real não é implementada.

## Requisitos
- Python 3.11+
- Dependências listadas em `requirements.txt` (`pip install -r requirements.txt`)

## Como executar
1. Crie e ative um ambiente virtual (opcional, porém recomendado).
2. Instale as dependências: `pip install -r requirements.txt`.
3. Aplique migrações padrão do Django: `python manage.py migrate`.
4. Inicie o servidor: `python manage.py runserver 0.0.0.0:8000`.
5. Acesse `http://localhost:8000` e envie um PDF para iniciar a simulação.

## Fluxo do simulador
1. Envie um PDF do diagrama unifilar.
2. O backend cria uma topologia simulável (chaves e barras) e a grava na sessão do usuário.
3. Cada chave possui uma ação "Alternar" que abre ou fecha o circuito.
4. A lista de barras energizadas é recalculada sempre que uma chave muda de estado.

## Estrutura principal
- `manage.py`: utilitário de linha de comando do Django.
- `substation_site/`: configurações e roteamento do projeto.
- `simulator/`: app com formulário de upload, parser placeholder e interface de simulação.
