import React, { useState, useEffect } from 'react';
import { Clock, User, Calendar } from 'lucide-react';
import axios from 'axios';
import './Pages.css';

const Programming = () => {
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(true);

  const daysOfWeek = {
    'monday': 'Lunes',
    'tuesday': 'Martes',
    'wednesday': 'Miércoles',
    'thursday': 'Jueves',
    'friday': 'Viernes',
    'saturday': 'Sábado',
    'sunday': 'Domingo'
  };

  useEffect(() => {
    const fetchPrograms = async () => {
      try {
        const response = await axios.get('/api/radio/programs/');
        setPrograms(response.data.results || response.data);
      } catch (error) {
        console.error('Error fetching programs:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPrograms();
  }, []);

  const groupProgramsByDay = () => {
    const grouped = {};
    Object.keys(daysOfWeek).forEach(day => {
      grouped[day] = programs.filter(program => program.day_of_week === day);
    });
    return grouped;
  };

  const formatTime = (time) => {
    return new Date(`2000-01-01T${time}`).toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const groupedPrograms = groupProgramsByDay();

  return (
    <div className="programming-page">
      <div className="container">
        <div className="page-header">
          <Calendar className="page-icon" />
          <div>
            <h1 className="page-title">Programación</h1>
            <p className="page-subtitle">
              Conoce nuestra programación semanal y no te pierdas tus programas favoritos
            </p>
          </div>
        </div>

        {loading ? (
          <div className="loading-container">
            <div className="spinner-large"></div>
            <p>Cargando programación...</p>
          </div>
        ) : (
          <div className="programming-grid">
            {Object.entries(daysOfWeek).map(([dayKey, dayName]) => (
              <div key={dayKey} className="day-schedule">
                <h2 className="day-title">{dayName}</h2>
                <div className="programs-list">
                  {groupedPrograms[dayKey].length > 0 ? (
                    groupedPrograms[dayKey].map((program) => (
                      <div key={program.id} className="program-card">
                        {program.image && (
                          <img 
                            src={program.image} 
                            alt={program.title}
                            className="program-image"
                          />
                        )}
                        <div className="program-content">
                          <h3 className="program-title">{program.title}</h3>
                          <p className="program-description">{program.description}</p>
                          <div className="program-meta">
                            <div className="program-time">
                              <Clock size={16} />
                              {formatTime(program.start_time)} - {formatTime(program.end_time)}
                            </div>
                            <div className="program-host">
                              <User size={16} />
                              {program.host}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="no-programs">
                      <p>No hay programas programados para este día</p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Programming;