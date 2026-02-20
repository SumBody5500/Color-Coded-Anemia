import React, { useState } from 'react';
import './App.css';

function App() {
  const [eyeFile, setEyeFile] = useState(null);
  const [tongueFile, setTongueFile] = useState(null);
  const [nailFile, setNailFile] = useState(null);
  const [preview, setPreview] = useState({ eye: null, tongue: null, nail: null });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const backendUrl = 'http://localhost:5000';

  const handleFileChange = (event, type) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!['image/jpeg', 'image/png', 'image/jpg'].includes(file.type)) {
      setError('Please upload only JPG or PNG images.');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('File size should be less than 10MB.');
      return;
    }

    setError('');

    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(prev => ({ ...prev, [type]: reader.result }));
    };
    reader.readAsDataURL(file);

    if (type === 'eye') setEyeFile(file);
    if (type === 'tongue') setTongueFile(file);
    if (type === 'nail') setNailFile(file);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setResult(null);

    if (!eyeFile || !tongueFile || !nailFile) {
      setError('Please upload all three images: eye, tongue, and fingernail.');
      return;
    }

    const formData = new FormData();
    formData.append('eye', eyeFile);
    formData.append('tongue', tongueFile);
    formData.append('nail', nailFile);

    try {
      setLoading(true);
      const response = await fetch(`${backendUrl}/api/analyze`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.error || 'Failed to analyze images.');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error('Error during analysis:', err);
      setError(err.message || 'An error occurred while analyzing images.');
    } finally {
      setLoading(false);
    }
  };

  const renderScoreBar = (score) => {
    const percentage = Math.min(Math.max(score, 0), 100);
    let color = '#4caf50';
    if (percentage >= 75) color = '#d32f2f';
    else if (percentage >= 50) color = '#f57c00';
    else if (percentage >= 30) color = '#fbc02d';

    return (
      <div className="score-bar">
        <div
          className="score-bar-inner"
          style={{ width: `${percentage}%`, backgroundColor: color }}
        />
      </div>
    );
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Anemia Risk Detector</h1>
        <p>Upload clear images of your eye, tongue, and fingernail to screen for anemia risk.</p>
      </header>

      <main className="app-main">
        <form className="upload-form" onSubmit={handleSubmit}>
          <div className="upload-grid">
            <div className="upload-card">
              <h2>Eye (Conjunctiva)</h2>
              <p>Pull down your lower eyelid and capture the inner red area.</p>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => handleFileChange(e, 'eye')}
              />
              {preview.eye && (
                <img src={preview.eye} alt="Eye preview" className="preview-image" />
              )}
            </div>

            <div className="upload-card">
              <h2>Tongue</h2>
              <p>Stick out your tongue in good lighting and capture the full surface.</p>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => handleFileChange(e, 'tongue')}
              />
              {preview.tongue && (
                <img src={preview.tongue} alt="Tongue preview" className="preview-image" />
              )}
            </div>

            <div className="upload-card">
              <h2>Fingernail</h2>
              <p>Capture the nail bed of your index finger in natural light.</p>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => handleFileChange(e, 'nail')}
              />
              {preview.nail && (
                <img src={preview.nail} alt="Nail preview" className="preview-image" />
              )}
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? 'Analyzing...' : 'Submit for Analysis'}
          </button>
        </form>

        {result && (
          <section className="results-section">
            <h2>Analysis Results</h2>

            <div className="results-grid">
              <div className="result-card">
                <h3>Eye (Conjunctiva)</h3>
                <p>Score: {result.eye_analysis.score.toFixed(1)} / 100</p>
                {renderScoreBar(result.eye_analysis.score)}
                <p>Interpretation: {result.eye_analysis.interpretation}</p>
              </div>

              <div className="result-card">
                <h3>Tongue</h3>
                <p>Score: {result.tongue_analysis.score.toFixed(1)} / 100</p>
                {renderScoreBar(result.tongue_analysis.score)}
                <p>Interpretation: {result.tongue_analysis.interpretation}</p>
              </div>

              <div className="result-card">
                <h3>Fingernail</h3>
                <p>Score: {result.nail_analysis.score.toFixed(1)} / 100</p>
                {renderScoreBar(result.nail_analysis.score)}
                <p>Interpretation: {result.nail_analysis.interpretation}</p>
              </div>
            </div>

            <div className="final-result">
              <h3>Overall Anemia Risk</h3>
              <p className="final-score">
                Final Score: {result.final_score.toFixed(1)} / 100
              </p>
              {renderScoreBar(result.final_score)}
              <p className="risk-level">Risk Level: {result.recommendation.risk_level}</p>
              <p className="recommendation-text">
                {result.recommendation.recommendation}
              </p>

              <h4>Suggested Actions</h4>
              <ul>
                {result.recommendation.dietary_advice.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>

              <p className="disclaimer">
                Disclaimer: This tool is for preliminary screening and educational purposes
                only. It does not provide a medical diagnosis. Always consult a qualified
                healthcare professional for proper evaluation and treatment.
              </p>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
