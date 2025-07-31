// src/context/AuthContext.jsx
import { createContext, useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  const setUserFromToken = () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const decoded = jwtDecode(token);
        setUser(decoded.user);
      } catch (err) {
        console.error('Token inválido');
        localStorage.removeItem('token');
        setUser(null);
      }
    }
  };

  useEffect(() => {
    setUserFromToken();
  }, []);

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, logout, setUserFromToken }}>
      {children}
    </AuthContext.Provider>
  );
}
