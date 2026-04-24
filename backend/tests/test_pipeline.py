from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_parse_jd_endpoint():
    payload = {
        'title': 'Senior AI Engineer',
        'description': 'Need Python, FastAPI, AWS and Docker. Nice to have React.',
    }
    response = client.post('/api/parse-jd', json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body['title'] == 'Senior AI Engineer'
    assert 'python' in body['required_skills']


def test_upload_csv_endpoint():
    csv_content = (
        'candidate_id,name,profile_text\n'
        'C1,Anya,Python and FastAPI engineer open to work\n'
        'C2,Rohan,Java backend engineer\n'
    )

    response = client.post(
        '/api/upload-csv',
        files={'file': ('candidates.csv', csv_content, 'text/csv')},
    )
    assert response.status_code == 200

    body = response.json()
    assert body['count'] == 2
    assert body['candidates'][0]['candidate_id'] == 'C1'


def test_run_pipeline_endpoint():
    payload = {
        'jd': {
            'title': 'Senior AI Engineer',
            'description': 'Need Python, FastAPI, LLM and AWS skills.',
        },
        'candidates': [
            {
                'candidate_id': 'C1',
                'name': 'Anya',
                'profile_text': 'Senior Python engineer with FastAPI, AWS and LLM. Open to work.',
            },
            {
                'candidate_id': 'C2',
                'name': 'Rohan',
                'profile_text': 'Java backend engineer with SQL. Happy in current role.',
            },
        ],
        'weights': {'match_weight': 0.6, 'interest_weight': 0.4},
        'top_k': 2,
    }

    response = client.post('/api/run-pipeline', json=payload)
    assert response.status_code == 200

    body = response.json()
    shortlist = body['shortlist']

    assert len(shortlist) == 2
    assert shortlist[0]['final_score'] >= shortlist[1]['final_score']

    for candidate in shortlist:
        assert 0 <= candidate['match_score'] <= 100
        assert 0 <= candidate['interest_score'] <= 100
        assert 0 <= candidate['final_score'] <= 100
