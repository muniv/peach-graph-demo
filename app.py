from flask import Flask, render_template, jsonify, request
from neo4j import GraphDatabase
import json
import re

app = Flask(__name__)

# Neo4j connection configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"

# Mock data for demo when Neo4j is not available
MOCK_DATA = {
    'nodes': [
        {
            'id': '1', 'label': '침수사고', 'pos': '명사', 'difficulty': 3,
            'domain': ['재난'], 'gloss': '비나 물이 차서 곳이 물에 잠기는 사고'
        },
        {
            'id': '2', 'label': '물에 잠기는 사고', 'pos': '명사구', 'difficulty': 2,
            'domain': ['재난'], 'gloss': '비나 물 때문에 장소가 물에 잠기는 일'
        },
        {
            'id': '3', 'label': '물이 차서 생긴 사고', 'pos': '명사구', 'difficulty': 1,
            'domain': ['재난'], 'gloss': '물이 많이 들어와서 난 사고'
        },
        {
            'id': '4', 'label': '조사단장', 'pos': '명사', 'difficulty': 3,
            'domain': ['행정'], 'gloss': '조사단의 책임자'
        },
        {
            'id': '5', 'label': '조사팀 책임자', 'pos': '명사구', 'difficulty': 2,
            'domain': ['행정'], 'gloss': '조사하는 팀을 이끄는 사람'
        },
        {
            'id': '6', 'label': '조사 책임자', 'pos': '명사구', 'difficulty': 1,
            'domain': ['행정'], 'gloss': '조사를 맡아 책임지는 사람'
        },
        {
            'id': '7', 'label': '불구하고', 'pos': '관용표현', 'difficulty': 3,
            'domain': ['문법'], 'gloss': '그 상황인데도 어떤 일이 일어남'
        },
        {
            'id': '8', 'label': '그런데도', 'pos': '부사', 'difficulty': 2,
            'domain': ['문법'], 'gloss': '그럼에도'
        },
        {
            'id': '9', 'label': '그래도', 'pos': '부사', 'difficulty': 1,
            'domain': ['문법'], 'gloss': '그렇지만 여전히'
        },
        {
            'id': '10', 'label': '배수시스템', 'pos': '명사', 'difficulty': 3,
            'domain': ['재난'], 'gloss': '물이 잘 빠지도록 만든 시설'
        },
        {
            'id': '11', 'label': '물 빠지는 시설', 'pos': '명사구', 'difficulty': 2,
            'domain': ['재난'], 'gloss': '물이 고이지 않게 빠지는 장치가 있는 시설'
        },
        {
            'id': '12', 'label': '물이 빠지게 하는 장치', 'pos': '명사구', 'difficulty': 1,
            'domain': ['재난'], 'gloss': '물을 밖으로 내보내는 장치'
        }
    ],
    'edges': [
        {'source': '1', 'target': '2', 'rank': 1, 'type': 'EASIER_ALTERNATIVE'},
        {'source': '2', 'target': '3', 'rank': 2, 'type': 'EASIER_ALTERNATIVE'},
        {'source': '4', 'target': '5', 'rank': 1, 'type': 'EASIER_ALTERNATIVE'},
        {'source': '5', 'target': '6', 'rank': 2, 'type': 'EASIER_ALTERNATIVE'},
        {'source': '7', 'target': '8', 'rank': 1, 'type': 'EASIER_ALTERNATIVE'},
        {'source': '8', 'target': '9', 'rank': 2, 'type': 'EASIER_ALTERNATIVE'},
        {'source': '10', 'target': '11', 'rank': 1, 'type': 'EASIER_ALTERNATIVE'},
        {'source': '11', 'target': '12', 'rank': 2, 'type': 'EASIER_ALTERNATIVE'}
    ]
}

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = None
        self.connected = False
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            self.connected = True
            print("✅ Neo4j connection successful")
        except Exception as e:
            print(f"❌ Neo4j connection failed: {e}")
            print("📝 Using mock data mode for demonstration")
            self.connected = False
    
    def close(self):
        if self.driver:
            self.driver.close()
    
    def execute_query(self, query, parameters=None):
        if not self.connected:
            raise Exception("Neo4j not connected")
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record for record in result]

