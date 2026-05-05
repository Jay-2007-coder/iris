import React from 'react';
import { format } from 'date-fns';
import { Cloud, CloudRain, Sun, CloudSnow, CloudLightning } from 'lucide-react';

const WeatherIconSmall = ({ code, className }) => {
  if (code === 0 || code === 1) return <Sun className={className} />;
  if (code >= 2 && code <= 48) return <Cloud className={className} />;
  if ((code >= 51 && code <= 67) || (code >= 80 && code <= 82)) return <CloudRain className={className} />;
  if ((code >= 71 && code <= 77) || (code >= 85 && code <= 86)) return <CloudSnow className={className} />;
  if (code >= 95) return <CloudLightning className={className} />;
  return <Sun className={className} />;
};

const Forecast = ({ weather }) => {
  if (!weather || !weather.daily) return null;

  const { time, weather_code, temperature_2m_max, temperature_2m_min } = weather.daily;

  // Skip the first day (today) and show the next 6 days
  const forecastDays = time.slice(1, 7).map((dateStr, index) => {
    return {
      date: new Date(dateStr),
      code: weather_code[index + 1],
      max: temperature_2m_max[index + 1],
      min: temperature_2m_min[index + 1]
    };
  });

  return (
    <div className="forecast-container glass-panel animate-fade-in" style={{ animationDelay: '0.2s' }}>
      <h3 className="forecast-title">7-Day Forecast</h3>
      <div className="forecast-list">
        {forecastDays.map((day, idx) => (
          <div key={idx} className="forecast-item">
            <div className="forecast-day">
              {format(day.date, 'EEE')}
            </div>
            <WeatherIconSmall code={day.code} className="text-secondary" />
            <div className="forecast-temps">
              <span className="temp-max">{Math.round(day.max)}°</span>
              <span className="temp-min">{Math.round(day.min)}°</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Forecast;
