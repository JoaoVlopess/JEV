
from dotenv import load_dotenv
from typesafe_sdk import TypeSafeClient, Choice

load_dotenv()


def classificar(client, contexto, instrucao, opcoes):
    resultado = client.system_one(
        state=contexto,
        questions={
            "classificacao": Choice(
                instructions=instrucao,
                criteria={opcao: None for opcao in opcoes},
            )
        },
    )
    return resultado.answers["classificacao"]


# Simulação da transcrição de um áudio enviado pelo WhatsApp pelo engenheiro na obra
transcricao_audio = """
E aí pessoal do financeiro, acabei de liberar a medição do empreiteiro da alvenaria, 
o seu Carlos. Deu R$ 4.500 pela etapa do bloco B. 
"""

with TypeSafeClient() as client:
    macro_res = classificar(
        client=client,
        contexto=transcricao_audio,
        instrucao="Qual é o objetivo principal desta nota de voz enviada pelo engenheiro de obra?",
        opcoes=[
            "pagamento_despesa",       
            "recebimento_receita",     
            "relatorio_progresso",     # Atualização de avanço físico
            "alerta_seguranca_risco",  
            "outro_assunto"           
        ]
    )

    print(f"[MACRO] Categoria: {macro_res.choice} | Confiança: {macro_res.confidence:.2%}")

    # Trava de segurança: Se a IA não tiver 80% de certeza sobre a intenção do áudio,
    # interrompe o fluxo e pede para o usuário regravar de forma mais objetiva e direcionada
    if macro_res.confidence < 0.80 or macro_res.choice == "outro_assunto":
        print("⚠️ Confiança baixa ou assunto ambíguo. Roteando para validação humana.")
        exit()


    # ROTA A: PAGAMENTOS E DESPESAS DE OBRA
    if macro_res.choice == "pagamento_despesa":
        micro_res = classificar(
            client=client,
            contexto=transcricao_audio,
            instrucao="Qual é o centro de custo/categoria exata deste pagamento?",
            opcoes=[
                "mao_de_obra_empreiteiro",     
                "material_construcao_bruto",  
                "aluguel_maquinario_equip",    
                "alimentacao_transporte_equipe",
                "taxas_licencas_cartorio"
            ]
        )
        
        print(f"[MICRO - Pagamento] Subcategoria: {micro_res.choice} ({micro_res.confidence:.2%})")
        
        # Ação de Integração com o ERP / Financeiro
        if micro_res.choice == "mao_de_obra_empreiteiro" and micro_res.confidence >= 0.85:
            # Chama a API do ERP para criar um lançamento no Contas a Pagar
            print(" Criado título em 'Contas a Pagar' -> Fila de Aprovação da Medição.")
        else:
            print(" Lançado como rascunho de despesa para checagem da nota fiscal.")


    # ROTA B: RECEBIMENTOS E APORTES DA OBRA
    elif macro_res.choice == "recebimento_receita":
        micro_res = classificar(
            client=client,
            contexto=transcricao_audio,
            instrucao="Qual é a origem deste recebimento financeiro?",
            opcoes=[
                "medicao_cliente_contratante",  
                "aporte_investidor_socio",      
                "venda_sucata_sobra_material",  
                "estorno_devolucao_fornecedor"
            ]
        )
        
        print(f"[MICRO - Recebimento] Subcategoria: {micro_res.choice} ({micro_res.confidence:.2%})")
        
        # Ação de Integração
        print(f"Lançado crédito em 'Contas a Receber' sob a rubrica {micro_res.choice}.")


    # ROTA C: SEGURANÇA E FISCALIZAÇÃO DA OBRA
    elif macro_res.choice == "alerta_seguranca_risco":
        micro_res = classificar(
            client=client,
            contexto=transcricao_audio,
            instrucao="Qual é a gravidade do problema de segurança reportado?",
            opcoes=[
                "risco_grave_paralisa_obra",  # Falta de EPI em altura, risco de desabamento
                "ocorrencia_leve_advertencia", # Falta de organização de material
                "incidente_com_vitima"
            ]
        )
        
        print(f"[MICRO - Segurança] Nível: {micro_res.choice} ({micro_res.confidence:.2%})")
        
        if micro_res.choice in ["risco_grave_paralisa_obra", "incidente_com_vitima"]:
            print(" Disparado SMS/WhatsApp de emergência para o Engenheiro Chefe e TST.")


    # ROTA D: AVANÇO FÍSICO / DIÁRIO DE OBRA
    elif macro_res.choice == "relatorio_progresso":
        # Aqui o código pode rotear para o Diário de Obra digital
        print("Transcrição registrada automaticamente no Diário de Obra de Hoje.")
