// firebase.server.js
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import {
  getFirestore,
  collection,
  addDoc,
  getDocs,
  updateDoc,
  deleteDoc,
  doc,
  onSnapshot,
  query,
  orderBy,
  serverTimestamp
} from "firebase/firestore";

// Firebase configuration object
const firebaseConfig = {
  apiKey: "AIzaSyAkkIgBCRYdG_KCnnE4BXh29_BtBlXcUU4",
  authDomain: "facebook-clown-62591.firebaseapp.com",
  projectId: "facebook-clown-62591",
  storageBucket: "facebook-clown-62591.firebasestorage.app",
  messagingSenderId: "467401168801",
  appId: "1:467401168801:web:2153374124dba0dabd1de0",
  measurementId: "G-SGVK1XF7EB"
};

// Initialize Firebase App
const app = initializeApp(firebaseConfig);

// Initialize Analytics (supported in browser environment)
const analytics = typeof window !== "undefined" ? getAnalytics(app) : null;

// Initialize Firestore Database connection
const db = getFirestore(app);

// Export Firebase instance and database connection
export { app, db, analytics };
