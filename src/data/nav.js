import {
  BarChart3,
  FileText,
  Globe2,
  Home,
  LineChart,
  Map,
  Search,
  Settings,
  SlidersHorizontal,
  Sparkles,
} from 'lucide-react';

export const appName = 'MortexVision';

export const navItems = [
  { path: '/', label: 'Overview', icon: Home },
  { path: '/data', label: 'Data Explorer', icon: Search },
  { path: '/maps', label: 'Global Maps', icon: Map },
  { path: '/analytics', label: 'Analytics', icon: LineChart },
  { path: '/countries', label: 'Country Profiles', icon: Globe2 },
  { path: '/simulator', label: 'Policy Simulator', icon: SlidersHorizontal },
  { path: '/reports', label: 'Reports', icon: FileText },
  { path: '/insights', label: 'Insights', icon: Sparkles },
  { path: '/settings', label: 'About', icon: Settings },
];

export const determinantGroups = [
  {
    title: 'Distal Determinants',
    icon: BarChart3,
    tone: 'amber',
    description: 'Root socioeconomic conditions such as income, literacy, inequality, and health investment.',
  },
  {
    title: 'Intermediate Determinants',
    icon: SlidersHorizontal,
    tone: 'blue',
    description: 'System capacity and infrastructure, including water, sanitation, physicians, and electricity.',
  },
  {
    title: 'Proximate Determinants',
    icon: Sparkles,
    tone: 'rose',
    description: 'Direct disease burden and risk factors including communicable disease mortality, HIV, immunisation, and nutrition.',
  },
];