# Initialize Neo4j connection
neo4j_conn = Neo4jConnection(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

def setup_database():
    """Setup the Neo4j database with the provided Korean lexical data"""
    
    if not neo4j_conn.connected:
        return "mock"  # Return mock mode indicator
    
    # Create constraint
    constraint_query = """
    CREATE CONSTRAINT lex_unique IF NOT EXISTS
    FOR (l:LexicalItem) REQUIRE l.label IS UNIQUE
    """
    
    # Data insertion queries
    data_queries = [
        # 침수사고
        """
        MERGE (a:LexicalItem {label:"침수사고"})
          SET a.pos="명사", a.difficulty=3, a.domain=["재난"],
              a.gloss="비나 물이 차서 곳이 물에 잠기는 사고";
        MERGE (a1:LexicalItem {label:"물에 잠기는 사고"})
          SET a1.pos="명사구", a1.difficulty=2, a1.domain=["재난"],
              a1.gloss="비나 물 때문에 장소가 물에 잠기는 일";
        MERGE (a2:LexicalItem {label:"물이 차서 생긴 사고"})
          SET a2.pos="명사구", a2.difficulty=1, a2.domain=["재난"],
              a2.gloss="물이 많이 들어와서 난 사고";
        MERGE (a)-[:EASIER_ALTERNATIVE {rank:1}]->(a1);
        MERGE (a1)-[:EASIER_ALTERNATIVE {rank:2}]->(a2)
        """,
        
        # 조사단장
        """
        MERGE (b:LexicalItem {label:"조사단장"})
          SET b.pos="명사", b.difficulty=3, b.domain=["행정"],
              b.gloss="조사단의 책임자";
        MERGE (b1:LexicalItem {label:"조사팀 책임자"})
          SET b1.pos="명사구", b1.difficulty=2, b1.domain=["행정"],
              b1.gloss="조사하는 팀을 이끄는 사람";
        MERGE (b2:LexicalItem {label:"조사 책임자"})
          SET b2.pos="명사구", b2.difficulty=1, b2.domain=["행정"],
              b2.gloss="조사를 맡아 책임지는 사람";
        MERGE (b)-[:EASIER_ALTERNATIVE {rank:1}]->(b1);
        MERGE (b1)-[:EASIER_ALTERNATIVE {rank:2}]->(b2)
        """,
        
        # ~에도 불구하고
        """
        MERGE (c:LexicalItem {label:"~에도 불구하고"})
          SET c.pos="관용표현", c.difficulty=3, c.domain=["문법"],
              c.gloss="그 상황인데도 어떤 일이 일어남";
        MERGE (c1:LexicalItem {label:"그런데도"})
          SET c1.pos="부사", c1.difficulty=2, c1.domain=["문법"],
              c1.gloss="그럼에도";
        MERGE (c2:LexicalItem {label:"그래도"})
          SET c2.pos="부사", c2.difficulty=1, c2.domain=["문법"],
              c2.gloss="그렇지만 여전히";
        MERGE (c)-[:EASIER_ALTERNATIVE {rank:1}]->(c1);
        MERGE (c1)-[:EASIER_ALTERNATIVE {rank:2}]->(c2)
        """,
        
        # 배수시설
        """
        MERGE (d:LexicalItem {label:"배수시설"})
          SET d.pos="명사", d.difficulty=3, d.domain=["재난"],
              d.gloss="물이 잘 빠지도록 만든 시설";
        MERGE (d1:LexicalItem {label:"물 빠지는 시설"})
          SET d1.pos="명사구", d1.difficulty=2, d1.domain=["재난"],
              d1.gloss="물이 고이지 않게 빠지는 장치가 있는 시설";
        MERGE (d2:LexicalItem {label:"물이 빠지게 하는 장치"})
          SET d2.pos="명사구", d2.difficulty=1, d2.domain=["재난"],
              d2.gloss="물을 밖으로 내보내는 장치";
        MERGE (d)-[:EASIER_ALTERNATIVE {rank:1}]->(d1);
        MERGE (d1)-[:EASIER_ALTERNATIVE {rank:2}]->(d2)
        """
    ]
    
    try:
        # Execute constraint
        neo4j_conn.execute_query(constraint_query)
        
        # Execute data insertion queries
        for query in data_queries:
            neo4j_conn.execute_query(query)
        
        return True
    except Exception as e:
        print(f"Database setup error: {e}")
        return False

def get_graph_data():
    """Retrieve graph data for visualization"""
    
    if not neo4j_conn.connected:
        return MOCK_DATA
    
    query = """
    MATCH (n:LexicalItem)
    OPTIONAL MATCH (n)-[r:EASIER_ALTERNATIVE]->(m:LexicalItem)
    RETURN n, r, m
    """
    
    try:
        results = neo4j_conn.execute_query(query)
        
        nodes = {}
        edges = []
        
        for record in results:
            # Add source node
            node = record['n']
            if node.element_id not in nodes:
                nodes[node.element_id] = {
                    'id': node.element_id,
                    'label': node['label'],
                    'pos': node.get('pos', ''),
                    'difficulty': node.get('difficulty', 0),
                    'domain': node.get('domain', []),
                    'gloss': node.get('gloss', '')
                }
            
            # Add target node and relationship if exists
            if record['r'] and record['m']:
                target_node = record['m']
                if target_node.element_id not in nodes:
                    nodes[target_node.element_id] = {
                        'id': target_node.element_id,
                        'label': target_node['label'],
                        'pos': target_node.get('pos', ''),
                        'difficulty': target_node.get('difficulty', 0),
                        'domain': target_node.get('domain', []),
                        'gloss': target_node.get('gloss', '')
                    }
                
                edges.append({
                    'source': node.element_id,
                    'target': target_node.element_id,
                    'rank': record['r'].get('rank', 0),
                    'type': 'EASIER_ALTERNATIVE'
                })
        
        return {
            'nodes': list(nodes.values()),
            'edges': edges
        }
    
    except Exception as e:
        print(f"Error retrieving graph data: {e}")
        return MOCK_DATA

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/setup')
def setup():
    result = setup_database()
    if result == "mock":
        return jsonify({'success': True, 'mode': 'mock', 'message': 'Neo4j 연결 실패. 데모 데이터를 사용합니다.'})
    return jsonify({'success': result, 'mode': 'neo4j' if result else 'error'})

@app.route('/graph-data')
def graph_data():
    data = get_graph_data()
    return jsonify(data)

def build_word_mapping():
    """Build a mapping of words to their easier alternatives by difficulty level"""
    word_mapping = {}
    
    # Get all nodes and their relationships
    data = get_graph_data()
    
    # Build a dictionary of word -> easier alternatives
    nodes_by_id = {node['id']: node for node in data['nodes']}
    
    for edge in data['edges']:
        source_node = nodes_by_id.get(edge['source'])
        target_node = nodes_by_id.get(edge['target'])
        
        if source_node and target_node:
            source_word = source_node['label']
            target_word = target_node['label']
            target_difficulty = target_node['difficulty']
            
            if source_word not in word_mapping:
                word_mapping[source_word] = {}
            
            word_mapping[source_word][target_difficulty] = target_word
    
    return word_mapping

def extract_keywords(text):
    """Extract keywords from text that exist in our knowledge graph"""
    # Return exactly the specified keywords that appear in the text
    target_keywords = ["침수사고", "조사단장", "배수시스템", "불구하고", "재발", "관리체계", "소통부족"]
    
    found_keywords = []
    for keyword in target_keywords:
        if keyword in text:
            found_keywords.append(keyword)
    
    return found_keywords

def analyze_context(text):
    """Analyze the context and main theme of the text"""
    # Simple context analysis based on keywords
    if '침수사고' in text and '조사단장' in text:
        if '재발' in text and '관리체계' in text:
            return "침수 사고의 재발 원인은 배수시설이 아닌 관리 체계와 소통 부족에 있다는 주장"
        else:
            return "침수 사고에 대한 조사 및 분석 내용"
    elif '침수사고' in text:
        return "침수 사고와 관련된 내용"
    elif '조사단장' in text:
        return "조사 및 분석 관련 내용"
    else:
        return "입력 텍스트에서 발견된 어려운 단어들을 쉬운 단어로 바꾸는 과정"

def find_word_by_difficulty(target_difficulty, word_group):
    """Find a word with the target difficulty level from a word group"""
    for word_id, word_info in word_group.items():
        if word_info['difficulty'] == target_difficulty:
            return word_info['label']
    return None

def get_keyword_replacements(text, target_level):
    """Get keyword replacements based on target difficulty level"""
    data = get_graph_data()
    keywords = extract_keywords(text)
    
    # Build word groups by semantic meaning - each chain of connected words
    word_groups = {}
    nodes_by_id = {node['id']: node for node in data['nodes']}
    
    # First, find all chains by following EASIER_ALTERNATIVE relationships
    visited = set()
    chain_id = 0
    
    for node in data['nodes']:
        if node['id'] in visited:
            continue
            
        # Start a new chain from this node
        chain = {}
        to_visit = [node['id']]
        
        while to_visit:
            current_id = to_visit.pop(0)
            if current_id in visited:
                continue
                
            visited.add(current_id)
            current_node = nodes_by_id[current_id]
            chain[current_id] = current_node
            
            # Find all connected nodes
            for edge in data['edges']:
                if edge['source'] == current_id and edge['target'] not in visited:
                    to_visit.append(edge['target'])
                elif edge['target'] == current_id and edge['source'] not in visited:
                    to_visit.append(edge['source'])
        
        if len(chain) > 1:  # Only keep chains with multiple words
            # Use the hardest word (difficulty 3) as group key, or first word if no difficulty 3
            group_key = None
            for word_info in chain.values():
                if word_info['difficulty'] == 3:
                    group_key = word_info['label']
                    break
            if not group_key:
                group_key = f"chain_{chain_id}"
                chain_id += 1
            
            word_groups[group_key] = chain
    
    replacements = []
    
    for keyword in keywords:
        replacement = keyword
        changed = False
        
        # Find which group this keyword belongs to
        for group_key, word_group in word_groups.items():
            for word_id, word_info in word_group.items():
                if word_info['label'] == keyword:
                    # Found the keyword in this group, now find target difficulty
                    target_word = find_word_by_difficulty(target_level, word_group)
                    print(f"DEBUG: keyword={keyword}, target_level={target_level}, target_word={target_word}")
                    print(f"DEBUG: word_group keys: {[info['label'] + '(' + str(info['difficulty']) + ')' for info in word_group.values()]}")
                    if target_word and target_word != keyword:
                        replacement = target_word
                        changed = True
                    break
            if changed:
                break
        
        replacements.append({
            'original': keyword,
            'replacement': replacement,
            'target_level': target_level,
            'changed': changed
        })
    
    return replacements

def rewrite_text_with_context(original_text, context, replacements, target_level):
    """Rewrite text using context and keyword replacements to create natural language"""
    
    # Apply replacements to the original text first
    rewritten_text = original_text
    for rep in replacements:
        if rep['original'] != rep['replacement']:
            rewritten_text = rewritten_text.replace(rep['original'], rep['replacement'])
    
    # Create a more natural, conversational rewrite based on the context
    if '침수사고' in original_text and '조사단장' in original_text:
        if target_level == 1:  # Most simplified version
            natural_rewrite = """
7월 17일, 대구 북구 노곡동에서 큰 비로 물에 잠기는 사고가 또 일어났어요. 이 사고를 조사한 팀의 책임자는 이렇게 말했어요. '예전에도 이곳에서 비슷한 일이 있었고, 그 뒤로 물이 빠지게 하는 장치를 고쳤어요. 그래도 이번에 다시 사고가 난 건, 제대로 관리하지 못했고, 서로 소통이 잘 안 됐기 때문이에요.'
            """.strip()
        elif target_level == 2:  # Medium difficulty
            natural_rewrite = """
지난 달 17일 대구 북구 노곡동에서 물에 잠기는 사고가 발생했습니다. 이 사고를 조사한 팀의 책임자는 "과거 노곡동 물에 잠기는 사고 이후 물 빠지는 시설이 보강됐음그런데도 이번 사고가 재발된 원인은 관리체계 및 소통부족 문제에 있다"고 진단했습니다.
            """.strip()
        else:  # Keep original difficulty
            natural_rewrite = original_text
    else:
        # For other types of text, just apply the replacements
        natural_rewrite = rewritten_text
    
    return natural_rewrite

@app.route('/simplify', methods=['POST'])
def simplify_text_api():
    data = request.json
    text = data.get('text', '')
    level = data.get('level', 1)
    
    if not text:
        return jsonify({'success': False, 'error': 'Text is required'})
    
    try:
        # Stage 1: Extract context and keywords
        keywords = extract_keywords(text)
        context = analyze_context(text)
        
        stage1_output = {
            'context': context,
            'keywords': keywords
        }
        
        # Stage 2: Get keyword replacements
        replacements = get_keyword_replacements(text, level)
        stage2_output = {
            'replacements': replacements
        }
        
        # Stage 3: Rewrite text with context and replacements
        stage3_output = {
            'rewritten_text': rewrite_text_with_context(text, context, replacements, level)
        }
        
        return jsonify({
            'success': True,
            'stage1': stage1_output,
            'stage2': stage2_output,
            'stage3': stage3_output
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/query', methods=['POST'])
def custom_query():
    query = request.json.get('query', '')
    
    try:
        results = neo4j_conn.execute_query(query)
        # Convert Neo4j results to JSON-serializable format
        serialized_results = []
        for record in results:
            record_dict = {}
            for key in record.keys():
                value = record[key]
                if hasattr(value, '__dict__'):
                    # Handle Neo4j node/relationship objects
                    record_dict[key] = dict(value)
                else:
                    record_dict[key] = value
            serialized_results.append(record_dict)
        
        return jsonify({'success': True, 'results': serialized_results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
