import { Menu, X } from 'lucide-react';
import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { appName, navItems } from '../data/nav.js';

export default function AppLayout({ children }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="app-shell">
      <aside className={`sidebar ${open ? 'is-open' : ''}`}>
        <div className="brand">
          <div className="brand-mark">MV</div>
          <div>
            <strong>{appName}</strong>
            <span>Global health intelligence</span>
          </div>
        </div>
        <nav>
          {navItems.map(({ path, label, icon: Icon }) => (
            <NavLink key={path} to={path} onClick={() => setOpen(false)} className={({ isActive }) => (isActive ? 'active' : '')} end={path === '/'}>
              <Icon size={18} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-note">
          <span>World Bank Open Data</span>
          <strong>Ecological mortality analysis</strong>
        </div>
      </aside>
      <button className="mobile-menu" onClick={() => setOpen((value) => !value)} aria-label="Toggle navigation">
        {open ? <X /> : <Menu />}
      </button>
      <div className="content-shell">{children}</div>
    </div>
  );
}
