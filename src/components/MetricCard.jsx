import { motion } from 'framer-motion';
import { formatNumber } from '../utils/format.js';

export default function MetricCard({ label, value, detail, icon: Icon, tone = 'blue' }) {
  return (
    <motion.div className={`metric-card tone-${tone}`} whileHover={{ y: -4 }} transition={{ duration: 0.2 }}>
      <div className="metric-icon">{Icon && <Icon size={20} />}</div>
      <div>
        <p>{label}</p>
        <strong>{typeof value === 'number' ? formatNumber(value, 2) : value}</strong>
        {detail && <span>{detail}</span>}
      </div>
    </motion.div>
  );
}
