import React from 'react';
import { format, isValid, parseISO } from 'date-fns';

const GameCard = ({ game }) => {
  const formatReleaseDate = (dateString) => {
    if (!dateString) return 'TBA';
    
    try {
      const date = new Date(dateString);
      if (isValid(date)) {
        return format(date, 'MMM dd, yyyy');
      }
    } catch (error) {
      console.error('Date parsing error:', error);
    }
    
    return 'TBA';
  };

  const getCoverImage = (cover) => {
    if (!cover?.url) return null;
    
    // Convert IGDB thumbnail URL to larger image
    return `https:${cover.url.replace('t_thumb', 't_cover_big')}`;
  };

  const getRatingColor = (rating) => {
    if (!rating) return 'bg-gray-100 text-gray-800';
    if (rating >= 80) return 'bg-green-100 text-green-800';
    if (rating >= 70) return 'bg-yellow-100 text-yellow-800';
    if (rating >= 60) return 'bg-orange-100 text-orange-800';
    return 'bg-red-100 text-red-800';
  };

  const platforms = game.platforms || [];
  const releaseDate = game.first_release_date;
  const coverImageUrl = getCoverImage(game.cover);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow duration-200">
      <div className="p-6">
        <div className="flex space-x-4">
          {/* Game Cover */}
          <div className="flex-shrink-0">
            {coverImageUrl ? (
              <img
                src={coverImageUrl}
                alt={`${game.name} cover`}
                className="w-16 h-20 object-cover rounded-md bg-gray-100"
                onError={(e) => {
                  e.target.style.display = 'none';
                }}
              />
            ) : (
              <div className="w-16 h-20 bg-gray-100 rounded-md flex items-center justify-center">
                <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            )}
          </div>

          {/* Game Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-1">
                  {game.name}
                </h3>
                
                {/* Release Date */}
                <div className="flex items-center text-sm text-gray-600 mb-2">
                  <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span className="font-medium">Release:</span>
                  <span className="ml-1">{formatReleaseDate(releaseDate)}</span>
                </div>

                {/* Platforms */}
                {platforms.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {platforms.slice(0, 6).map((platform, index) => (
                      <span
                        key={platform.id || index}
                        className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200"
                      >
                        {platform.name}
                      </span>
                    ))}
                    {platforms.length > 6 && (
                      <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-50 text-gray-700 border border-gray-200">
                        +{platforms.length - 6} more
                      </span>
                    )}
                  </div>
                )}

                {/* Summary */}
                {game.summary && (
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {game.summary.length > 150 
                      ? `${game.summary.substring(0, 150)}...` 
                      : game.summary
                    }
                  </p>
                )}
              </div>

              {/* Rating */}
              {game.rating && (
                <div className="flex-shrink-0 ml-4">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRatingColor(game.rating)}`}>
                    {Math.round(game.rating)}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GameCard;