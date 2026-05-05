import React, { useState, useEffect } from 'react';
import SearchBar from './components/SearchBar';
import CurrentWeather from './components/CurrentWeather';
import Forecast from './components/Forecast';
import IrisAuth from './components/IrisAuth';
import { fetchWeatherData } from './services/weatherApi';

function App() {
  // Authentication state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authUser, setAuthUser] = useState(null);

  // Default to London
  const [city, setCity] = useState({ name: 'London', latitude: 51.5085, longitude: -0.1257 });
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isAuthenticated) return;

    const loadWeather = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchWeatherData(city.latitude, city.longitude);
        if (data) {
          setWeather(data);
          updateTheme(data.current.weather_code, data.current.is_day);
        } else {
          setError("Failed to fetch weather data.");
        }
      } catch (err) {
        setError("An error occurred while fetching data.");
      } finally {
        setLoading(false);
      }
    };

    loadWeather();
  }, [city, isAuthenticated]);

  const updateTheme = (code, isDay) => {
    // Remove old themes
    document.body.className = '';
    
    // WMO codes logic
    if (code === 0 || code === 1) {
      document.body.classList.add(isDay ? 'theme-day-clear' : 'theme-night-clear');
    } else if (code >= 2 && code <= 48) {
      document.body.classList.add('theme-clouds');
    } else if ((code >= 51 && code <= 67) || (code >= 80 && code <= 82)) {
      document.body.classList.add('theme-rain');
    } else if ((code >= 71 && code <= 77) || (code >= 85 && code <= 86)) {
      document.body.classList.add('theme-snow');
    } else {
      document.body.classList.add(isDay ? 'theme-day-clear' : 'theme-night-clear');
    }
  };

  const handleAuthenticated = (username) => {
    setAuthUser(username);
    setIsAuthenticated(true);
  };

  if (!isAuthenticated) {
    return (
      <div className="app-container" style={{display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh'}}>
        <IrisAuth onAuthenticated={handleAuthenticated} />
      </div>
    );
  }

  return (
    <div className="app-container">
      <div style={{ display: 'flex', justifyContent: 'flex-end', padding: '10px 20px', color: 'white' }}>
        <span style={{ marginRight: '15px', alignSelf: 'center' }}>Welcome, <strong>{authUser}</strong>!</span>
        <button 
          onClick={() => { setIsAuthenticated(false); setAuthUser(null); document.body.className = ''; }}
          style={{ background: 'rgba(255,255,255,0.2)', color: 'white', border: '1px solid white', borderRadius: '15px', padding: '5px 15px', cursor: 'pointer' }}
        >
          Logout
        </button>
      </div>

      <SearchBar onCitySelect={setCity} />
      
      {loading ? (
        <div className="loader-container">
          <div className="loader"></div>
        </div>
      ) : error ? (
        <div className="error-message glass-panel">
          {error}
        </div>
      ) : (
        <main className="main-content">
          <CurrentWeather weather={weather} city={city} />
          <Forecast weather={weather} />
        </main>
      )}
    </div>
  );
}

export default App;
