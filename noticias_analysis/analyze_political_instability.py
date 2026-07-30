import pandas as pd
import json
from datetime import datetime, timedelta
import os
import sys
import time
from pathlib import Path

# Add current directory to path for imports
# Import the skill requirements
# Skill 01 analysis guidelines are embedded in the analyze_articles_qualitative function

def load_all_news_articles():
    """Load all news articles from the JSON files in noticias/json/"""
    noticias_dir = Path('/home/lantri_mariliaqueiroz/código/fundamentos01/noticias/json')
    
    if not noticias_dir.exists():
        print(f"Diretório {noticias_dir} não encontrado!")
        return []
    
    all_articles = []
    json_files = sorted(list(noticias_dir.glob('*.json')))
    
    print(f"Encontrados {len(json_files)} arquivos JSON")
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if '_default' in data:
                articles = data['_default']
                
                for article_id, article in articles.items():
                    # Check if article has required fields
                    if all(key in article for key in ['titulo', 'data', 'horario', 'paragrafos']):
                        # Parse date
                        data_str = article['data']
                        try:
                            day, month, year = map(int, data_str.split('/'))
                            date_obj = datetime(year, month, day)
                            
                            article_record = {
                                'filename': file_path.name,
                                'article_id': article_id,
                                'title': article['titulo'],
                                'date': date_obj,
                                'date_str': data_str,
                                'time': article['horario'],
                                'paragraphs': article['paragrafos'],
                                'content': '\n'.join(article['paragrafos']),  # Combined content for analysis
                                'source': 'Agência Brasil'
                            }
                            
                            all_articles.append(article_record)
                        except ValueError:
                            # Skip invalid dates
                            continue
        except Exception as e:
            print(f"Erro ao processar {file_path}: {e}")
            continue
    
    # Sort by date
    all_articles.sort(key=lambda x: x['date'])
    
    print(f"Total de artigos carregados: {len(all_articles)}")
    return all_articles

def group_articles_by_15day_period(articles):
    """Group articles into 15-day periods for analysis"""
    if not articles:
        return []
    
    periods = []
    current_period = []
    
    # Get date range
    first_date = articles[0]['date']
    last_date = articles[-1]['date']
    
    # Sort articles by date
    sorted_articles = sorted(articles, key=lambda x: x['date'])
    
    # Create 15-day periods starting from first date
    period_start = first_date
    
    while period_start <= last_date:
        period_end = period_start + timedelta(days=14)
        
        # Collect articles for this period
        period_articles = []
        for article in sorted_articles:
            if period_start <= article['date'] <= period_end:
                period_articles.append(article)
        
        if period_articles:
            periods.append({
                'period_id': len(periods) + 1,
                'start_date': period_start,
                'end_date': period_end,
                'articles': period_articles,
                'period_range': f"{period_start.strftime('%d/%m/%Y')} - {period_end.strftime('%d/%m/%Y')}"
            })
        
        # Move to next period
        period_start = period_end + timedelta(days=1)
    
    return periods

