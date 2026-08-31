// static/js/firebase.server.js
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-analytics.js";
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
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore.js";

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAkkIgBCRYdG_KCnnE4BXh29_BtBlXcUU4",
  authDomain: "facebook-clown-62591.firebaseapp.com",
  projectId: "facebook-clown-62591",
  storageBucket: "facebook-clown-62591.firebasestorage.app",
  messagingSenderId: "467401168801",
  appId: "1:467401168801:web:2153374124dba0dabd1de0",
  measurementId: "G-SGVK1XF7EB"
};

// Initialize Firebase App & Database
const app = initializeApp(firebaseConfig);
const analytics = typeof window !== "undefined" ? getAnalytics(app) : null;
const db = getFirestore(app);

// Firestore collections references
const TASKS_COLLECTION = "tasks";
const SECTIONS_COLLECTION = "sections";

/**
 * Subscribe to real-time updates from Firestore tasks collection
 */
export function subscribeTasks(onUpdateCallback) {
  const tasksRef = collection(db, TASKS_COLLECTION);
  return onSnapshot(tasksRef, (snapshot) => {
    const tasks = [];
    snapshot.forEach((docSnap) => {
      tasks.push({ id: docSnap.id, ...docSnap.data() });
    });
    // Sort tasks by createdAt timestamp descending or title
    tasks.sort((a, b) => (b.createdAt?.seconds || 0) - (a.createdAt?.seconds || 0));
    onUpdateCallback(tasks);
  }, (error) => {
    console.error("Firestore Task Subscription Error:", error);
  });
}

/**
 * Add a new task to Firestore
 */
export async function addTaskToFirebase(taskData) {
  const tasksRef = collection(db, TASKS_COLLECTION);
  const newTaskDoc = {
    title: taskData.title || "",
    assigned_to: taskData.assigned_to || "Unassigned",
    status: taskData.status || "pending",
    section: taskData.section || "General",
    due_date_text: taskData.due_date_text || "",
    due_timestamp: taskData.due_timestamp || "",
    reminder_offset: taskData.reminder_offset || 15,
    reminder_sent: false,
    location_alert: taskData.location_alert || "",
    recurring: taskData.recurring || "",
    labels: Array.isArray(taskData.labels) ? taskData.labels : [],
    subtasks: Array.isArray(taskData.subtasks) ? taskData.subtasks : [],
    createdAt: serverTimestamp()
  };
  const docRef = await addDoc(tasksRef, newTaskDoc);
  return { id: docRef.id, ...newTaskDoc };
}

/**
 * Toggle task status between pending and done
 */
export async function toggleTaskStatusInFirebase(taskId, currentStatus) {
  const taskRef = doc(db, TASKS_COLLECTION, String(taskId));
  const newStatus = currentStatus === "pending" ? "done" : "pending";
  await updateDoc(taskRef, { status: newStatus });
  return newStatus;
}

/**
 * Update general task fields in Firestore
 */
export async function updateTaskInFirebase(taskId, updateData) {
  const taskRef = doc(db, TASKS_COLLECTION, String(taskId));
  await updateDoc(taskRef, updateData);
}

/**
 * Delete a task document from Firestore
 */
export async function deleteTaskFromFirebase(taskId) {
  const taskRef = doc(db, TASKS_COLLECTION, String(taskId));
  await deleteDoc(taskRef);
}

/**
 * Add a subtask to a parent task document
 */
export async function addSubtaskToFirebase(taskId, currentSubtasks, subtaskTitle) {
  const taskRef = doc(db, TASKS_COLLECTION, String(taskId));
  const newSubtask = {
    id: "st_" + Date.now() + "_" + Math.random().toString(36).substr(2, 4),
    title: subtaskTitle.trim(),
    completed: false
  };
  const updatedSubtasks = [...(currentSubtasks || []), newSubtask];
  await updateDoc(taskRef, { subtasks: updatedSubtasks });
  return newSubtask;
}

/**
 * Toggle subtask completed status
 */
export async function toggleSubtaskInFirebase(taskId, currentSubtasks, subtaskId) {
  const taskRef = doc(db, TASKS_COLLECTION, String(taskId));
  const updatedSubtasks = (currentSubtasks || []).map(st => {
    if (st.id === subtaskId) {
      return { ...st, completed: !st.completed };
    }
    return st;
  });
  await updateDoc(taskRef, { subtasks: updatedSubtasks });
}

/**
 * Delete a subtask from a parent task document
 */
export async function deleteSubtaskFromFirebase(taskId, currentSubtasks, subtaskId) {
  const taskRef = doc(db, TASKS_COLLECTION, String(taskId));
  const updatedSubtasks = (currentSubtasks || []).filter(st => st.id !== subtaskId);
  await updateDoc(taskRef, { subtasks: updatedSubtasks });
}

/**
 * Acknowledge reminder sent for a task
 */
export async function acknowledgeReminderInFirebase(taskId) {
  const taskRef = doc(db, TASKS_COLLECTION, String(taskId));
  await updateDoc(taskRef, { reminder_sent: true });
}

export { app, db, analytics };
