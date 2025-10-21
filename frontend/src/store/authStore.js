import { create } from 'zustand';
import Cookies from 'js-cookie';
import { jwtDecode } from 'jwt-decode';
import { gql } from '@apollo/client';
import { client } from '../main.jsx';
import { LOGOUT, REFRESH_TOKEN } from '../graphql/mutations'; // Corrected path

export const useAuthStore = create((set) => ({
  user: null,
  token: Cookies.get('access_token') || null,
  login: (token) => {
    Cookies.set('access_token', token, {
      expires: 1 / 24, // 1 hour
      sameSite: 'Lax',
      secure: import.meta.env.VITE_SECURE_COOKIES === 'true',
    });
    const decoded = jwtDecode(token);
    set({ token, user: decoded });
  },
  logout: async () => {
    try {
      await client.mutate({ mutation: LOGOUT });
      Cookies.remove('access_token');
      set({ token: null, user: null });
    } catch (error) {
      console.error('Logout failed:', error);
      Cookies.remove('access_token');
      set({ token: null, user: null });
    }
  },
  refreshToken: async () => {
    try {
      const response = await client.mutate({ mutation: REFRESH_TOKEN });
      const newToken = response.data.refreshToken.accessToken;
      Cookies.set('access_token', newToken, {
        expires: 1 / 24,
        sameSite: 'Lax',
        secure: import.meta.env.VITE_SECURE_COOKIES === 'true',
      });
      const decoded = jwtDecode(newToken);
      set({ token: newToken, user: decoded });
      return newToken;
    } catch (error) {
      console.error('Token refresh failed:', error);
      set({ token: null, user: null });
      throw error;
    }
  },
}));