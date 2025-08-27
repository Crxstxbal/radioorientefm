import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';

const AnimatedTitle = ({ children, className = "" }) => {
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.3, // aparece al 30% visible
  });

  return (
    <motion.h2
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.8, ease: "easeOut" }}
      className={`text-3xl font-bold mb-4 ${className}`}
    >
      {children}
    </motion.h2>
  );
};

export default AnimatedTitle;