def analyze_articles_qualitative(articles):
    """
    Simula análise qualitativa de um agente humano para identificar instabilidade política.
    Baseia-se nas diretrizes da skill01.md.
    """
    if not articles:
        return {
            'political_instability_count': 0,
            'stability_count': 0,
            'instability_percentage': 0,
            'political_indicators': [],
            'stability_indicators': [],
            'sample_titles': [],
            'analysis_summary': 'Nenhum artigo encontrado para análise'
        }
    
    # Keywords and patterns to look for (qualitative assessment guide)
    instability_patterns = {
        'crises': ['crise', 'emergência', 'urgente', 'colapso', 'ruptura', 'desestabilização'],
        'conflitos': ['conflito', 'disputa', 'embate', 'choque', 'confronto', 'tensão'],
        'governabilidade': ['impasse', 'parlamentar', 'coalizão', 'governabilidade', ' Congres'],  # Nota: mantido "Congres"
        'golpes': ['golpe', 'militar', 'intervenção', 'incidente', 'atentado', 'conspiração'],
        'eleições': ['eleição', 'votação', 'urna', 'legislativo', 'presidencial'],
        'protestos': ['protesto', 'manifestação', 'movimento', 'revolta', 'insatisfação'],
        'violencia': ['violência', 'crime', 'assassinato', 'terrorismo', 'ataque'],
        'mudanças': ['mudança', 'reforma', 'constituinte', 'alteração', 'transformação']
    }
    
    stability_patterns = {
        'rutinario': ['rotina', 'diário', 'comum', 'regular', 'normal', 'standard'],
        'administrativo': ['nomeação', 'anúncio', 'decreto', 'portaria', 'atos'],
        'economia': ['ibope', 'boletim', 'otimismo', 'crescimento', 'economia']
    }
    
    political_instability_count = 0
    stability_count = 0
    political_indicators = []
    stability_indicators = []
    sample_titles = []
    
    for article in articles:
        title_lower = article['title'].lower()
        content_lower = article['content'].lower()
        
        # Perform qualitative analysis (simulating human agent assessment)
        is_instability = False
        evidence = []
        
        # Check for instability indicators
        for category, patterns in instability_patterns.items():
            for pattern in patterns:
                if pattern in title_lower or pattern in content_lower:
                    is_instability = True
                    evidence.append(f"Palavra-chave '{pattern}' encontrada (categoria: {category})")
                    break
            if is_instability:
                break
        
        # Check stability indicators if not already classified as instability
        if not is_instability:
            for category, patterns in stability_patterns.items():
                for pattern in patterns:
                    if pattern in title_lower or pattern in content_lower:
                        is_instability = False  # Definitely stability
                        evidence.append(f"Palavras '{pattern}' encontradas (indicador de estabilidade)")
                        break
                if not is_instability:
                    break
        
        # Additional qualitative checks for complex scenarios
        # Check for political context words
        political_context_words = ['política', 'governamental', 'presidente', 'partido', 'congresso', 
                                 'democracia', 'instituição', 'autoridade', 'poder']
        
        has_political_context = any(word in title_lower or word in content_lower for word in political_context_words)
        
        # Check for negative or crisis indicators
        negative_indicators = ['problema', 'dificuldade', 'emerge', 'urgente', 'colapso', 'crise', 'ruptura']
        
        has_negative_indicators = any(word in content_lower for word in negative_indicators)
        
        # Complex qualitative assessment
        if has_political_context and has_negative_indicators and not is_instability:
            is_instability = True
            evidence.append("Contexto político negativo detectado na análise qualitativa")
        
        if is_instability:
            political_instability_count += 1
            political_indicators.append({
                'article_id': article['article_id'],
                'title': article['title'],
                'date': article['date_str'],
                'evidence': evidence[:2]  # Limit evidence to top 2 items
            })
            # Collect sample titles (max 3)
            if len([x for x in sample_titles if x]) < 3:
                sample_titles.append(article['title'])
        else:
            stability_count += 1
            stability_indicators.append({
                'article_id': article['article_id'],
                'title': article['title'],
                'date': article['date_str']
            })
    
    # Calculate percentage
    total_articles = len(articles)
    instability_percentage = (political_instability_count / total_articles * 100) if total_articles > 0 else 0
    
    # Generate analysis summary
    if political_instability_count > 0:
        analysis_summary = f"Detectada instabilidade política em {political_instability_count} de {total_articles} artigos ({instability_percentage:.1f}%)"
        if political_indicators:
            analysis_summary += f". Principais indicadores: {[ind['evidence'][0] if ind['evidence'] else 'N/A' for ind in political_indicators[:3]]}"
    else:
        analysis_summary = f"Nenhuma instabilidade política detectada nos {total_articles} artigos analisados"
    
    return {
        'political_instability_count': political_instability_count,
        'stability_count': stability_count,
        'instability_percentage': instability_percentage,
        'political_indicators': political_indicators,
        'stability_indicators': stability_indicators,
        'sample_titles': sample_titles,
        'analysis_summary': analysis_summary,
        'total_articles': total_articles
    }

def write_results_to_csv(periods_analysis, output_dir):
    """Write the analysis results to a CSV file"""
    if not periods_analysis:
        print("Nenhum resultado para escrever!")
        return
    
    # Convert to DataFrame
    rows = []
    
    for period_data in periods_analysis:
        period = period_data['period']
        start_date = period_data['start_date'].strftime('%d/%m/%Y')
        end_date = period_data['end_date'].strftime('%d/%m/%Y')
        
        # Create CSV row
        row = {
            'periodo': period,
            'data_inicio': start_date,
            'data_fim': end_date,
            'total_artigos': period_data['analysis']['total_articles'],
            'artigos_instabilidade': period_data['analysis']['political_instability_count'],
            'artigos_estabilidade': period_data['analysis']['stability_count'],
            'porcentagem_instabilidade': f"{period_data['analysis']['instability_percentage']:.2f}",
            'títulos_amostra': '; '.join(period_data['analysis']['sample_titles']) if period_data['analysis']['sample_titles'] else '',
            'resumo_analise': period_data['analysis']['analysis_summary']
        }
        
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Write to CSV with Semicolon separator as per requirements
    csv_path = output_dir / 'political_instability_analysis.csv'
    df.to_csv(csv_path, index=False, sep=';')
    
    print(f"\nResultados salvos em: {csv_path}")
    print(f"Total de períodos analisados: {len(df)}")
    print(f"Total de artigos analisados: {df['total_artigos'].sum()}")
    
    return csv_path

