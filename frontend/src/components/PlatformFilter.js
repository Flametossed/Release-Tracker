import React, { useState } from 'react';

const PlatformFilter = ({ platforms, selectedPlatforms, onPlatformChange }) => {
  const [isOpen, setIsOpen] = useState(false);

  const handlePlatformToggle = (platformId) => {
    const newSelected = selectedPlatforms.includes(platformId)
      ? selectedPlatforms.filter(id => id !== platformId)
      : [...selectedPlatforms, platformId];
    
    onPlatformChange(newSelected);
  };

  const clearFilters = () => {
    onPlatformChange([]);
  };

  const majorPlatforms = platforms.filter(platform => {
    const name = platform.name.toLowerCase();
    return (
      name.includes('playstation') ||
      name.includes('xbox') ||
      name.includes('nintendo') ||
      name.includes('switch') ||
      name.includes('steam') ||
      name.includes('epic') ||
      name.includes('pc') ||
      name.includes('windows')
    );
  });

  const getDisplayName = (platform) => {
    const name = platform.name;
    // Shorten some common platform names
    if (name.includes('PlayStation')) return name.replace('Sony ', '');
    if (name.includes('Xbox')) return name.replace('Microsoft ', '');
    if (name.includes('Nintendo')) return name;
    return name;
  };

  return (
    <div className="relative">
      <div className="flex items-center space-x-2">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
          </svg>
          Platforms
          {selectedPlatforms.length > 0 && (
            <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
              {selectedPlatforms.length}
            </span>
          )}
          <svg className="ml-2 -mr-1 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {selectedPlatforms.length > 0 && (
          <button
            onClick={clearFilters}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            Clear filters
          </button>
        )}
      </div>

      {isOpen && (
        <div className="absolute z-10 mt-2 w-80 bg-white rounded-md shadow-lg border border-gray-200">
          <div className="p-4">
            <div className="mb-3">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Select Platforms</h4>
              <div className="text-xs text-gray-500">
                Filter games by gaming platform
              </div>
            </div>
            
            <div className="max-h-60 overflow-y-auto">
              <div className="space-y-2">
                {majorPlatforms.length > 0 ? (
                  majorPlatforms.map((platform) => (
                    <label
                      key={platform.id}
                      className="flex items-center space-x-3 cursor-pointer hover:bg-gray-50 p-2 rounded"
                    >
                      <input
                        type="checkbox"
                        checked={selectedPlatforms.includes(platform.id)}
                        onChange={() => handlePlatformToggle(platform.id)}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <span className="text-sm text-gray-900">
                        {getDisplayName(platform)}
                      </span>
                      {platform.abbreviation && (
                        <span className="text-xs text-gray-500">
                          ({platform.abbreviation})
                        </span>
                      )}
                    </label>
                  ))
                ) : (
                  <div className="text-sm text-gray-500 text-center py-4">
                    No platforms available
                  </div>
                )}
              </div>
            </div>
            
            <div className="mt-4 pt-3 border-t border-gray-200">
              <button
                onClick={() => setIsOpen(false)}
                className="w-full text-center text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlatformFilter;