import React from 'react';
import { format } from 'date-fns';
import { 
  Cloud, CloudRain, Sun, CloudSnow, CloudLightning, 
  Droplets, Wind, Thermometer, Sunrise, Sunset 
} from 'lucide-react';
import { getWeatherDescription } from '../services/weatherApi';

const WeatherIcon = ({ code, isDay, className }) => {
  // WMO codes to lucide icons
  if (code === 0 || code === 1) return <Sun className={className} />;
  if (code >= 2 && code <= 48) return <Cloud className={className} />;
  if ((code >= 51 && code <= 67) || (code >= 80 && code <= 82)) return <CloudRain className={className} />;
  if ((code >= 71 && code <= 77) || (code >= 85 && code <= 86)) return <CloudSnow className={className} />;
  if (code >= 95) return <CloudLightning className={className} />;
  return <Sun className={className} />;
};

const CurrentWeather = ({ weather, city }) => {
  if (!weather || !weather.current) return null;

  const current = weather.current;
  const daily = weather.daily;

  // Assume the first element in daily array is today
  const todayHigh = daily.temperature_2m_max[0];
  const todayLow = daily.temperature_2m_min[0];
  const sunrise = new Date(daily.sunrise[0]);
  const sunset = new Date(daily.sunset[0]);

  return (
    <div className="current-weather-card glass-panel animate-fade-in">
      <div className="text-center">
        <h2 className="city-name">{city.name}</h2>
        <p className="date-text">
          {format(new Date(), 'EEEE, d MMMM yyyy | h:mm a')}
        </p>
      </div>

      <div className="temp-container">
        <WeatherIcon 
          code={current.weather_code} 
          isDay={current.is_day} 
          className="weather-icon-large" 
        />
        <div className="main-temp">
          {Math.round(current.temperature_2m)}°
        </div>
      </div>
      
      <div className="weather-desc">
        {getWeatherDescription(current.weather_code)}
      </div>

      <div className="weather-details-grid">
        <div className="detail-item">
          <Thermometer className="text-secondary" size={20} />
          <div className="detail-info">
            <span className="detail-label">Feels Like</span>
            <span className="detail-value">{Math.round(current.apparent_temperature)}°</span>
          </div>
        </div>
        
        <div className="detail-item">
          <Droplets className="text-secondary" size={20} />
          <div className="detail-info">
            <span className="detail-label">Humidity</span>
            <span className="detail-value">{current.relative_humidity_2m}%</span>
          </div>
        </div>

        <div className="detail-item">
          <Wind className="text-secondary" size={20} />
          <div className="detail-info">
            <span className="detail-label">Wind</span>
            <span className="detail-value">{current.wind_speed_10m} km/h</span>
          </div>
        </div>

        <div className="detail-item">
          <Thermometer className="text-secondary" size={20} />
          <div className="detail-info">
            <span className="detail-label">High / Low</span>
            <span className="detail-value">{Math.round(todayHigh)}° / {Math.round(todayLow)}°</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CurrentWeather;