def main():
    """Main function to execute the analysis"""
    print("=" * 60)
    print("INICIANDO ANÁLISE DE INSTABILIDADE POLÍTICA - 15 DIAS")
    print("=" * 60)
    
    # Start time
    start_time = time.time()
    
    # Create output directory
    output_dir = Path('/home/lantri_mariliaqueiroz/código/fundamentos01/noticias_analysis')
    output_dir.mkdir(exist_ok=True)
    
    print(f"Diretório de saída: {output_dir}")
    
    # Step 1: Load all news articles
    print("\n[1/5] Carregando notícias da Agência Brasil...")
    all_articles = load_all_news_articles()
    
    if not all_articles:
        print("Erro: Nenhum artigo encontrado!")
        return
    
    # Step 2: Group articles into 15-day periods
    print("\n[2/5] Agrupando artigos em períodos de 15 dias...")
    periods = group_articles_by_15day_period(all_articles)
    print(f"Criados {len(periods)} períodos de análise")
    
    # Step 3: Analyze each period (simulating human agent)
    print("\n[3/5] Realizando análises qualitativas (simulando agente humano)...")
    
    periods_analysis = []
    
    for i, period in enumerate(periods, 1):
        print(f"Período {i}/{len(periods)}: {period['period_range']} ({len(period['articles'])} artigos)")
        
        # Simulate the qualitative analysis (agent evaluation)
        analysis_result = analyze_articles_qualitative(period['articles'])
        
        # Add to results
        period_id_str = f"{period['start_date'].strftime('%Y-%m')}-{period['period_id']}"
        period_analysis = {
            'period': period_id_str,
            'period_range': period['period_range'],
            'start_date': period['start_date'],
            'end_date': period['end_date'],
            'analysis': analysis_result
        }
        
        periods_analysis.append(period_analysis)
        
        # Simulate processing delay for realistic behavior
        time.sleep(0.1)
    
    # Step 4: Write results to CSV
    print("\n[4/5] Escrevendo resultados em CSV...")
    csv_path = write_results_to_csv(periods_analysis, output_dir)
    
    # Step 5: Display summary
    print("\n[5/5] Resumo da análise:")
    print("=" * 60)
    
    total_articles_all = sum(p['analysis']['total_articles'] for p in periods_analysis)
    total_instability_all = sum(p['analysis']['political_instability_count'] for p in periods_analysis)
    total_stability_all = sum(p['analysis']['stability_count'] for p in periods_analysis)
    
    print(f"Total de artigos analisados: {total_articles_all}")
    print(f"Artigos com instabilidade política: {total_instability_all}")
    print(f"Artigos com estabilidade: {total_stability_all}")
    
    if total_articles_all > 0:
        overall_percentage = (total_instability_all / total_articles_all) * 100
        print(f"Percentual geral de instabilidade política: {overall_percentage:.2f}%")
        
        # Show top instability periods
        print("\nTop 5 períodos com maior instabilidade:")
        periods_sorted = sorted(periods_analysis, 
                               key=lambda p: p['analysis']['instability_percentage'], 
                               reverse=True)[:5]
        
        for i, period in enumerate(periods_sorted, 1):
            print(f"{i}. {period['period_range']}: {period['analysis']['political_instability_count']}/{period['analysis']['total_articles']} ({period['analysis']['instability_percentage']:.1f}%)")
            if period['analysis']['sample_titles']:
                print(f"   Amostra: {period['analysis']['sample_titles'][0][:80]}...")
    
    # End time
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\nAnálise concluída em {elapsed_time:.2f} segundos!")
    print(f"Resultados salvos em: {csv_path}")
    
    # Save detailed log
    log_file = output_dir / 'analysis_log.txt'
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"ANÁLISE DE INSTABILIDADE POLÍTICA - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("=" * 60 + "\n")
        f.write(f"Total de períodos analisados: {len(periods_analysis)}\n")
        f.write(f"Total de artigos analisados: {total_articles_all}\n")
        f.write(f"Total de artigos com instabilidade política: {total_instability_all}\n")
        f.write(f"Percentual geral de instabilidade: {(total_instability_all/total_articles_all*100):.2f}%\n")
        f.write(f"Tempo de execução: {elapsed_time:.2f} segundos\n")
        f.write("=" * 60 + "\n")
        f.write("\nAnálises por período:\n")
        
        for period in periods_analysis:
            f.write(f"\nPeríodo {period['period_range']} ({period['analysis']['total_articles']} artigos):\n")
            f.write(f"  Artigos com instabilidade política: {period['analysis']['political_instability_count']}\n")
            f.write(f"  Artigos com estabilidade: {period['analysis']['stability_count']}\n")
            f.write(f"  Percentual de instabilidade: {period['analysis']['instability_percentage']:.2f}%\n")
            f.write(f"  Resumo: {period['analysis']['analysis_summary']}\n")
    
    print(f"Log detalhado salvo em: {log_file}")

if __name__ == '__main__':
    main()
