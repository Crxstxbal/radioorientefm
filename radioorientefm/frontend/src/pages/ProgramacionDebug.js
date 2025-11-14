import React, { useState, useEffect } from 'react';
import { Clock, User, Calendar } from 'lucide-react';
import axios from 'axios';
import './Pages.css';

const ProgramacionDebug = () => {
  const [programs, setPrograms] = useState([]);
  const [horarios, setHorarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const daysOfWeek = {
    0: 'Domingo',
    1: 'Lunes',
    2: 'Martes',
    3: 'Miércoles',
    4: 'Jueves',
    5: 'Viernes',
    6: 'Sábado'
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('🔄 Iniciando carga de datos...');
        
        // Cargar programas
        console.log('📡 Cargando programas...');
        const programsResponse = await axios.get('/api/radio/api/programas/');
        const programsData = programsResponse.data.results || programsResponse.data;
        console.log('✅ Programas cargados:', programsData);
        setPrograms(programsData);
        
        // Cargar horarios
        console.log('📅 Cargando horarios...');
        const horariosResponse = await axios.get('/api/radio/api/horarios/');
        const horariosData = horariosResponse.data.results || horariosResponse.data;
        console.log('✅ Horarios cargados:', horariosData);
        setHorarios(horariosData);
        
        console.log('🎉 Datos cargados exitosamente');
        
      } catch (error) {
        console.error('❌ Error fetching data:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const formatTime = (time) => {
    if (!time) return 'N/A';
    return new Date(`2000-01-01T${time}`).toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getProgramsForDay = (dayNumber) => {
    const daySchedules = horarios.filter(h => h.dia_semana === dayNumber);
    return daySchedules.map(schedule => {
      const program = programs.find(p => p.id === schedule.programa);
      return {
        ...schedule,
        programa: program
      };
    }).sort((a, b) => a.hora_inicio.localeCompare(b.hora_inicio));
  };

  if (loading) {
    return (
      <div className="programming-page">
        <div className="container">
          <div className="loading-container">
            <div className="spinner-large"></div>
            <p>Cargando programación...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="programming-page">
        <div className="container">
          <div style={{ padding: '2rem', textAlign: 'center', color: 'red' }}>
            <h2>Error al cargar la programación</h2>
            <p>{error}</p>
            <button onClick={() => window.location.reload()}>Reintentar</button>
          </div>
        </div>
      </div>
    );
  }

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

        {/* Debug Info */}
        <div style={{ background: '#f0f0f0', padding: '1rem', marginBottom: '2rem', borderRadius: '0.5rem' }}>
          <h3>Debug Info:</h3>
          <p><strong>Programas cargados:</strong> {programs.length}</p>
          <p><strong>Horarios cargados:</strong> {horarios.length}</p>
          <details>
            <summary>Ver datos cargados</summary>
            <pre style={{ fontSize: '12px', overflow: 'auto' }}>
              <strong>Programas:</strong>
              {JSON.stringify(programs, null, 2)}
              
              <strong>Horarios:</strong>
              {JSON.stringify(horarios, null, 2)}
            </pre>
          </details>
        </div>

        <div className="programming-grid">
          {Object.entries(daysOfWeek).map(([dayKey, dayName]) => {
            const dayNumber = parseInt(dayKey);
            const dayPrograms = getProgramsForDay(dayNumber);
            
            return (
              <div key={dayKey} className="day-schedule">
                <h2 className="day-title">
                  {dayName} ({dayPrograms.length} programas)
                </h2>
                <div className="programs-list">
                  {dayPrograms.length > 0 ? (
                    dayPrograms.map((schedule, index) => (
                      <div key={`${schedule.id}-${index}`} className="program-card">
                        <div className="program-content">
                          <h3 className="program-title">
                            {schedule.programa?.nombre || `Programa ID: ${schedule.programa}`}
                          </h3>
                          <p className="program-description">
                            {schedule.programa?.descripcion || 'Sin descripción disponible'}
                          </p>
                          <div className="program-meta">
                            <div className="program-time">
                              <Clock size={16} />
                              {formatTime(schedule.hora_inicio)} - {formatTime(schedule.hora_fin)}
                            </div>
                            <div className="program-host">
                              <User size={16} />
                              Radio Oriente FM
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
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ProgramacionDebug;
