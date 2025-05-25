import React, { useState } from 'react';

function FileUpload({ onStartEvaluation, disabled }) { // Accept new props
  const [questionPaper, setQuestionPaper] = useState(null);
  const [answerSheet, setAnswerSheet] = useState(null);

  const handleQuestionPaperChange = (event) => {
    setQuestionPaper(event.target.files[0]);
  };

  const handleAnswerSheetChange = (event) => {
    setAnswerSheet(event.target.files[0]);
  };

  const handleSubmit = () => {
    if (questionPaper && answerSheet) {
      if (onStartEvaluation) {
        onStartEvaluation(questionPaper, answerSheet); // Call the callback from App.js
      } else {
        // Fallback or error if the prop isn't passed, though it should be
        console.error('onStartEvaluation prop not provided to FileUpload component');
        alert('Cannot start evaluation. Configuration error.');
      }
    } else {
      alert('Please select both files before starting evaluation.');
    }
  };

  return (
    <div>
      <h2>Upload Files</h2>
      <div>
        <label htmlFor="questionPaper">Question Paper PDF:</label>
        <input
          type="file"
          id="questionPaper"
          accept="application/pdf"
          onChange={handleQuestionPaperChange}
          disabled={disabled} // Disable input if evaluation is in progress
        />
      </div>
      <br />
      <div>
        <label htmlFor="answerSheet">Answer Sheet PDF:</label>
        <input
          type="file"
          id="answerSheet"
          accept="application/pdf"
          onChange={handleAnswerSheetChange}
          disabled={disabled} // Disable input if evaluation is in progress
        />
      </div>
      <br />
      <button
        onClick={handleSubmit}
        disabled={!questionPaper || !answerSheet || disabled} // Disable button if files not selected or evaluation in progress
      >
        {disabled ? 'Evaluation in Progress...' : 'Start Evaluation'}
      </button>
    </div>
  );
}

export default FileUpload;
