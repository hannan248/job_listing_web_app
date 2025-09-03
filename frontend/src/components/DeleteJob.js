import React, { useState } from 'react';
import { jobsAPI } from '../api';

const DeleteJob = ({ job, onDelete, onCancel, showAsButton = true }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [error, setError] = useState('');

  const handleDeleteClick = () => {
    setShowConfirm(true);
    setError('');
  };

  const handleConfirmDelete = async () => {
    setIsLoading(true);
    setError('');

    try {
      await jobsAPI.deleteJob(job.id);
      
      if (onDelete) {
        onDelete(job.id);
      }
      
      setShowConfirm(false);
    } catch (error) {
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancelDelete = () => {
    setShowConfirm(false);
    setError('');
    
    if (onCancel) {
      onCancel();
    }
  };

  if (showAsButton && !showConfirm) {
    return (
      <button
        onClick={handleDeleteClick}
        className="btn btn-danger btn-sm"
        title="Delete this job"
      >
        Delete
      </button>
    );
  }

  // Confirmation dialog
  return (
    <div className="delete-job">
      {showConfirm && (
        <div className="delete-confirmation">
          <div className="confirmation-content">
            <h3>Confirm Delete</h3>
            
            <div className="job-details">
              <p>Are you sure you want to delete this job?</p>
              <div className="job-info">
                <strong>{job.title}</strong><br />
                <span>{job.company}</span><br />
                <span>{job.location}</span>
              </div>
            </div>
            
            {error && (
              <div className="error-message">
                {error}
              </div>
            )}
            
            <div className="confirmation-actions">
              <button
                onClick={handleConfirmDelete}
                className="btn btn-danger"
                disabled={isLoading}
              >
                {isLoading ? 'Deleting...' : 'Yes, Delete'}
              </button>
              
              <button
                onClick={handleCancelDelete}
                className="btn btn-secondary"
                disabled={isLoading}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export const SimpleDeleteJob = ({ job, onDelete, className = "btn btn-danger btn-sm" }) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleDelete = async () => {
    const confirmDelete = window.confirm(
      `Are you sure you want to delete "${job.title}" at ${job.company}?`
    );
    
    if (!confirmDelete) return;

    setIsLoading(true);

    try {
      await jobsAPI.deleteJob(job.id);
      
      if (onDelete) {
        onDelete(job.id);
      }
      
    } catch (error) {
      alert(`Failed to delete job: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      onClick={handleDelete}
      className={className}
      disabled={isLoading}
      title="Delete this job"
    >
      {isLoading ? '...' : 'Delete'}
    </button>
  );
};

export default DeleteJob;