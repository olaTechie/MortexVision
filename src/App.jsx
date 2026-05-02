import { AnimatePresence } from 'framer-motion';
import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import AppLayout from './layouts/AppLayout.jsx';
import Analytics from './pages/Analytics.jsx';
import CountryProfiles from './pages/CountryProfiles.jsx';
import DataExplorer from './pages/DataExplorer.jsx';
import Insights from './pages/Insights.jsx';
import Maps from './pages/Maps.jsx';
import Overview from './pages/Overview.jsx';
import PolicySimulator from './pages/PolicySimulator.jsx';
import Reports from './pages/Reports.jsx';
import Settings from './pages/Settings.jsx';

export default function App() {
  const location = useLocation();

  return (
    <AppLayout>
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<Overview />} />
          <Route path="/data" element={<DataExplorer />} />
          <Route path="/maps" element={<Maps />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/countries" element={<CountryProfiles />} />
          <Route path="/simulator" element={<PolicySimulator />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/insights" element={<Insights />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AnimatePresence>
    </AppLayout>
  );
}
