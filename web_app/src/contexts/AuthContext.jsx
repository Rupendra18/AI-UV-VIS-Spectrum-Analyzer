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
        import('../services/api').then(({ default: api }) => {
          api.get('/auth/profile').then(res => {
            if (res.data?.user) {
              setUserProfile(res.data.user);
              setUser({ uid: res.data.user.id || 'local', email: res.data.user.email, displayName: res.data.user.name });
            }
          }).catch(() => {
            // invalid or expired token
            localStorage.removeItem('uvvis_token');
            setToken(null);
          }).finally(() => {
            setLoading(false);
          });
        });
        return () => {};
      }
      setLoading(false);
    }
    return () => unsubscribe && unsubscribe();
  }, []);

  // Firebase login
  const loginWithFirebase = async (email, password) => {
    if (!auth) throw new Error('Firebase Auth not available');
    const cred = await signInWithEmailAndPassword(auth, email, password);
    const t = await cred.user.getIdToken();
    setToken(t);
    localStorage.setItem('uvvis_token', t);
    return cred;
  };

  // Local / API login (when Firebase not configured or fails)
  const loginWithAPI = async (email, password) => {
    const { default: api } = await import('../services/api');
    try {
      const res = await api.post('/auth/login', { email, password });
      const { uid, token: t, user: u } = res.data;
      setToken(t || 'token');
      localStorage.setItem('uvvis_token', t || 'token');
      setUserProfile(u);
      setUser({ uid: uid || 'user', email, displayName: u?.name || email.split('@')[0] });
      return res.data;
    } catch (err) {
      if (err.response?.status === 404 || err.response?.status === 405) {
        const res = await api.post('/login', { email, password });
        const { uid, token: t, user: u } = res.data;
        setToken(t || 'token');
        localStorage.setItem('uvvis_token', t || 'token');
        setUserProfile(u);
        setUser({ uid: uid || 'user', email, displayName: u?.name || email.split('@')[0] });
        return res.data;
      }
      throw err;
    }
  };

  const login = async (email, password) => {
    if (auth) {
      try {
        return await loginWithFirebase(email, password);
      } catch (err) {
        // If Firebase rejected because user isn't in Firebase, try local backend API
        try {
          return await loginWithAPI(email, password);
        } catch (apiErr) {
          throw new Error(apiErr.response?.data?.error || err.message || 'Invalid email or password');
        }
      }
    }
    return await loginWithAPI(email, password);
  };

  const register = async (name, orgName, email, password) => {
    const { default: api } = await import('../services/api');
    if (auth) {
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
      } catch (err) {
        // Fallback to local API
        try {
          const res = await api.post('/auth/register', { name, org_name: orgName, email, password });
          setToken(res.data.token);
          localStorage.setItem('uvvis_token', res.data.token);
          setUserProfile(res.data.user);
          setUser({ uid: res.data.uid, email, displayName: name });
          return res.data;
        } catch (apiErr) {
          throw new Error(apiErr.response?.data?.error || err.message || 'Registration failed');
        }
      }
    }
    // Fallback to local API directly
    const res = await api.post('/auth/register', { name, org_name: orgName, email, password });
    setToken(res.data.token);
    localStorage.setItem('uvvis_token', res.data.token);
    setUserProfile(res.data.user);
    setUser({ uid: res.data.uid, email, displayName: name });
    return res.data;
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
