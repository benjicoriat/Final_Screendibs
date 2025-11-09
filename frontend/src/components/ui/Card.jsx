import { motion } from 'framer-motion';

const Card = ({ 
  children, 
  onClick, 
  hover = true,
  className = '',
  ...props 
}) => {
  const Component = onClick ? motion.div : 'div';
  const hoverStyles = hover ? {
    whileHover: { scale: 1.02 },
    whileTap: { scale: 0.98 }
  } : {};

  return (
    <Component
      className={`bg-white rounded-xl shadow-lg overflow-hidden ${onClick ? 'cursor-pointer' : ''} ${className}`}
      onClick={onClick}
      {...hoverStyles}
      {...props}
    >
      {children}
    </Component>
  );
};

export default Card;