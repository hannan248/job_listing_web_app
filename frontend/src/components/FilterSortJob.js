import React, { useState, useEffect } from 'react';
import { jobsAPI } from '../api';

const FilterSortJob = ({ onFiltersChange, initialFilters = {} }) => {
  const [filters, setFilters] = useState({
    search: '',
    job_type: '',
    location: '',
    tag: '',
    sort: 'posting_date_desc',
    ...initialFilters
  });

  const [dropdownData, setDropdownData] = useState({
    jobTypes: [],
    locations: [],
    tags: []
  });

  const [isLoading, setIsLoading] = useState(false);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  // Load dropdown data on component mount
  useEffect(() => {
    loadDropdownData();
  }, []);

  // Notify parent component when filters change
  useEffect(() => {
    if (onFiltersChange) {
      onFiltersChange(filters);
    }
  }, [filters, onFiltersChange]);

  const loadDropdownData = async () => {
    setIsLoading(true);
    try {
      const [jobTypesRes, locationsRes, tagsRes] = await Promise.all([
        jobsAPI.getJobTypes().catch(() => ({ data: [] })),
        jobsAPI.getLocations().catch(() => ({ data: [] })),
        jobsAPI.getTags().catch(() => ({ data: [] }))
      ]);

      setDropdownData({
        jobTypes: jobTypesRes.data || [],
        locations: locationsRes.data || [],
        tags: tagsRes.data || []
      });
    } catch (error) {
      console.error('Error loading dropdown data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    // The useEffect will handle notifying parent
  };

  const resetFilters = () => {
    setFilters({
      search: '',
      job_type: '',
      location: '',
      tag: '',
      sort: 'posting_date_desc'
    });
  };

  const getActiveFiltersCount = () => {
    const activeFilters = Object.entries(filters).filter(([key, value]) => 
      value && value !== '' && key !== 'sort'
    );
    return activeFilters.length;
  };

  return (
    <div className="filter-sort-container">
      {/* Search Bar */}
      <div className="search-section">
        <form onSubmit={handleSearchSubmit} className="search-form">
          <div className="search-input-group">
            <input
              type="text"
              name="search"
              value={filters.search}
              onChange={handleInputChange}
              placeholder="Search jobs by title or company..."
              className="search-input"
            />
            <button type="submit" className="search-button">
              Search
            </button>
          </div>
        </form>
      </div>

      {/* Quick Filters */}
      <div className="quick-filters">
        <div className="filter-group">
          <label htmlFor="sort">Sort by:</label>
          <select
            id="sort"
            name="sort"
            value={filters.sort}
            onChange={handleInputChange}
            className="filter-select"
          >
            <option value="posting_date_desc">Newest First</option>
            <option value="posting_date_asc">Oldest First</option>
            <option value="title_asc">Title A-Z</option>
            <option value="company_asc">Company A-Z</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="job_type">Job Type:</label>
          <select
            id="job_type"
            name="job_type"
            value={filters.job_type}
            onChange={handleInputChange}
            className="filter-select"
            disabled={isLoading}
          >
            <option value="">All Types</option>
            {dropdownData.jobTypes.map((type, index) => (
              <option key={index} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>

        <button
          type="button"
          onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
          className="btn btn-secondary btn-sm"
        >
          {showAdvancedFilters ? 'Hide' : 'More'} Filters
          {getActiveFiltersCount() > 0 && (
            <span className="filter-count">({getActiveFiltersCount()})</span>
          )}
        </button>
      </div>

      {/* Advanced Filters */}
      {showAdvancedFilters && (
        <div className="advanced-filters">
          <div className="filter-row">
            <div className="filter-group">
              <label htmlFor="location">Location:</label>
              <select
                id="location"
                name="location"
                value={filters.location}
                onChange={handleInputChange}
                className="filter-select"
                disabled={isLoading}
              >
                <option value="">All Locations</option>
                {dropdownData.locations.map((location, index) => (
                  <option key={index} value={location}>
                    {location}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label htmlFor="tag">Tag/Skill:</label>
              <select
                id="tag"
                name="tag"
                value={filters.tag}
                onChange={handleInputChange}
                className="filter-select"
                disabled={isLoading}
              >
                <option value="">All Tags</option>
                {dropdownData.tags.map((tag, index) => (
                  <option key={index} value={tag}>
                    {tag}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Active Filters Summary */}
      {getActiveFiltersCount() > 0 && (
        <div className="active-filters">
          <div className="active-filters-header">
            <span>Active Filters:</span>
            <button
              type="button"
              onClick={resetFilters}
              className="btn btn-link btn-sm"
            >
              Clear All
            </button>
          </div>
          
          <div className="active-filters-list">
            {filters.search && (
              <span className="filter-tag">
                Search: "{filters.search}"
                <button
                  onClick={() => setFilters(prev => ({ ...prev, search: '' }))}
                  className="filter-tag-remove"
                >
                  ×
                </button>
              </span>
            )}
            
            {filters.job_type && (
              <span className="filter-tag">
                Type: {filters.job_type}
                <button
                  onClick={() => setFilters(prev => ({ ...prev, job_type: '' }))}
                  className="filter-tag-remove"
                >
                  ×
                </button>
              </span>
            )}
            
            {filters.location && (
              <span className="filter-tag">
                Location: {filters.location}
                <button
                  onClick={() => setFilters(prev => ({ ...prev, location: '' }))}
                  className="filter-tag-remove"
                >
                  ×
                </button>
              </span>
            )}
            
            {filters.tag && (
              <span className="filter-tag">
                Tag: {filters.tag}
                <button
                  onClick={() => setFilters(prev => ({ ...prev, tag: '' }))}
                  className="filter-tag-remove"
                >
                  ×
                </button>
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default FilterSortJob;