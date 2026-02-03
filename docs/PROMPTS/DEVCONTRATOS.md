Aja como um Desenvolvedor Full Stack Sênior especialista em Automação de Processos.



Vamos construir uma aplicação web para \*\*Gestão e Geração de Contratos\*\*. Eu tenho dois arquivos essenciais no projeto:

1\. `bacenmodelo.docx`: O modelo de texto do contrato com as cláusulas e placeholders.

2\. `Base-estrutural.pdf`: O layout institucional (cabeçalho/rodapé) que deve ser aplicado como fundo em todas as páginas.



\*\*O Fluxo da Aplicação (Baseado nos meus requisitos visuais):\*\*



A aplicação deve ter um fluxo de navegação lateral ou por etapas, construída preferencialmente em \*\*Streamlit\*\* (para prototipagem rápida e robusta em Python):



\*\*TELA 1: Cadastro de Dados (Referência: "Input de Dados")\*\*

\- Crie um formulário para input dos dados variáveis que alimentarão o contrato.

\- Campos necessários (baseados no modelo BACEN):

&nbsp; - Nome do Cliente / Razão Social

&nbsp; - CNPJ/CPF

&nbsp; - Endereço Completo (Cidade, Estado)

&nbsp; - Valor do Contrato (R$)

&nbsp; - Data do Contrato

\- \*\*Lógica:\*\* Esses dados devem ser armazenados na sessão (Session State) para serem usados em qualquer modelo selecionado posteriormente.



\*\*TELA 2: Biblioteca de Modelos (Referência: "Seleção de Módulo")\*\*

\- Exiba uma grade ou lista de contratos disponíveis.

\- \*\*Item Obrigatório:\*\* Um card/botão para o "Contrato BACEN".

\- O sistema deve ser escalável para eu adicionar outros modelos (ex: "Contrato LGPD", "Contrato Prestação de Serviços") no futuro apenas adicionando novos arquivos .docx.

\- \*\*Ação:\*\* Ao clicar em "Gerar Contrato BACEN", o sistema deve disparar a `ContractEngine`.



\*\*O Motor de Processamento (Backend):\*\*

Você deve implementar uma classe `ContractEngine` robusta que execute os seguintes passos quando o botão for clicado:

1\. \*\*Mapeamento:\*\* Pegar os dados da Tela 1 e mapear para as tags do `bacenmodelo.docx`. (Assuma que o docx usa tags Jinja2 como `{{ nome\_cliente }}`).

2\. \*\*Renderização:\*\* Usar `docxtpl` para preencher o DOCX.

3\. \*\*Conversão Fiel:\*\* Converter o DOCX preenchido para PDF usando `LibreOffice` (headless) via subprocess. \*\*Isso é crítico para manter a formatação das cláusulas.\*\*

4\. \*\*Aplicação do Layout:\*\* Usar `pypdf` para pegar o PDF gerado (que tem o texto) e sobrepor ao `Base-estrutural.pdf` (que tem o design/timbre). O resultado deve ser um híbrido perfeito.

5\. \*\*Download:\*\* Oferecer o botão para baixar o PDF finalizado.



\*\*Requisitos Técnicos \& Infra:\*\*

\- Crie o arquivo `app.py` (Frontend Streamlit).

\- Crie o arquivo `engine.py` (Lógica de processamento).

\- Crie um `Dockerfile` que instale Python 3.11, `libreoffice`, `default-jre` e as fontes necessárias.

\- Crie o `requirements.txt`.



\*\*Instrução Imediata:\*\*

Analise o `bacenmodelo.docx` e o `Base-estrutural.pdf` que estão no diretório. Implemente o código completo focando na integração entre a tela de input e a geração do arquivo final do módulo BACEN.

