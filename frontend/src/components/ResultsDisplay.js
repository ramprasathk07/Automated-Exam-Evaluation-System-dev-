import React from 'react';

function ResultsDisplay({ evaluationData }) {
  if (!evaluationData || Object.keys(evaluationData).length === 0) {
    return <p>No evaluation results to display yet. Please complete an evaluation.</p>;
  }

  // Placeholder for displaying results.
  // This will be expanded upon when the backend API is integrated.
  return (
    <div>
      <h2>Evaluation Results</h2>
      <div>
        <h3>Overall Summary</h3>
        <p>Overall Score: {evaluationData.overallScore || 'N/A'}</p>
        {/* More summary details can be added here */}
      </div>
      <hr />
      <div>
        <h3>Detailed Breakdown</h3>
        {evaluationData.questions && evaluationData.questions.length > 0 ? (
          evaluationData.questions.map((q, index) => (
            <div key={index} style={{ borderBottom: '1px solid #eee', marginBottom: '10px', paddingBottom: '10px' }}>
              <h4>Question {q.number || (index + 1)}</h4>
              <p><strong>Details:</strong> {q.details || 'N/A'}</p>
              <p><strong>Student Answer:</strong> {q.studentAnswer || 'N/A'}</p>
              <p><strong>Evaluation:</strong> {q.evaluation || 'N/A'}</p>
              <p><strong>Score:</strong> {q.score || 'N/A'}</p>
              <p><strong>Feedback:</strong> {q.feedback || 'N/A'}</p>
            </div>
          ))
        ) : (
          <p>No detailed question breakdown available.</p>
        )}
      </div>
    </div>
  );
}

export default ResultsDisplay;
