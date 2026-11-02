import React, { createContext, useContext, useEffect, useState } from 'react';
import {
  onAuthStateChanged,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  sendPasswordResetEmail,
  signOut,
  updateProfile,
} from 'firebase/auth';
import { doc, setDoc, getDoc } from 'firebase/firestore';
import { auth, db } from '../firebase/firebase';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(() => localStorage.getItem('uvvis_token'));

  useEffect(() => {
    // Try Firebase auth first
    let unsubscribe;
    if (auth) {
      try {
        unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
          if (firebaseUser) {
            setUser(firebaseUser);
            const t = await firebaseUser.getIdToken();
            setToken(t);
            localStorage.setItem('uvvis_token', t);
            // Load Firestore profile
            try {
              const snap = await getDoc(doc(db, 'Users', firebaseUser.uid));
              setUserProfile(snap.exists() ? snap.data() : null);
            } catch (_) { setUserProfile(null); }
          } else {
            setUser(null);
            setUserProfile(null);
          }
          setLoading(false);
        });
      } catch (_) {
        setLoading(false);
      }
    } else {
      // Firebase not configured — check for local token
      const localToken = localStorage.getItem('uvvis_token');
      if (localToken) {
        setToken(localToken);
        // user stays null until a page verifies the token
      }
      setLoading(false);
    }
    return () => unsubscribe && unsubscribe();
  }, []);

  // Firebase login
  const loginWithFirebase = async (email, password) => {
    const cred = await signInWithEmailAndPassword(auth, email, password);
    const t = await cred.user.getIdToken();
    setToken(t);
    localStorage.setItem('uvvis_token', t);
    return cred;
  };

  // Local / API login (when Firebase not configured)
  const loginWithAPI = async (email, password) => {
    const { default: api } = await import('../services/api');
    const res = await api.post('/auth/login', { email, password });
    const { uid, token: t, user: u } = res.data;
    setToken(t);
    localStorage.setItem('uvvis_token', t);
    setUserProfile(u);
    // Simulate minimal user object
    setUser({ uid, email, displayName: u.name });
    return res.data;
  };

  const login = async (email, password) => {
    try {
      return await loginWithFirebase(email, password);
    } catch (_) {
      return await loginWithAPI(email, password);
    }
  };

  const register = async (name, orgName, email, password) => {
    const { default: api } = await import('../services/api');
    try {
      // Try Firebase first
      const cred = await createUserWithEmailAndPassword(auth, email, password);
      await updateProfile(cred.user, { displayName: name });
      const t = await cred.user.getIdToken();
      setToken(t);
      localStorage.setItem('uvvis_token', t);
      // Save profile to Firestore
      await setDoc(doc(db, 'Users', cred.user.uid), {
        name, org_name: orgName, email, role: 'User',
        created_at: new Date().toISOString(),
      });
      return cred;
    } catch (_) {
      // Fallback to local API
      const res = await api.post('/auth/register', { name, org_name: orgName, email, password });
      setToken(res.data.token);
      localStorage.setItem('uvvis_token', res.data.token);
      setUserProfile(res.data.user);
      setUser({ uid: res.data.uid, email, displayName: name });
      return res.data;
    }
  };

  const forgotPassword = async (email) => {
    try {
      await sendPasswordResetEmail(auth, email);
    } catch (_) {
      const { default: api } = await import('../services/api');
      await api.post('/auth/forgot-password', { email });
    }
  };

  const logout = async () => {
    try { await signOut(auth); } catch (_) {}
    localStorage.removeItem('uvvis_token');
    setToken(null);
    setUser(null);
    setUserProfile(null);
  };

  const value = { user, userProfile, token, loading, login, register, forgotPassword, logout };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
