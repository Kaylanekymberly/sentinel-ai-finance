def analisar_texto(self, texto):
    """Analisa o sentimento de um texto"""
    # Tokenizar e analisar
    inputs = self.tokenizer(texto, return_tensors="pt", truncation=True, max_length=512)
    
    with torch.no_grad():
        outputs = self.model(**inputs)
    
    # Obter probabilidades
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    scores = {
        'negative': probs[0][0].item(),
        'neutral': probs[0][1].item(),
        'positive': probs[0][2].item()
    }
    
    # APLICAR BIAS: Reduzir o score neutro em 20% para forçar classificação
    scores_ajustados = {
        'negative': scores['negative'],
        'neutral': scores['neutral'] * 0.80,  # Penaliza neutro
        'positive': scores['positive']
    }
    
    # Escolher o maior score AJUSTADO
    sentimento_final = max(scores_ajustados, key=scores_ajustados.get)
    
    # Mapear para português
    mapa = {
        'positive': 'positivo',
        'negative': 'negativo',
        'neutral': 'neutro'
    }
    
    sentimento_pt = mapa[sentimento_final]
    
    return {
        'sentimento': sentimento_pt,
        'confianca': round(scores[sentimento_final] * 100, 1),  # Usa score original
        'score_positivo': scores['positive'],
        'score_negativo': scores['negative'],
        'score_neutro': scores['neutral']
    }