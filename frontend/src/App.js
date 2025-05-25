import React, { useState, useEffect } from 'react';
import './App.css';
import FileUpload from './components/FileUpload';
import EvaluationProgress from './components/EvaluationProgress';
import ResultsDisplay from './components/ResultsDisplay';

function App() {
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [evaluationStatusMessage, setEvaluationStatusMessage] = useState('');
  const [evaluationResults, setEvaluationResults] = useState(null);
  const [backendMessage, setBackendMessage] = useState(''); // For backend message

  // Fetch message from backend on component mount
  useEffect(() => {
    fetch('http://localhost:5001/api/hello')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        setBackendMessage(data.message || 'No message field in response');
      })
      .catch(error => {
        console.error('Error fetching from backend:', error);
        setBackendMessage('Failed to connect to backend. Is it running?');
      });
  }, []); // Empty dependency array means this runs once on mount

  const handleStartEvaluation = (questionFile, answerFile) => {
    console.log('App: Starting evaluation with:', questionFile.name, answerFile.name);
    setIsEvaluating(true);
    setEvaluationResults(null); // Clear previous results
    setEvaluationStatusMessage('Uploading files...');

    // Simulate evaluation process
    setTimeout(() => {
      setEvaluationStatusMessage('Processing PDFs...');
      setTimeout(() => {
        setEvaluationStatusMessage('Extracting text from documents...');
        setTimeout(() => {
          setEvaluationStatusMessage('AI is evaluating the answers...');
          setTimeout(() => {
            // Simulate receiving results
            const mockResults = {
              overallScore: '85%',
              questions: [
                {
                  number: 1,
                  details: 'What is the capital of France?',
                  studentAnswer: 'Paris',
                  evaluation: 'Correct',
                  score: '10/10',
                  feedback: 'Well done!',
                },
                {
                  number: 2,
                  details: 'What is 2 + 2?',
                  studentAnswer: '4',
                  evaluation: 'Correct',
                  score: '5/5',
                  feedback: 'Excellent.',
                },
                {
                  number: 3,
                  details: 'Explain photosynthesis.',
                  studentAnswer: 'It is a process plants use to make food.',
                  evaluation: 'Partially Correct',
                  score: '7/10',
                  feedback: 'Good start, but could include more detail on chlorophyll and sunlight.',
                },
              ],
              summary: 'Good overall performance. Pay attention to providing detailed answers for descriptive questions.'
            };
            setEvaluationResults(mockResults);
            setIsEvaluating(false);
            setEvaluationStatusMessage('Evaluation Complete!');
          }, 3000); // Simulate AI evaluation
        }, 2000); // Simulate text extraction
      }, 2000); // Simulate PDF processing
    }, 1000); // Simulate file upload
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Automated Exam Evaluation System</h1>
        {backendMessage && <p style={{ color: backendMessage.startsWith('Failed') ? 'red' : 'lightgreen', fontSize: '0.9em' }}>{backendMessage}</p>}
      </header>
      <main>
        {/* We can pass handleStartEvaluation to FileUpload */}
        <FileUpload onStartEvaluation={handleStartEvaluation} disabled={isEvaluating} />

        {isEvaluating && (
          <EvaluationProgress statusMessage={evaluationStatusMessage} />
        )}

        {evaluationResults && !isEvaluating && (
          <ResultsDisplay evaluationData={evaluationResults} />
        )}

        {!isEvaluating && !evaluationResults && (
          <p style={{marginTop: '20px'}}>Please upload files and start the evaluation.</p>
        )}
      </main>
    </div>
  );
}

export default App;
