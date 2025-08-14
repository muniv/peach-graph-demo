# Neo4j 한국어 어휘 지식그래프 데모

이 프로젝트는 Neo4j를 사용하여 한국어 어휘 데이터의 지식그래프를 구축하고 시각화하는 데모입니다.

## 기능

- Neo4j 데이터베이스에 한국어 어휘 데이터 저장
- 어휘 간의 `EASIER_ALTERNATIVE` 관계 시각화
- 인터랙티브 그래프 탐색
- 노드 클릭 시 상세 정보 표시
- 난이도별 색상 구분

## 설치 및 실행

### 1. Neo4j 설치 및 실행

Neo4j Desktop을 다운로드하거나 Docker를 사용하여 Neo4j를 실행하세요:

```bash
# Docker를 사용하는 경우
docker run \
    --name neo4j \
    -p7474:7474 -p7687:7687 \
    -d \
    -v $HOME/neo4j/data:/data \
    -v $HOME/neo4j/logs:/logs \
    -v $HOME/neo4j/import:/var/lib/neo4j/import \
    -v $HOME/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/password \
    neo4j:latest
```

### 2. Python 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 애플리케이션 실행

```bash
python app.py
```

### 4. 브라우저에서 접속

http://localhost:5000 에 접속하여 데모를 확인하세요.

## 데이터 구조

### 노드 (LexicalItem)
- `label`: 어휘 표현
- `pos`: 품사
- `difficulty`: 난이도 (1-3)
- `domain`: 도메인 (배열)
- `gloss`: 정의

### 관계 (EASIER_ALTERNATIVE)
- `rank`: 대안의 순위

## 포함된 어휘 데이터

1. **침수사고** (재난 도메인)
   - 물에 잠기는 사고 → 물이 차서 생긴 사고

2. **조사단장** (행정 도메인)
   - 조사팀 책임자 → 조사 책임자

3. **~에도 불구하고** (문법 도메인)
   - 그런데도 → 그래도

4. **배수시설** (재난 도메인)
   - 물 빠지는 시설 → 물이 빠지게 하는 장치

## 사용법

1. **데이터베이스 설정**: "데이터베이스 설정" 버튼을 클릭하여 Neo4j에 데이터를 로드합니다.
2. **그래프 로드**: "그래프 로드" 버튼을 클릭하여 시각화를 시작합니다.
3. **노드 탐색**: 노드를 클릭하면 우측 패널에 상세 정보가 표시됩니다.
4. **드래그**: 노드를 드래그하여 그래프 레이아웃을 조정할 수 있습니다.

## 기술 스택

- **Backend**: Flask, Neo4j Python Driver
- **Frontend**: HTML, CSS, D3.js
- **Database**: Neo4j
- **Visualization**: D3.js Force-directed Graph
