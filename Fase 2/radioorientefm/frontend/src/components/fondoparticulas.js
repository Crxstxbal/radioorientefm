import React, { useMemo, useCallback } from "react";
import Particles from "react-tsparticles";
import { loadFull } from "tsparticles";

const FondoParticulas = React.memo(() => {
  const particlesInit = useCallback(async (main) => {
    await loadFull(main);
  }, []);

  const options = useMemo(() => ({
    fullScreen: { enable: true },

    fpsLimit: 120,
    interactivity: {
      events: {
        onHover: {
          enable: true,
          mode: ["attract", "bubble"]
        },
        onClick: {
          enable: true,
          mode: "push"
        }
      },
      modes: {
        attract: {
          distance: 200,
          duration: 0.4,
          factor: 3
        },
        bubble: {
          distance: 250,
          size: 8,
          duration: 2,
          opacity: 0.8
        },
        push: {
          quantity: 3
        }
      }
    },
    particles: {
      color: {
        value: ["#dc2626", "#b91c1c", "#991b1b", "#7f1d1d", "#ffffff"] // Gama de rojos y blanco
      },
      links: {
        enable: true,
        color: "#dc2626",
        distance: 150,
        opacity: 0.6,
        width: 1
      },
      collisions: {
        enable: true
      },
      move: {
        enable: true,
        speed: 2,
        direction: "none",
        random: true,
        straight: false,
        outModes: {
          default: "bounce"
        },
        attract: {
          enable: false,
          rotateX: 600,
          rotateY: 1200
        }
      },
      number: {
        value: 150,
        density: {
          enable: true,
          area: 600
        }
      },
      opacity: {
        value: 0.7,
        random: {
          enable: true,
          minimumValue: 0.3
        },
        animation: {
          enable: true,
          speed: 1,
          minimumValue: 0.1,
          sync: false
        }
      },
      shape: {
        type: ["circle", "triangle", "square"] // Formas variadas como ondas de radio
      },
      size: {
        value: 4,
        random: {
          enable: true,
          minimumValue: 2
        },
        animation: {
          enable: true,
          speed: 2,
          minimumValue: 1,
          sync: false
        }
      }
    },
    detectRetina: true,
    //efecto de pulsación como ondas de radio
    emitters: {
      direction: "none",
      life: {
        count: 0,
        duration: 0.1,
        delay: 0.1
      },
      rate: {
        delay: 0.5,
        quantity: 1
      },
      size: {
        width: 0,
        height: 0
      },
      position: {
        x: 50,
        y: 50
      }
    }
  }), []);

  return (
    <Particles
      id="tsparticles"
      init={particlesInit}
      options={options}
    />
  );
});

export default FondoParticulas;