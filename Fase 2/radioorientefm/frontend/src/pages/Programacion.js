import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Clock, User, Calendar } from 'lucide-react';
import api from '../utils/api';
import './Pages.css';

const Programming = () => {
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDay, setSelectedDay] = useState(null); // null = todos los días

  const daysOfWeek = [
    { key: 1, name: 'Lunes', short: 'Lun' },
    { key: 2, name: 'Martes', short: 'Mar' },
    { key: 3, name: 'Miércoles', short: 'Mié' },
    { key: 4, name: 'Jueves', short: 'Jue' },
    { key: 5, name: 'Viernes', short: 'Vie' },
    { key: 6, name: 'Sábado', short: 'Sáb' },
    { key: 0, name: 'Domingo', short: 'Dom' }
  ];

  useEffect(() => {
    const fetchData = async () => {
      try {
        const programsResponse = await api.get('/api/radio/programas/');
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

  const groupProgramsByDay = useMemo(() => {
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
  }, [programs]);

  const formatTime = useCallback((time) => {
    if (!time) return '';
    return new Date(`2000-01-01T${time}`).toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit'
    });
  }, []);

  const groupedPrograms = groupProgramsByDay;

  //memoizar días filtrados
  const daysToShow = useMemo(() => {
    return selectedDay !== null
      ? daysOfWeek.filter(day => day.key === selectedDay)
      : daysOfWeek;
  }, [selectedDay]);

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

        {/*filtro de días*/}
        <div className="days-filter">
          <button
            className={`day-filter-btn ${selectedDay === null ? 'active' : ''}`}
            onClick={() => setSelectedDay(null)}
          >
            <span className="day-full">Todos</span>
            <span className="day-short">Todos</span>
          </button>
          {daysOfWeek.map((day) => (
            <button
              key={day.key}
              className={`day-filter-btn ${selectedDay === day.key ? 'active' : ''}`}
              onClick={() => setSelectedDay(day.key)}
            >
              <span className="day-full">{day.name}</span>
              <span className="day-short">{day.short}</span>
            </button>
          ))}
        </div>

        {loading ? (
          <div className="loading-container">
            <div className="spinner-large"></div>
            <p>Cargando programación...</p>
          </div>
        ) : (
          <div className="programming-grid">
            {daysToShow.map((day) => {
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

                            <div className="program-time">
                              <Clock size={18} />
                              <span>{formatTime(schedule.hora_inicio)} - {formatTime(schedule.hora_fin)}</span>
                            </div>

                            <p className="program-description">
                              {schedule.programa_descripcion || 'Sin descripción disponible'}
                            </p>

                            {schedule.conductores && schedule.conductores.length > 0 && (
                              <div className="program-hosts">
                                <div className="hosts-label">
                                  <User size={16} />
                                  <span>Conducido por:</span>
                                </div>
                                <div className="hosts-list">
                                  {schedule.conductores.map((conductor, idx) => (
                                    <div key={idx} className="host-item">
                                      {conductor.conductor_foto ? (
                                        <img
                                          src={conductor.conductor_foto}
                                          alt={conductor.conductor_nombre}
                                          className="host-avatar"
                                        />
                                      ) : (
                                        <div className="host-avatar-placeholder">
                                          <User size={16} />
                                        </div>
                                      )}
                                      <div className="host-info">
                                        <span className="host-name">
                                          {conductor.conductor_apodo || conductor.conductor_nombre}
                                        </span>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
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