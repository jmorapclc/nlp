import React from 'react';
import { Moon, Sun, FileText } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import './Header.css';

const Header = () => {
  const { theme, toggleTheme, isDark } = useTheme();

  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <FileText className="logo-icon" />
          <h1>PDF to Markdown</h1>
        </div>
        
        <button 
          className="theme-toggle"
          onClick={toggleTheme}
          aria-label={`Switch to ${isDark ? 'light' : 'dark'} theme`}
        >
          {isDark ? <Sun className="theme-icon" /> : <Moon className="theme-icon" />}
        </button>
      </div>
    </header>
  );
};

export default Header;
