import React, { useState, useEffect } from 'react';
import GameList from './components/GameList';
import PlatformFilter from './components/PlatformFilter';
import SearchBar from './components/SearchBar';
import LoadingSpinner from './components/LoadingSpinner';
import { gameService } from './services/gameService';
import './App.css';

function App() {
  const [games, setGames] = useState([]);
  const [platforms, setPlatforms] = useState([]);
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [daysAhead, setDaysAhead] = useState(90);

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    loadGames();
  }, [selectedPlatforms, daysAhead]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      
      // Load platforms first
      const platformsData = await gameService.getPlatforms();
      setPlatforms(platformsData);
      
      // Load initial games
      await loadGames();
      
    } catch (err) {
      console.error('Error loading initial data:', err);
      setError('Failed to load data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const loadGames = async () => {
    try {
      setError(null);
      
      if (searchQuery.trim()) {
        // If there's a search query, search for games
        const searchResults = await gameService.searchGames(searchQuery);
        setGames(searchResults.games || []);
      } else {
        // Otherwise, load upcoming games
        const platformIds = selectedPlatforms.length > 0 ? selectedPlatforms : null;
        const gamesData = await gameService.getUpcomingGames(daysAhead, 100, platformIds);
        setGames(gamesData.games || []);
      }
      
    } catch (err) {
      console.error('Error loading games:', err);
      setError('Failed to load games. Please try again.');
    }
  };

  const handlePlatformChange = (platformIds) => {
    setSelectedPlatforms(platformIds);
  };

  const handleSearch = async (query) => {
    setSearchQuery(query);
    
    if (query.trim()) {
      try {
        setLoading(true);
        const searchResults = await gameService.searchGames(query);
        setGames(searchResults.games || []);
      } catch (err) {
        console.error('Error searching games:', err);
        setError('Failed to search games. Please try again.');
      } finally {
        setLoading(false);
      }
    } else {
      // Clear search, reload upcoming games
      loadGames();
    }
  };

  const handleRefresh = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Force refresh from API
      const platformIds = selectedPlatforms.length > 0 ? selectedPlatforms : null;
      const gamesData = await gameService.getUpcomingGames(daysAhead, 100, platformIds, true);
      setGames(gamesData.games || []);
      
    } catch (err) {
      console.error('Error refreshing games:', err);
      setError('Failed to refresh data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSyncData = async () => {
    try {
      await gameService.syncData();
      // Show success message (you could add a toast notification here)
      setTimeout(() => {
        loadGames();
      }, 2000); // Reload after 2 seconds to let sync complete
    } catch (err) {
      console.error('Error syncing data:', err);
      setError('Failed to sync data. Please try again.');
    }
  };

  if (loading && games.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                🎮 Game Release Tracker
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={handleRefresh}
                disabled={loading}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
              >
                {loading ? 'Refreshing...' : 'Refresh'}
              </button>
              <button
                onClick={handleSyncData}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Sync Data
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters and Search */}
        <div className="mb-8 space-y-4">
          <SearchBar onSearch={handleSearch} />
          
          <div className="flex flex-wrap items-center gap-4">
            <PlatformFilter
              platforms={platforms}
              selectedPlatforms={selectedPlatforms}
              onPlatformChange={handlePlatformChange}
            />
            
            <div className="flex items-center space-x-2">
              <label htmlFor="days-ahead" className="text-sm font-medium text-gray-700">
                Days ahead:
              </label>
              <select
                id="days-ahead"
                value={daysAhead}
                onChange={(e) => setDaysAhead(parseInt(e.target.value))}
                className="rounded-md border-gray-300 text-sm focus:border-primary-500 focus:ring-primary-500"
              >
                <option value={30}>30 days</option>
                <option value={60}>60 days</option>
                <option value={90}>90 days</option>
                <option value={180}>6 months</option>
                <option value={365}>1 year</option>
              </select>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Games List */}
        <GameList games={games} loading={loading} />
      </main>
    </div>
  );
}

export default App;