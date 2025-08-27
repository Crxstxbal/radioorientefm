import { motion } from "framer-motion";
import React from "react";

const pageVariants = {
  initial: {
    opacity: 0,
    y: 20,
  },
  in: {
    opacity: 1,
    y: 0,
  },
  out: {
    opacity: 0,
    y: -20,
  },
};

const pageTransition = {
  type: "tween",
  ease: "easeInOut",
  duration: 0.5,
};

const PageWrapper = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50 p-6 sm:p-12 flex flex-col justify-center">
      <motion.div
        initial="initial"
        animate="in"
        exit="out"
        variants={pageVariants}
        transition={pageTransition}
        className="max-w-3xl mx-auto bg-white p-8 rounded shadow-lg"
      >
        {children}
      </motion.div>
    </div>
  );
};

export default PageWrapper;
