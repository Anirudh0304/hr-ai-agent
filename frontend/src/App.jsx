import { useMemo, useState } from 'react';
import Papa from 'papaparse';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function parseCsvToCandidates(csvText) {
  const parsed = Papa.parse(csvText, {
    header: true,
    skipEmptyLines: true,
    transformHeader: (h) => h.trim(),
  });

  if (parsed.errors.length) {
    throw new Error(`CSV parse error: ${parsed.errors[0].message}`);
  }

  const headers = parsed.meta.fields || [];
  const required = ['candidate_id', 'name', 'profile_text'];
  const hasRequiredHeaders = required.every((h) => headers.includes(h));

  if (!hasRequiredHeaders) {
    throw new Error('CSV must include candidate_id, name, profile_text columns.');
  }

  return parsed.data.map((row) => {
    return {
      candidate_id: String(row.candidate_id || '').trim(),
      name: String(row.name || '').trim(),
      profile_text: String(row.profile_text || '').trim(),
    };
  }).filter((c) => c.candidate_id && c.name && c.profile_text);
}

export default function App() {
  const [jdTitle, setJdTitle] = useState('Senior AI Engineer');
  const [jdDescription, setJdDescription] = useState(
    'We need a Senior AI Engineer with Python, FastAPI, LLM and AWS experience. Nice to have: React and Docker.'
  );
  const [csvText, setCsvText] = useState(
    'candidate_id,name,profile_text\nC1,Anya,Senior Python engineer with FastAPI and AWS background. Open to work and excited for high ownership roles.\nC2,Rohan,Backend engineer skilled in Java and SQL. Happy in current role.\nC3,Maya,ML engineer with LLM, Docker and cloud deployment experience. Interested in career growth.'
  );

  const [topK, setTopK] = useState(5);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const candidateCount = useMemo(() => {
    try {
      return parseCsvToCandidates(csvText).length;
    } catch {
      return 0;
    }
  }, [csvText]);

  const handleFileUpload = async (evt) => {
    const file = evt.target.files?.[0];
    if (!file) return;
    const text = await file.text();
    setCsvText(text);
  };

  const runPipeline = async () => {
    setIsRunning(true);
    setError('');

    try {
      const candidates = parseCsvToCandidates(csvText);
      const payload = {
        jd: {
          title: jdTitle,
          description: jdDescription,
        },
        candidates,
        weights: {
          match_weight: 0.6,
          interest_weight: 0.4,
        },
        top_k: Number(topK),
      };

      const res = await fetch(`${API_BASE}/api/run-pipeline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const body = await res.json();
        throw new Error(body.detail || 'Pipeline request failed.');
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'Unexpected error while running pipeline.');
      setResult(null);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="page">
      <div className="ambient ambient-a" />
      <div className="ambient ambient-b" />

      <header className="hero">
        <p className="eyebrow">AI Talent Intelligence</p>
        <h1>Talent Scouting & Engagement Agent</h1>
        <p>
          Submit a JD, upload candidates, and get a recruiter-ready shortlist ranked by
          Match Score and Interest Score.
        </p>
      </header>

      <main className="grid">
        <section className="card">
          <h2>Job Description</h2>
          <label>Role Title</label>
          <input value={jdTitle} onChange={(e) => setJdTitle(e.target.value)} />

          <label>Description</label>
          <textarea value={jdDescription} onChange={(e) => setJdDescription(e.target.value)} rows={7} />

          <div className="row">
            <div>
              <label>Top K</label>
              <input
                type="number"
                min={1}
                max={100}
                value={topK}
                onChange={(e) => setTopK(e.target.value)}
              />
            </div>
            <button onClick={runPipeline} disabled={isRunning}>
              {isRunning ? 'Running Pipeline...' : 'Run Pipeline'}
            </button>
          </div>
          {error && <p className="error">{error}</p>}
        </section>

        <section className="card">
          <h2>Candidate Data</h2>
          <label>Upload CSV</label>
          <input type="file" accept=".csv" onChange={handleFileUpload} />
          <p className="hint">Columns required: candidate_id, name, profile_text</p>

          <label>CSV Preview / Edit</label>
          <textarea value={csvText} onChange={(e) => setCsvText(e.target.value)} rows={13} />
          <p className="hint">Detected candidates: {candidateCount}</p>
        </section>
      </main>

      <section className="card results">
        <h2>Ranked Shortlist</h2>
        {!result && <p className="hint">Run the pipeline to see ranked candidates.</p>}

        {result && (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Candidate</th>
                  <th>Match Score</th>
                  <th>Interest Score</th>
                  <th>Final Score</th>
                  <th>Matched Skills</th>
                  <th>Missing Skills</th>
                  <th>Engagement Summary</th>
                </tr>
              </thead>
              <tbody>
                {result.shortlist.map((c) => (
                  <tr key={c.candidate_id}>
                    <td>
                      <strong>{c.name}</strong>
                      <span className="mono">{c.candidate_id}</span>
                    </td>
                    <td>{c.match_score}</td>
                    <td>{c.interest_score}</td>
                    <td>{c.final_score}</td>
                    <td>{(c.match_reason?.matched_skills || []).join(', ') || 'None'}</td>
                    <td>{(c.match_reason?.missing_skills || []).join(', ') || 'None'}</td>
                    <td>{c.engagement_summary}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
