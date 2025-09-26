import React, { useState, useEffect } from 'react';
import './App.css';
import Header from './components/Header';
import Converter from './components/Converter';
import { ThemeProvider } from './contexts/ThemeContext';

function App() {
  return (
    <ThemeProvider>
      <div className="app">
        <Header />
        <main className="main-content">
          <Converter />
        </main>
      </div>
    </ThemeProvider>
  );
}

export default App;
