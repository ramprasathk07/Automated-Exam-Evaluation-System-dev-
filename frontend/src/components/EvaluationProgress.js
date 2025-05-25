import React from 'react';

function EvaluationProgress({ statusMessage }) {
  return (
    <div>
      <h3>Evaluation in Progress...</h3>
      <p>{statusMessage}</p>
      {/* Simple loading spinner placeholder */}
      <div style={{
        border: '4px solid #f3f3f3', /* Light grey */
        borderTop: '4px solid #3498db', /* Blue */
        borderRadius: '50%',
        width: '30px',
        height: '30px',
        animation: 'spin 1s linear infinite'
      }}></div>
      <style jsx global>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default EvaluationProgress;
