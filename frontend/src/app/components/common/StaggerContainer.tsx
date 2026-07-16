import React from "react";
import { motion } from "motion/react";

interface StaggerContainerProps {
  children: React.ReactNode;
  className?: string;
}

export function StaggerContainer({ children, className = "" }: StaggerContainerProps) {
  return (
    <motion.div
      className={className}
      initial="hidden"
      animate="show"
    >
      {React.Children.map(children, (child) =>
        child ? (
          <motion.div
            variants={{
              hidden: { opacity: 0, y: 14 },
              show: {
                opacity: 1,
                y: 0,
                transition: { duration: 0.5, ease: "easeOut" },
              },
            }}
            style={{ display: "contents" }}
          >
            {child}
          </motion.div>
        ) : null
      )}
    </motion.div>
  );
}
