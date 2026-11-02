import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';
import firebaseConfig from './firebaseConfig';

// Initialize Firebase (gracefully handle placeholder / missing config)
let app = null;
let auth = null;
let db = null;
let storage = null;

try {
  if (firebaseConfig.apiKey && firebaseConfig.apiKey !== 'YOUR_API_KEY') {
    app = initializeApp(firebaseConfig);
    auth = getAuth(app);
    db = getFirestore(app);
    storage = getStorage(app);
  }
} catch (e) {
  console.warn('Firebase not configured — running in local-API-only mode.', e);
}

export { auth, db, storage };
export default app;
