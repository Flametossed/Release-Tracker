import React from 'react';
import GameCard from './GameCard';
import LoadingSpinner from './LoadingSpinner';

const GameList = ({ games, loading }) => {
  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (!games || games.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="mx-auto h-24 w-24 text-gray-400">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2M4 13h2m13-8l-8 8-4-4" />
          </svg>
        </div>
        <h3 className="mt-4 text-lg font-medium text-gray-900">No games found</h3>
        <p className="mt-2 text-gray-500">
          Try adjusting your filters or search criteria to find more games.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-1">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">
          Upcoming Releases ({games.length} games)
        </h2>
      </div>
      
      <div className="space-y-4">
        {games.map((game) => (
          <GameCard key={game.id} game={game} />
        ))}
      </div>
    </div>
  );
};

export default GameList;