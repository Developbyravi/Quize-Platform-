"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { fetchApi } from '@/lib/api';

interface UserProfile {
  id: number;
  email: string;
  role: string;
  full_name: string;
}

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  login: (token: string, role: string, fullName: string, userId: number) => void;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  login: () => {},
  logout: () => {},
  isLoading: true,
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedRole = localStorage.getItem('role');
    const storedName = localStorage.getItem('full_name');
    const storedUserId = localStorage.getItem('user_id');

    if (storedToken && storedRole && storedName && storedUserId) {
      setToken(storedToken);
      setUser({
        id: Number(storedUserId),
        email: '',
        role: storedRole,
        full_name: storedName,
      });
    }
    setIsLoading(false);
  }, []);

  const login = (newToken: string, role: string, fullName: string, userId: number) => {
    localStorage.setItem('token', newToken);
    localStorage.setItem('role', role);
    localStorage.setItem('full_name', fullName);
    localStorage.setItem('user_id', userId.toString());

    setToken(newToken);
    setUser({
      id: userId,
      email: '',
      role: role,
      full_name: fullName,
    });

    if (role === 'admin') {
      router.push('/admin');
    } else {
      router.push('/dashboard');
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('full_name');
    localStorage.removeItem('user_id');
    setToken(null);
    setUser(null);
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
