import React, { useState, useEffect } from 'react';
import { Clock, User, Calendar } from 'lucide-react';
import axios from 'axios';
import './Pages.css';

const Programming = () => {
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(true);

  const daysOfWeek = [
    { key: 1, name: 'Lunes' },
    { key: 2, name: 'Martes' },
    { key: 3, name: 'Miércoles' },
    { key: 4, name: 'Jueves' },
    { key: 5, name: 'Viernes' },
    { key: 6, name: 'Sábado' },
    { key: 0, name: 'Domingo' }
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        const programsResponse = await axios.get('/api/radio/programas/');
        const programsData = programsResponse.data.results || programsResponse.data;
        setPrograms(programsData);

      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const groupProgramsByDay = () => {
    const grouped = {};
    daysOfWeek.forEach(day => {
      grouped[day.key] = [];
    });

    programs.forEach(program => {
      if (!program.activo) return;
      program.horarios.forEach(horario => {
        if (horario.activo === false) return;

        const scheduleItem = {
          id: `${program.id}-${horario.id}`,
          hora_inicio: horario.hora_inicio,
          hora_fin: horario.hora_fin,
          programa_nombre: program.nombre,
          programa_descripcion: program.descripcion,
          programa_imagen: program.imagen_url,
          conductores: program.conductores 
        };
        
        if (grouped[horario.dia_semana]) {
          grouped[horario.dia_semana].push(scheduleItem);
        }
      });
    });

    daysOfWeek.forEach(day => {
      grouped[day.key].sort((a, b) => a.hora_inicio.localeCompare(b.hora_inicio));
    });
    
    return grouped;
  };

  const formatTime = (time) => {
    if (!time) return '';
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
            {daysOfWeek.map((day) => {
              const dayNumber = day.key;
              return (
                <div key={day.key} className="day-schedule">
                  <h2 className="day-title">{day.name}</h2>
                  <div className="programs-list">
                    {groupedPrograms[dayNumber]?.length > 0 ? (
                      groupedPrograms[dayNumber].map((schedule) => (
                        <div key={schedule.id} className="program-card">
                          {schedule.programa_imagen && (
                            <img 
                              src={schedule.programa_imagen} 
                              alt={schedule.programa_nombre}
                              className="program-image"
                            />
                          )}
                          <div className="program-content">
                            
                            <h3 className="program-title">
                              {schedule.programa_nombre}
                            </h3>
                            
                            <p className="program-description">
                              {schedule.programa_descripcion || 'Sin descripción disponible'}
                            </p>
                            <div className="program-meta">
                              <div className="program-time">
                                <Clock size={16} />
                                {formatTime(schedule.hora_inicio)} - {formatTime(schedule.hora_fin)}
                              </div>
                              
                              <div className="program-host">
                                <User size={16} />
                                {schedule.conductores && schedule.conductores.length > 0 ? (
                                  schedule.conductores.map(c => c.conductor_nombre).join(', ')
                                ) : (
                                  'Radio Oriente FM'
                                )}
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
        )}
      </div>
    </div>
  );
};

export default Programming;